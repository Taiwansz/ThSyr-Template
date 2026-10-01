"""
Testes unitarios para o AgyCliProvider e integracao com ModelGateway.
Garante execucao deterministica, parsing de saida, gestao de falhas e mapeamento de tiers.
"""

import json
import subprocess
import unittest
from unittest.mock import MagicMock, patch

from engine.models.base import ChatMessage, ModelRequest, ModelRole, ModelTier
from engine.models.gateway import ModelGateway
from engine.models.providers.agy_provider import (
    AgyCliProvider,
    find_agy_binary,
    has_windows_gemini_credential,
)


class TestAgyCliProvider(unittest.TestCase):
    def test_detection_functions_do_not_crash(self):
        binary = find_agy_binary()
        self.assertTrue(binary is None or isinstance(binary, str))
        has_cred = has_windows_gemini_credential()
        self.assertIsInstance(has_cred, bool)

    def test_tier_resolution(self):
        prov = AgyCliProvider(binary_path="dummy_agy.exe")

        req_fast = ModelRequest(messages=[], tier=ModelTier.FAST)
        self.assertEqual(prov._resolve_model(req_fast), "gemini-3.7-flash-low")

        req_reasoning = ModelRequest(messages=[], tier=ModelTier.REASONING)
        self.assertEqual(prov._resolve_model(req_reasoning), "gemini-3.8-flash-high")

        req_explicit = ModelRequest(messages=[], tier=ModelTier.FAST, model_name="custom-model")
        self.assertEqual(prov._resolve_model(req_explicit), "custom-model")

    def test_prompt_formatting(self):
        prov = AgyCliProvider(binary_path="dummy_agy.exe")
        req = ModelRequest(
            messages=[
                ChatMessage(role=ModelRole.SYSTEM, content="Diretriz Ultron ativa"),
                ChatMessage(role=ModelRole.USER, content="Status da operacao?"),
            ],
            tier=ModelTier.FAST,
        )
        prompt = prov._build_prompt_text(req)
        self.assertIn("[DIRETRIZES DE SISTEMA - THSYR SAGITAL]", prompt)
        self.assertIn("Diretriz Ultron ativa", prompt)
        self.assertIn("[SOLICITACAO DO OPERADOR]", prompt)
        self.assertIn("Status da operacao?", prompt)

    @patch("engine.models.providers.agy_provider.AgyCliProvider.is_available", return_value=True)
    @patch("subprocess.Popen")
    def test_generate_success(self, mock_popen, mock_avail):
        fake_response_data = {
            "conversation_id": "test-conv-id",
            "status": "SUCCESS",
            "response": "Resposta do modelo Gemini atraves do Antigravity CLI.",
            "duration_seconds": 1.45,
            "usage": {
                "input_tokens": 120,
                "output_tokens": 45,
                "total_tokens": 165,
            },
        }
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.communicate.return_value = (json.dumps(fake_response_data), "")
        mock_popen.return_value = mock_proc

        prov = AgyCliProvider(binary_path="fake_agy.exe")
        req = ModelRequest(
            messages=[ChatMessage(role=ModelRole.USER, content="Teste de geracao")],
            tier=ModelTier.FAST,
        )

        resp = prov.generate(req)
        self.assertEqual(resp.content, "Resposta do modelo Gemini atraves do Antigravity CLI.")
        self.assertEqual(resp.model_name, "gemini-3.7-flash-low")
        self.assertEqual(resp.provider_name, "antigravity_cli")
        self.assertEqual(resp.telemetry.total_tokens, 165)
        self.assertGreaterEqual(resp.telemetry.latency_ms, 0)
        self.assertEqual(resp.telemetry.estimated_cost_usd, 0.0)

    @patch("engine.models.providers.agy_provider.AgyCliProvider.is_available", return_value=True)
    @patch("subprocess.Popen")
    def test_generate_process_failure(self, mock_popen, mock_avail):
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.communicate.return_value = ("", "Erro fatal no executavel agy")
        mock_popen.return_value = mock_proc

        prov = AgyCliProvider(binary_path="fake_agy.exe")
        req = ModelRequest(messages=[], tier=ModelTier.FAST)

        with self.assertRaises(RuntimeError) as ctx:
            prov.generate(req)
        self.assertIn("Erro fatal no executavel agy", str(ctx.exception))

    @patch("engine.models.providers.agy_provider.AgyCliProvider.is_available", return_value=True)
    @patch("subprocess.Popen")
    def test_generate_timeout(self, mock_popen, mock_avail):
        mock_proc = MagicMock()
        mock_proc.communicate.side_effect = subprocess.TimeoutExpired(cmd="agy", timeout=5)
        mock_popen.return_value = mock_proc

        prov = AgyCliProvider(binary_path="fake_agy.exe", timeout_seconds=5)
        req = ModelRequest(messages=[], tier=ModelTier.FAST)

        with self.assertRaises(TimeoutError):
            prov.generate(req)
        mock_proc.kill.assert_called_once()

    @patch("engine.models.providers.agy_provider.AgyCliProvider.is_available", return_value=True)
    @patch("subprocess.Popen")
    def test_stream_chunks(self, mock_popen, mock_avail):
        fake_response_data = {
            "response": "Paragrafo 1.\n\nParagrafo 2.",
            "usage": {"total_tokens": 10},
        }
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.communicate.return_value = (json.dumps(fake_response_data), "")
        mock_popen.return_value = mock_proc

        prov = AgyCliProvider(binary_path="fake_agy.exe")
        req = ModelRequest(messages=[], tier=ModelTier.FAST)

        chunks = list(prov.stream(req))
        self.assertEqual(len(chunks), 2)
        full_text = "".join(c.delta for c in chunks)
        self.assertEqual(full_text, "Paragrafo 1.\n\nParagrafo 2.")

    def test_embed_fallback(self):
        prov = AgyCliProvider(binary_path="fake_agy.exe")
        embs = prov.embed(["teste de vetorizacao"])
        self.assertEqual(len(embs), 1)
        self.assertEqual(len(embs[0]), 8)


if __name__ == "__main__":
    unittest.main()
