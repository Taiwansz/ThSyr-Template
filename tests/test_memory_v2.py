import shutil
import tempfile
import unittest
from pathlib import Path

from engine.memory_manager import MemoryManager
from engine.memory_models import MemoryMetadata, MemoryType, dump_yaml_frontmatter, parse_yaml_frontmatter
from engine.procedural_memory import ProceduralMemoryManager
from engine.working_memory import WorkingMemory


class TestMemoryV2(unittest.TestCase):
    def setUp(self):
        self.temp_brain = Path(tempfile.mkdtemp())
        self.temp_state = Path(tempfile.mkdtemp())
        self.manager = MemoryManager(root=self.temp_brain, state_dir=self.temp_state)

    def tearDown(self):
        shutil.rmtree(self.temp_brain, ignore_errors=True)
        shutil.rmtree(self.temp_state, ignore_errors=True)

    def test_yaml_frontmatter_roundtrip(self):
        meta = MemoryMetadata(
            id="test_meta_01",
            type=MemoryType.PROCEDURAL.value,
            source="manual_test",
            confidence=0.95,
            importance=0.88,
            entities=["Operador", "Agente"],
            projects=["Copilot", "Projeto_Alpha"],
            tags=["core", "testing"]
        )
        rendered = dump_yaml_frontmatter(meta)
        self.assertTrue(rendered.startswith("---"))
        self.assertTrue(rendered.endswith("---"))

        parsed_dict, body = parse_yaml_frontmatter(f"{rendered}\n\n# Titulo\nConteudo aqui.")
        self.assertEqual(parsed_dict["id"], "test_meta_01")
        self.assertEqual(parsed_dict["type"], "procedural")
        self.assertEqual(float(parsed_dict["importance"]), 0.88)
        self.assertIn("Operador", parsed_dict["entities"])
        self.assertIn("Projeto_Alpha", parsed_dict["projects"])
        self.assertIn("# Titulo", body)

    def test_working_memory_lifecycle(self):
        wm = WorkingMemory(state_dir=self.temp_state)
        wm.update_focus("Refatorar persistencia de memoria", project="Copilot", entities=["Operador"])
        wm.append_scratchpad("Anotacao temporaria 1")
        wm.set_variable("step_count", 4)
        wm.set_constraints(["Nao quebrar testes existentes"])

        # Carregar em nova instancia para verificar persistencia
        wm2 = WorkingMemory(state_dir=self.temp_state)
        self.assertEqual(wm2.focus, "Refatorar persistencia de memoria")
        self.assertEqual(wm2.project, "Copilot")
        self.assertIn("Anotacao temporaria 1", wm2.scratchpad)
        self.assertEqual(wm2.get_variable("step_count"), 4)

        # Converter para MemoryItem
        item = wm2.to_memory_item()
        self.assertEqual(item.metadata.type, MemoryType.WORKING.value)
        self.assertIn("Anotacao temporaria 1", item.content)

    def test_procedural_memory_manager(self):
        proc_mgr = ProceduralMemoryManager(brain_dir=self.temp_brain)
        p_path = proc_mgr.save_procedure(
            name="deploy_pipeline",
            title="Procedimento de Deploy Continuo",
            content="Passo 1: Rodar testes.\nPasso 2: Git push.",
            projects=["ThSyr"],
            tags=["deploy", "ci"]
        )
        self.assertTrue(p_path.exists())

        loaded = proc_mgr.get_procedure("deploy_pipeline")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.title, "Procedimento de Deploy Continuo")
        self.assertEqual(loaded.metadata.type, MemoryType.PROCEDURAL.value)

        # Busca por palavra-chave
        searched = proc_mgr.search_procedures("deploy")
        self.assertEqual(len(searched), 1)

    def test_unified_query_interface(self):
        # 1. Criar memórias em diferentes categorias
        self.manager.update_working_focus("Validar busca unificada", project="Atlas", entities=["Operador"])

        self.manager.save_procedure(
            name="auth_flow",
            title="Fluxo de Autenticacao Supabase",
            content="Como configurar RLS em tabelas multi-tenant.",
            projects=["Atlas", "Projeto_Alpha"],
            entities=["Operador"],
            tags=["auth", "supabase"],
            importance=0.9
        )

        self.manager.save_semantic_memory(
            name="atlas_stack",
            title="Stack do Projeto Atlas",
            content="Next.js 15, Supabase, Tailwind.",
            projects=["Atlas"],
            entities=["Operador"],
            tags=["stack"],
            importance=0.8
        )

        self.manager.append_episodic_log(
            title="Reuniao Atlas",
            content="Discutida a estrutura de dados.",
            projects=["Atlas"],
            entities=["Colaborador"],
            tags=["meeting"],
            importance=0.5
        )

        self.manager.save_analytical_memory(
            title="Deducao Estrategica Atlas",
            content="O projeto Atlas requer isolamento de contexto.",
            projects=["Atlas"],
            entities=["Operador"],
            tags=["estrategia"],
            importance=0.92
        )

        # Consulta 1: Por projeto Atlas
        res_atlas = self.manager.query(project="Atlas")
        self.assertGreaterEqual(len(res_atlas), 4)

        # Consulta 2: Por tipo Procedural
        res_proc = self.manager.query(memory_type=MemoryType.PROCEDURAL)
        self.assertEqual(len(res_proc), 1)
        self.assertEqual(res_proc[0].title, "Fluxo de Autenticacao Supabase")

        # Consulta 2.1: Por tipo Analytical
        res_ana = self.manager.query(memory_type=MemoryType.ANALYTICAL)
        self.assertEqual(len(res_ana), 1)
        self.assertEqual(res_ana[0].title, "Deducao Estrategica Atlas")

        # Consulta 3: Por entidade Colaborador
        res_colab = self.manager.query(entity="Colaborador")
        self.assertEqual(len(res_colab), 1)
        self.assertEqual(res_colab[0].metadata.type, MemoryType.EPISODIC.value)

        # Consulta 4: Por importancia minima
        res_imp = self.manager.query(min_importance=0.85)
        self.assertTrue(all(item.metadata.importance >= 0.85 for item in res_imp))

    def test_compact_context_includes_procedures_and_working(self):
        self.manager.update_working_focus("Testar contexto compacto", project="ThSyr")
        self.manager.save_procedure(
            name="code_guideline",
            title="Diretrizes de Codigo",
            content="Regras estritas de tipagem.",
            importance=0.9
        )

        ctx = self.manager.build_compact_context(include_procedures=True, include_working=True)
        self.assertIn("MEMÓRIA DE TRABALHO", ctx)
        self.assertIn("Testar contexto compacto", ctx)
        self.assertIn("PROCEDIMENTOS RELEVANTES", ctx)
        self.assertIn("Diretrizes de Codigo", ctx)


if __name__ == "__main__":
    unittest.main()
