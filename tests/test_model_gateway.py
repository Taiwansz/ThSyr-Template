import shutil
import tempfile
import unittest
from pathlib import Path

from engine.cognitive_router import CognitiveRouter
from engine.models.base import (
    BaseModelProvider,
    ChatMessage,
    ModelRequest,
    ModelResponse,
    ModelRole,
    ModelTier,
)
from engine.models.gateway import ModelGateway
from engine.models.providers.mock import MockProvider
from engine.models.router import ModelRouter


class FailingProvider(BaseModelProvider):
    provider_name: str = "failing_mock"

    def supports_tier(self, tier: ModelTier) -> bool:
        return True

    def generate(self, request: ModelRequest) -> ModelResponse:
        raise ConnectionError("Falha de rede simulada para testar fallback.")

    def stream(self, request: ModelRequest):
        raise ConnectionError("Falha de stream simulada.")

    def embed(self, texts):
        raise ConnectionError("Falha de embedding simulada.")


class TestModelGateway(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.telemetry_file = self.temp_dir / "test_telemetry.json"
        self.router = ModelRouter()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_model_router_classification(self):
        # 1. Pergunta simples -> FAST
        tier_simple = self.router.classify_task("Qual e o status do sistema?")
        self.assertEqual(tier_simple, ModelTier.FAST)

        # 2. Pergunta de arquitetura complexa -> REASONING
        tier_reasoning = self.router.classify_task("Planeje a arquitetura do banco de dados e resolva a concorrencia")
        self.assertEqual(tier_reasoning, ModelTier.REASONING)

        # 3. Código markdown longo -> REASONING
        code_query = "Avalie este script:\n```python\nfor i in range(10):\n    print(i)\n```"
        self.assertEqual(self.router.classify_task(code_query), ModelTier.REASONING)

        # 4. Imagem / visão -> VISION
        tier_vision = self.router.classify_task("Analise este screenshot da interface", has_images=True)
        self.assertEqual(tier_vision, ModelTier.VISION)

    def test_mock_provider_generation_and_telemetry(self):
        provider = MockProvider(latency_ms=10.0)
        req = ModelRequest(
            messages=[ChatMessage(role=ModelRole.USER, content="Qual servidor foi configurado?")],
            tier=ModelTier.FAST
        )
        resp = provider.generate(req)
        self.assertIn("Dell PowerEdge", resp.content)
        self.assertEqual(resp.provider_name, "mock")
        self.assertGreater(resp.telemetry.total_tokens, 0)
        self.assertGreater(resp.telemetry.latency_ms, 0.0)

    def test_mock_provider_stream_and_embed(self):
        provider = MockProvider()
        req = ModelRequest(
            messages=[ChatMessage(role=ModelRole.USER, content="Ola Syr")],
            tier=ModelTier.FAST
        )
        chunks = list(provider.stream(req))
        self.assertTrue(len(chunks) > 0)
        full_text = "".join(c.delta for c in chunks)
        self.assertIn("ThSyr", full_text)

        embeddings = provider.embed(["texto para teste"])
        self.assertEqual(len(embeddings), 1)
        self.assertEqual(len(embeddings[0]), 8)

    def test_gateway_fallback_mechanism(self):
        failing = FailingProvider()
        mock = MockProvider(default_response="Resposta via Fallback com sucesso.")

        gateway = ModelGateway(
            providers=[failing, mock],
            telemetry_file=self.telemetry_file
        )

        req = ModelRequest(
            messages=[ChatMessage(role=ModelRole.USER, content="Teste de fallback")],
            tier=ModelTier.FAST
        )

        resp = gateway.generate(req)
        self.assertEqual(resp.content, "Resposta via Fallback com sucesso.")
        self.assertEqual(resp.provider_name, "mock")

        # Telemetria deve ter registrado 1 fallback
        t = gateway.get_telemetry_summary()
        self.assertEqual(t["total_requests"], 1)
        self.assertEqual(t["fallback_count"], 1)
        self.assertTrue(self.telemetry_file.exists())

    def test_cognitive_router_think_and_generate(self):
        cr = CognitiveRouter()
        res = cr.think_and_generate("Qual servidor foi configurado?")
        self.assertIn("Dell PowerEdge", res["response"])
        self.assertEqual(res["audit"]["status"], "APPROVED")
        self.assertIn("telemetry", res)
        self.assertGreater(res["telemetry"]["total_tokens"], 0)


if __name__ == "__main__":
    unittest.main()
