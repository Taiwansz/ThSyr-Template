"""
ThSyr Cognitive Router - Roteador Neurocognitivo V2
Orquestra ativação sináptica propagada, auditoria do córtex pré-frontal,
injeção de contexto compacto e verificação de integridade operacional.
"""

from typing import Any

from .identity_verifier import OperatorIdentityVerifier
from .memory_manager import MemoryManager
from .models import ModelGateway, ModelRouter
from .neural_pulse import record_neural_pulse
from .operator_intelligence import OperatorIntelligence
from .personalization.hub import PersonalizationHub
from .prefrontal_cortex import PreFrontalCortex
from .retriever import MemoryRetriever
from .self_model import OperationalSelfModel
from .session_state import HandoffManager
from .synaptic_engine import SynapticEngine


class CognitiveRouter:
    def __init__(
        self,
        memory: MemoryManager | None = None,
        synaptic: SynapticEngine | None = None,
        prefrontal: PreFrontalCortex | None = None,
        handoff: HandoffManager | None = None,
        retriever: MemoryRetriever | None = None,
        model_gateway: ModelGateway | None = None,
        model_router: ModelRouter | None = None,
        identity_verifier: OperatorIdentityVerifier | None = None,
        operator_intelligence: OperatorIntelligence | None = None,
        personalization: PersonalizationHub | None = None,
    ):
        self.memory = memory or MemoryManager()
        self.synaptic = synaptic or SynapticEngine()
        self.prefrontal = prefrontal or PreFrontalCortex()
        self.handoff = handoff or HandoffManager()
        self.retriever = retriever or MemoryRetriever(
            memory_manager=self.memory,
            synaptic_engine=self.synaptic
        )
        self.model_gateway = model_gateway or ModelGateway()
        self.model_router = model_router or ModelRouter()
        self.identity_verifier = identity_verifier or OperatorIdentityVerifier()
        self.personalization = personalization or PersonalizationHub(
            operator_intelligence=operator_intelligence or OperatorIntelligence()
        )
        self.operator_intelligence = self.personalization.operator
        self.self_model = OperationalSelfModel(
            memory=self.memory,
            gateway=self.model_gateway,
        )


    def route(
        self,
        user_message: str,
        conversation_state: Any | None = None,
    ) -> dict[str, Any]:
        """
        Executa a ativação sináptica, recuperação híbrida e constrói
        o contexto de trabalho compacto.
        """
        context_subject = getattr(conversation_state, "active_subject", None)
        context_project = getattr(conversation_state, "active_project", None)
        domain, artifact_kind = self.personalization.infer_scope_context(
            user_message,
            context_subject=context_subject,
        )
        operator_learning = self.personalization.observe(
            user_message,
            context_subject=context_subject,
            project_id=context_project,
            domain=domain,
            artifact_kind=artifact_kind,
        )
        operator_context = self.personalization.build_context(
            user_message,
            project_id=context_project,
            domain=domain,
            artifact_kind=artifact_kind,
        )

        activation = self.synaptic.activate(user_message)
        system_base = self.memory.build_compact_context(active_seeds=activation.get("seeds", []))
        retrieved_results = self.retriever.retrieve(user_message, limit=5)
        retrieved_pack = self.retriever.get_compact_context_pack(
            user_message,
            max_items=5,
            results=retrieved_results,
        )

        activated_block = [
            "\n# SUBGRAFO NEURAL ATIVADO (SPREADING ACTIVATION)",
            f"Sementes disparadas: {', '.join(activation['seeds'])}",
            "Neurônios de maior carga energetica:"
        ]
        for node_info in activation["top_activated"][:6]:
            activated_block.append(
                f"- [[{node_info['node']}]] (Energia: {node_info['energy']} | Lobo: {node_info['lobe']})"
            )

        if activation["inviolable_constraints"]:
            activated_block.append("\n# RESTRICOES INEGOCIAVEIS ATIVAS:")
            for c in activation["inviolable_constraints"]:
                activated_block.append(f"- {c}")

        # Compilar contexto sob um orçamento real. O import local evita
        # acoplamento circular entre o núcleo cognitivo e a camada de interação.
        from .interaction.context_budget import ContextBudgetManager
        from .interaction.conversation_state import ConversationState

        budget_manager = ContextBudgetManager()
        state = conversation_state if conversation_state is not None else ConversationState()
        system_context = "\n\n".join([
            system_base,
            operator_context,
            "\n".join(activated_block),
        ])
        final_prompt = budget_manager.build_effective_context(
            state=state,
            system_base=system_context,
            retrieved_pack=retrieved_pack,
            max_history_turns=4,
        )

        # Registrar pulso neural em tempo real para o Neural Canvas e HUD
        pulse = record_neural_pulse(
            query=user_message,
            seeds=activation.get("seeds", []),
            top_activated=activation.get("top_activated", []),
            constraints=activation.get("inviolable_constraints", []),
            retrieved=[r.to_dict() for r in retrieved_results]
        )

        # Verificacao de Identidade do Operador a cada interacao
        identity = self.identity_verifier.verify(user_message)
        if not identity["is_authentic"]:
            activation["inviolable_constraints"].append(
                f"[ALERTA DE IDENTIDADE: STATUS {identity['status']}] {'; '.join(identity['flags'])}"
            )

        return {
            "prompt": final_prompt,
            "activation": activation,
            "constraints": activation["inviolable_constraints"],
            "seeds": activation.get("seeds", []),
            "retrieved": [r.to_dict() for r in retrieved_results],
            "pulse": pulse,
            "identity": identity,
            "operator_learning": operator_learning,
            "operator_context": operator_context,
            "personalization_scope": {
                "project_id": context_project,
                "domain": domain,
                "artifact_kind": artifact_kind,
            },
        }

    def audit_response(self, draft_response: str, query: str = "") -> dict[str, Any]:
        """Submete uma resposta preliminar ao crivo do Córtex Pré-Frontal."""
        return self.prefrontal.audit(draft_response, query)

    def think_and_generate(
        self,
        user_message: str,
        conversation_state: Any | None = None,
    ) -> dict[str, Any]:
        """
        Ciclo completo: Roteamento + Recuperação Híbrida + Model Gateway + Auditoria Pré-Frontal.
        """
        route_info = self.route(user_message, conversation_state=conversation_state)
        request = self.model_router.build_request(
            query=user_message,
            system_prompt=route_info["prompt"]
        )

        response = self.model_gateway.generate(request)
        audit = self.audit_response(response.content, user_message)

        return {
            "response": response.content,
            "model": response.model_name,
            "provider": response.provider_name,
            "tier": request.tier.value,
            "telemetry": response.telemetry.to_dict(),
            "audit": audit,
            "route": route_info
        }

    def status(self) -> dict[str, Any]:
        semantics = self.memory.get_semantic_memories()
        total_episodics = self.memory.count_total_episodic_logs()
        recent_logs = self.memory.get_recent_episodic_logs(limit=1)
        active_handoff = self.handoff.load_handoff()

        return {
            "status": "online",
            "total_nodes": len(self.synaptic.nodes),
            "total_synapses": len(self.synaptic.edges),
            "lobes": ["frontal", "parietal", "temporal", "occipital", "limbico"],
            "semantic_categories": list(semantics.keys()),
            "total_episodic_sessions": total_episodics,
            "total_procedures": len(self.memory.get_procedural_items()),
            "latest_session": recent_logs[0]["filename"] if recent_logs else None,
            "has_active_handoff": active_handoff is not None,
            "active_goal": active_handoff.current_goal if active_handoff else None,
            "model_telemetry": self.model_gateway.get_telemetry_summary(),
            "self_model": self.self_model.snapshot(),
            "operator_intelligence": self.operator_intelligence.status(),
            "personalization": self.personalization.status(),
            "embedding": self.retriever.vector_store.embedding_status(),
        }
