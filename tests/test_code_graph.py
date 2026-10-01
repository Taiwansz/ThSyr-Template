"""
Testes unitarios para o motor Graphify & Code Graph Architecture.
Valida os parsers de Python, Java e SQL, o grafo unificado, consultas GraphRAG e o renderizador 3D.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from engine.code_graph.builder import CodeGraphBuilder
from engine.code_graph.java_parser import JavaStructuralParser
from engine.code_graph.models import (
    CodeEdge,
    CodeGraph,
    CodeNode,
    CodeRelationshipType,
    CodeSymbolType,
)
from engine.code_graph.python_parser import PythonASTParser
from engine.code_graph.sql_parser import SQLDDLParser
from engine.code_graph.visualizer import render_code_graph_3d


class TestCodeGraphModels(unittest.TestCase):
    def test_node_and_edge_serialization(self):
        node = CodeNode(
            id="py:class:TestClass",
            name="TestClass",
            symbol_type=CodeSymbolType.CLASS,
            language="python",
            filepath="test.py",
            line_number=10,
            docstring="Classe de teste",
        )
        edge = CodeEdge(
            source_id="py:class:TestClass",
            target_id="py:class:BaseClass",
            rel_type=CodeRelationshipType.INHERITS,
        )

        n_dict = node.to_dict()
        e_dict = edge.to_dict()

        self.assertEqual(n_dict["symbol_type"], "class")
        self.assertEqual(e_dict["rel_type"], "inherits")

    def test_graph_summary_and_helpers(self):
        g = CodeGraph()
        n1 = CodeNode(id="n1", name="foo", symbol_type=CodeSymbolType.FUNCTION, language="python", filepath="a.py")
        n2 = CodeNode(id="n2", name="bar", symbol_type=CodeSymbolType.FUNCTION, language="python", filepath="a.py")
        g.add_node(n1)
        g.add_node(n2)
        g.add_edge(CodeEdge(source_id="n1", target_id="n2", rel_type=CodeRelationshipType.CALLS))

        summary = g.summary()
        self.assertEqual(summary["total_nodes"], 2)
        self.assertEqual(summary["total_edges"], 1)
        self.assertEqual(g.get_callees("n1"), ["n2"])
        self.assertEqual(g.get_callers("n2"), ["n1"])


class TestPythonASTParser(unittest.TestCase):
    def setUp(self):
        self.parser = PythonASTParser()
        self.graph = CodeGraph()

    def test_parse_python_code(self):
        code = '''
"""Doc do modulo."""

class Animal:
    pass

class Dog(Animal):
    """Doc da classe Dog."""
    def bark(self, volume: int):
        print("woof")

def standalone_func():
    d = Dog()
    d.bark(10)
'''
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(code)
            tmp_path = Path(f.name)

        try:
            self.parser.parse_file(tmp_path, self.graph)
            # Modulo, Animal, Dog, bark, standalone_func
            self.assertIn(f"py:mod:{tmp_path.stem}", self.graph.nodes)
            dog_id = f"py:class:{tmp_path.stem}.Dog"
            self.assertIn(dog_id, self.graph.nodes)
            dog_node = self.graph.nodes[dog_id]
            self.assertEqual(dog_node.metadata["bases"], ["Animal"])

            # Verificar aresta de heranca
            inherits = [e for e in self.graph.edges if e.rel_type == CodeRelationshipType.INHERITS]
            self.assertTrue(len(inherits) >= 1)
            self.assertEqual(inherits[0].source_id, dog_id)

            # Metodo bark
            bark_id = f"py:method:{tmp_path.stem}.bark"
            self.assertIn(bark_id, self.graph.nodes)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


class TestJavaStructuralParser(unittest.TestCase):
    def setUp(self):
        self.parser = JavaStructuralParser()
        self.graph = CodeGraph()

    def test_parse_java_code(self):
        code = """
package com.thsyr.core;

import java.util.List;

public class TaskManager extends BaseManager implements ITaskProcessor {
    public void executeTask(String id, int priority) {
        System.out.println("Processing");
    }

    private boolean validate() {
        return true;
    }
}
"""
        with tempfile.NamedTemporaryFile("w", suffix=".java", delete=False, encoding="utf-8") as f:
            f.write(code)
            tmp_path = Path(f.name)

        try:
            self.parser.parse_file(tmp_path, self.graph)
            class_id = "java:class:com.thsyr.core.TaskManager"
            self.assertIn(class_id, self.graph.nodes)
            node = self.graph.nodes[class_id]
            self.assertEqual(node.metadata["extends"], "BaseManager")
            self.assertIn("ITaskProcessor", node.metadata["implements"])

            # Aresta de heranca e implementacao
            extends_edges = [e for e in self.graph.edges if e.rel_type == CodeRelationshipType.INHERITS]
            implements_edges = [e for e in self.graph.edges if e.rel_type == CodeRelationshipType.IMPLEMENTS]
            self.assertEqual(len(extends_edges), 1)
            self.assertEqual(len(implements_edges), 1)

            # Metodos
            self.assertIn("java:method:TaskManager.executeTask", self.graph.nodes)
            self.assertIn("java:method:TaskManager.validate", self.graph.nodes)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


class TestSQLDDLParser(unittest.TestCase):
    def setUp(self):
        self.parser = SQLDDLParser()
        self.graph = CodeGraph()

    def test_parse_sql_ddl_and_foreign_keys(self):
        ddl = """
