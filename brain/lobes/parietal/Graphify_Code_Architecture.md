# Graphify Code Architecture & Deterministic GraphRAG

O módulo **Graphify** (`engine/code_graph`) constitui o subsistema de inteligência estrutural e extração topológica de código-fonte do ThSyr. Inspirado nos princípios de GraphRAG determinístico, ele dissocia a análise estrutural da estocasticidade de LLMs, operando via árvores de sintaxe abstrata (AST) nativas e parsers gramaticais rígidos.

## 1. Topologia Tri-Linguagem

O grafo é composto por nós (`CodeNode`) e arestas relacionais (`CodeEdge`) fortemente tipados:

1. **Python (AST Nativa)**:
   - Parser: `PythonASTParser` (`ast.parse`)
   - Extração: Módulos, classes, funções síncronas/assíncronas, argumentos, docstrings e cadeias de herança (`bases`).
   - Sinapses: Contenção (`contains`), herança (`inherits`) e chamadas de função (`calls`).

2. **Java (POO Estrutural)**:
   - Parser: `JavaStructuralParser`
   - Extração: Pacotes, classes concretas/abstratas, interfaces e métodos.
   - Sinapses: Herança de classe (`extends` -> `inherits`), contratos de interface (`implements` -> `implements`) e contenção de métodos (`contains`).

3. **SQL (Engenharia Relacional & DDL)**:
   - Parser: `SQLDDLParser` (varredura por contagem de parênteses balanceados)
   - Extração: Tabelas, colunas, tipos de dados, chaves primárias (`PRIMARY KEY`) e integridade referencial.
   - Sinapses: Contenção de colunas (`contains`) e chaves estrangeiras (`references_fk` com metadados de coluna fonte/alvo).

## 2. Métodos Analíticos GraphRAG

A classe `CodeGraphBuilder` e a fachada `GraphifyEngine` oferecem as seguintes primitivas analíticas:

- **Busca Determinística (`find_symbols`)**: Localização exata ou por fragmento de símbolos sem alucinação de nomes.
- **Subgrafo de Vizinhança (`get_neighborhood`)**: Expansão radial em profundidade $N$ ao redor de qualquer nó.
- **Análise de Impacto (`get_impact_analysis`)**: Varredura determinística de dependentes reversos (quem chama este método, quem referencia esta tabela via FK, quem herda desta classe).

## 3. Visualização Holográfica 3D (`visualizer.py`)

- Canvas WebGL gerado via Three.js em `brain/code_canvas_3d.html`.
- Distribuição esférica áurea (Golden Spiral) agrupada por clusters de linguagem:
  - **Python**: Azul ciano elétrico (`#00d4ff`)
  - **Java**: Âmbar dourado (`#ffb52e`)
  - **SQL**: Esmeralda profundo (`#10b981`)
- HUD com busca em tempo real, filtros de linguagem, centralização orbital e inspetor de metadados e arestas.

## 4. Interface CLI (`thsyr graphify`)

- `thsyr graphify status`: Diagnóstico do grafo em cache (`state/code_graph.json`).
- `thsyr graphify build [--paths ...]`: Varredura e indexação de diretórios.
- `thsyr graphify query <simbolo>`: Pesquisa de nós e metadados.
- `thsyr graphify impact <simbolo_ou_id>`: Mapeamento de dependentes reversos.
- `thsyr graphify 3d [--no-open]`: Renderização do canvas holográfico 3D.
