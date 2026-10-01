import json

from engine.models.base import ChatMessage, ModelRequest, ModelResponse, ModelRole, ModelTier, UsageTelemetry
from engine.models.providers.http_provider import GenericHttpProvider
from engine.models.router import ModelRouter
from engine.visual.contracts import VisualArtifactKind, VisualBrief
from engine.visual.critic import VisualCritic
from engine.visual.studio import VisualStudio
from engine.visual.taste_memory import TasteMemory


class FakeVisionGateway:
    def __init__(self, payload):
        self.payload = payload
        self.last_request = None

    def generate(self, request):
        self.last_request = request
        return ModelResponse(
            content=json.dumps(self.payload),
            model_name="fake-vision",
            provider_name="fake",
            telemetry=UsageTelemetry(),
        )


def good_payload():
    return {
        "summary": "Direcao consistente.",
        "scores": {
            "composition": 90,
            "hierarchy": 91,
            "typography": 88,
            "color_contrast": 92,
            "brand_specificity": 89,
            "asset_quality": 90,
            "usability": 90,
            "originality": 87,
        },
        "issues": [],
    }


def test_taste_memory_persists_and_builds_context(tmp_path):
    memory = TasteMemory(tmp_path / "taste.json")
    memory.record("approved", "website", "ref-a", "hero editorial")
    memory.record("rejected", "website", "ref-b", "parece template")

    context = memory.build_context("website")
    assert "ref-a" in context
    assert "hero editorial" in context
    assert "ref-b" in context
    assert "parece template" in context
    assert memory.stats() == {"total": 2, "approved": 1, "rejected": 1}


def test_visual_critic_passes_real_image_reference_to_gateway(tmp_path):
    image = tmp_path / "shot.png"
    image.write_bytes(b"fake-png")
    gateway = FakeVisionGateway(good_payload())
    critic = VisualCritic(gateway=gateway)
    brief = VisualBrief(objective="Site de cafeteria", artifact_kind=VisualArtifactKind.WEBSITE)

    result = critic.critique(image, brief, viewport="desktop")

    assert result.passed is True
    assert result.score >= 85
    assert gateway.last_request.images == [str(image.resolve())]
    assert gateway.last_request.tier.value == "vision"


def test_visual_critic_fails_closed_on_invalid_response(tmp_path):
    image = tmp_path / "shot.png"
    image.write_bytes(b"fake-png")
    gateway = FakeVisionGateway({"unexpected": True})
    critic = VisualCritic(gateway=gateway)
    brief = VisualBrief(objective="Icone premium", artifact_kind=VisualArtifactKind.ICON)

    result = critic.critique(image, brief)

    assert result.passed is False
    assert result.score == 0
    assert result.issues[0].severity.value == "blocker"


def test_prepare_direction_includes_taste_and_quality_process(tmp_path):
    memory = TasteMemory(tmp_path / "taste.json")
    memory.record("rejected", "website", "old-design", "cards genericos")
    studio = VisualStudio(
        critic=VisualCritic(gateway=FakeVisionGateway(good_payload())),
        taste_memory=memory,
    )
    brief = VisualBrief(
        objective="Criar site de uma cafeteria de especialidade",
        artifact_kind=VisualArtifactKind.WEBSITE,
        niche="cafeteria",
    )

    prepared = studio.prepare_direction(brief)
    contract = prepared["generation_contract"]

    assert "old-design" in contract
    assert "cards genericos" in contract
    assert "Renderizar o resultado real" in contract
    assert "score geral >= 85" in contract


def test_model_router_preserves_image_references():
    router = ModelRouter()
    request = router.build_request(
        "Audite esta tela",
        images=["screen.png"],
    )

    assert request.tier == ModelTier.VISION
    assert request.images == ["screen.png"]


def test_http_provider_serializes_local_image_as_multimodal_content(tmp_path):
    image = tmp_path / "screen.png"
    image.write_bytes(b"png-bytes")
    provider = GenericHttpProvider(api_key="test-key", base_url="https://example.invalid/v1")
    request = ModelRequest(
        messages=[ChatMessage(role=ModelRole.USER, content="Analise a imagem.")],
        tier=ModelTier.VISION,
        images=[str(image)],
    )

    payload = provider._build_messages_payload(request)

    assert isinstance(payload[-1]["content"], list)
    assert payload[-1]["content"][0] == {"type": "text", "text": "Analise a imagem."}
    image_part = payload[-1]["content"][1]
    assert image_part["type"] == "image_url"
    assert image_part["image_url"]["url"].startswith("data:image/png;base64,")