CREATE DATABASE IF NOT EXISTS shop;
USE shop;

CREATE TABLE customers (
    id_customer VARCHAR(36) DEFAULT (UUID()) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE
);

CREATE TABLE orders (
    id_order VARCHAR(36) PRIMARY KEY,
    id_customer VARCHAR(36),
    amount DECIMAL(10, 2) NOT NULL,
    CONSTRAINT fk_customer FOREIGN KEY (id_customer) REFERENCES customers(id_customer)
);
"""
        with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
            f.write(ddl)
            tmp_path = Path(f.name)

        try:
            self.parser.parse_file(tmp_path, self.graph)

            # Tabelas
            self.assertIn("sql:table:customers", self.graph.nodes)
            self.assertIn("sql:table:orders", self.graph.nodes)

            # Colunas de customers
            self.assertIn("sql:col:customers.id_customer", self.graph.nodes)
            self.assertIn("sql:col:customers.name", self.graph.nodes)
            self.assertIn("sql:col:customers.email", self.graph.nodes)

            # Chave estrangeira de orders -> customers
            fks = [e for e in self.graph.edges if e.rel_type == CodeRelationshipType.REFERENCES_FK]
            self.assertEqual(len(fks), 1)
            self.assertEqual(fks[0].source_id, "sql:table:orders")
            self.assertEqual(fks[0].target_id, "sql:table:customers")
            self.assertEqual(fks[0].metadata["source_column"], "id_customer")
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


class TestCodeGraphBuilderAndGraphRAG(unittest.TestCase):
    def setUp(self):
        self.builder = CodeGraphBuilder()

    def test_build_and_graphrag_queries(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            dir_path = Path(tmp_dir)

            py_file = dir_path / "service.py"
            py_file.write_text("""
class PaymentService:
    def process_payment(self, order_id):
        pass
""", encoding="utf-8")

            sql_file = dir_path / "schema.sql"
            sql_file.write_text("""
CREATE TABLE payments (
    id VARCHAR(36) PRIMARY KEY,
    status VARCHAR(50)
);
""", encoding="utf-8")

            graph = self.builder.build_from_paths([dir_path])
            self.assertTrue(len(graph.nodes) >= 3)

            # Busca por simbolo
            symbols = self.builder.find_symbols("Payment")
            self.assertTrue(len(symbols) >= 1)

            # Subgrafo de vizinhanca
            neighborhood = self.builder.get_neighborhood(symbols[0].id, depth=1)
            self.assertEqual(neighborhood["root_id"], symbols[0].id)
            self.assertTrue(len(neighborhood["nodes"]) >= 1)

            # Analise de impacto
            impact = self.builder.get_impact_analysis(symbols[0].id)
            self.assertIn("direct_callers", impact)
            self.assertIn("total_dependents", impact)

            # Exportacao e Importacao de JSON
            json_path = dir_path / "graph.json"
            self.builder.export_json(json_path)
            self.assertTrue(json_path.exists())

            new_builder = CodeGraphBuilder()
            reloaded_graph = new_builder.import_json(json_path)
            self.assertEqual(len(reloaded_graph.nodes), len(graph.nodes))
            self.assertEqual(len(reloaded_graph.edges), len(graph.edges))

    def test_3d_renderer(self):
        g = CodeGraph()
        g.add_node(CodeNode(id="p1", name="Mod1", symbol_type=CodeSymbolType.MODULE, language="python", filepath="m.py"))
        g.add_node(CodeNode(id="j1", name="Class1", symbol_type=CodeSymbolType.CLASS, language="java", filepath="C.java"))
        g.add_node(CodeNode(id="s1", name="table1", symbol_type=CodeSymbolType.TABLE, language="sql", filepath="t.sql"))
        g.add_edge(CodeEdge(source_id="p1", target_id="j1", rel_type=CodeRelationshipType.CALLS))

        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
            tmp_out = Path(f.name)

        try:
            render_code_graph_3d(g, output_path=tmp_out, open_browser=False)
            self.assertTrue(tmp_out.exists())
            html = tmp_out.read_text(encoding="utf-8")
            self.assertIn("GRAPHIFY CORE 3D", html)
            self.assertIn("Mod1", html)
            self.assertIn("Class1", html)
            self.assertIn("table1", html)
        finally:
            if tmp_out.exists():
                tmp_out.unlink()


if __name__ == "__main__":
    unittest.main()
