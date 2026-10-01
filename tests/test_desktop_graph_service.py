"""
Testes unitarios para o DesktopGraphService.
Valida snapshot 3D, coordenadas deterministicas e mapeamento de pulsos neurais.
"""

import math

from engine.desktop.graph_service import DesktopGraphService


def test_graph_service_build_snapshot():
    service = DesktopGraphService()
    snapshot = service.build_snapshot()

    assert snapshot.version == 1
    assert snapshot.total_nodes > 0
    assert snapshot.total_edges > 0
    assert len(snapshot.nodes) == snapshot.total_nodes

    # Validar coordenadas e integridade numerica dos primeiros nós
    for node in snapshot.nodes[:50]:
        assert isinstance(node.x, float)
        assert isinstance(node.y, float)
        assert isinstance(node.z, float)
        assert not math.isnan(node.x) and not math.isinf(node.x)
        assert not math.isnan(node.y) and not math.isinf(node.y)
        assert not math.isnan(node.z) and not math.isinf(node.z)
        assert node.group != ""
        assert node.color.startswith("#")


def test_graph_service_deterministic_coordinates():
    service = DesktopGraphService()
    snap1 = service.build_snapshot(force_refresh=True)
    snap2 = service.build_snapshot(force_refresh=True)

    assert snap1.total_nodes == snap2.total_nodes
    assert snap1.total_edges == snap2.total_edges

    for n1, n2 in zip(snap1.nodes[:20], snap2.nodes[:20]):
        assert n1.id == n2.id
        assert n1.x == n2.x
        assert n1.y == n2.y
        assert n1.z == n2.z


def test_graph_service_match_pulse_nodes():
    service = DesktopGraphService()
    snapshot = service.build_snapshot()
    existing_id = snapshot.nodes[0].id if snapshot.nodes else "node_0"

    fake_pulse = {
        "id": "pulse_test_1",
        "seeds": [existing_id, "NonExistentSeed123"],
        "top_activated": [
            {"id": existing_id, "energy": 0.95, "lobe": "frontal"},
            {"id": "NonExistentNode456", "energy": 0.5, "lobe": "parietal"}
        ],
        "constraints": ["Regra_1"],
        "retrieved": [{"id": "mem_1", "title": "Memoria 1"}],
    }

    matched = service.match_pulse_nodes(fake_pulse)
    assert existing_id in matched["matched_seeds"]
    assert "NonExistentSeed123" in matched["unmatched_seeds"]
    assert any(item["id"] == existing_id for item in matched["matched_activated"])
    assert "NonExistentNode456" in matched["unmatched_activated"]
    assert matched["retrieved_count"] == 1
