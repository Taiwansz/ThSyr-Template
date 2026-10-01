"""
ThSyr Test Suite - Tool Bus & Permission Cortex (Fase 5 e Fase 6)
Valida:
- Contratos tipados e schemas de ferramentas
- Avaliacao de riscos e governanca do Permission Cortex
- Execucao de adapters (filesystem, git, shell, memory)
- Bloqueio de comandos destrutivos
- Emissao de eventos de auditoria
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from engine.tools.adapters.shell import ShellCommandTool
from engine.tools.base import RiskLevel, ToolMetadata
from engine.tools.bus import ToolBus
from engine.tools.permission import PermissionCortex, PermissionDecision


class TestToolBus(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.state_dir = self.temp_dir / "state"
        self.permission_cortex = PermissionCortex()
        self.tool_bus = ToolBus(
            permission_cortex=self.permission_cortex,
            state_dir=self.state_dir,
            register_defaults=True
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_permission_cortex_risk_levels(self):
        cortex = PermissionCortex(max_autonomous_risk=RiskLevel.LEVEL_2_CREATE_LOCAL)

        # Nivel 0: Automatico
        meta_0 = ToolMetadata("t0", "desc", {}, {}, risk_level=RiskLevel.LEVEL_0_SEARCH)
        dec_0, _ = cortex.evaluate(meta_0, {})
        self.assertEqual(dec_0, PermissionDecision.ALLOW)

        # Nivel 1: Automatico
        meta_1 = ToolMetadata("t1", "desc", {}, {}, risk_level=RiskLevel.LEVEL_1_READ)
        dec_1, _ = cortex.evaluate(meta_1, {})
        self.assertEqual(dec_1, PermissionDecision.ALLOW)

        # Nivel 3: Acima do limiar (2) -> requer confirmacao
        meta_3 = ToolMetadata("t3", "desc", {}, {}, risk_level=RiskLevel.LEVEL_3_EDIT_PROJECT)
        dec_3, _ = cortex.evaluate(meta_3, {})
        self.assertEqual(dec_3, PermissionDecision.REQUIRE_CONFIRMATION)

        # Nivel 6: Critico -> Negado
        meta_6 = ToolMetadata("t6", "desc", {}, {}, risk_level=RiskLevel.LEVEL_6_CRITICAL)
        dec_6, _ = cortex.evaluate(meta_6, {})
        self.assertEqual(dec_6, PermissionDecision.DENY)

    def test_filesystem_tools(self):
        # 1. Escrever arquivo de teste
        test_file = self.temp_dir / "sample.txt"
        res_write = self.tool_bus.execute("write_file", path=str(test_file), content="Conteudo de teste ThSyr")
        self.assertTrue(res_write.success)
        self.assertTrue(test_file.exists())

        # 2. Ler arquivo de teste
        res_read = self.tool_bus.execute("read_file", path=str(test_file))
        self.assertTrue(res_read.success)
        self.assertIn("Conteudo de teste ThSyr", res_read.raw_output)

        # 3. Listar diretorio
        res_list = self.tool_bus.execute("list_dir", path=str(self.temp_dir))
        self.assertTrue(res_list.success)
        self.assertIn("sample.txt", res_list.raw_output)

    def test_shell_tool_safety(self):
        res_safe = self.tool_bus.execute("shell_command", command="echo 'Jarvis runtime ativo'")
        self.assertFalse(res_safe.success)
        # Note que shell_command e Risco 3; com max_autonomous_risk=2 precisa de confirmacao
        # Vamos testar com cortex que autoriza ou avaliando diretamente o adapter:
        shell_adapter = ShellCommandTool()
        res_echo = shell_adapter.run(command="echo 'Jarvis runtime ativo'")
        self.assertTrue(res_echo.success)
        self.assertIn("Jarvis runtime ativo", res_echo.raw_output)

        # 2. Comando destrutivo bloqueado
        res_dang = shell_adapter.run(command="rm -rf /")
        self.assertFalse(res_dang.success)
        self.assertIn("bloqueado", res_dang.raw_output)

    def test_memory_tools(self):
        res_search = self.tool_bus.execute("search_memory", query="TokLang", limit=2)
        self.assertTrue(res_search.success)
        self.assertIn("items", res_search.data)

    def test_git_tools(self):
        res_status = self.tool_bus.execute("git_status")
        self.assertTrue(res_status.success)

        res_log = self.tool_bus.execute("git_log", count=2)
        self.assertTrue(res_log.success)
        self.assertGreater(len(res_log.data.get("commits", [])), 0)

    def test_audit_event_emission(self):
        test_file = self.temp_dir / "audit_test.txt"
        self.tool_bus.execute("write_file", path=str(test_file), content="Auditoria")

        events = list((self.state_dir / "events").glob("*.json"))
        self.assertGreater(len(events), 0)


if __name__ == "__main__":
    unittest.main()
