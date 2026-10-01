---
id: node_cognitive_core_v3
type: semantic
source: session_closure_2026-09-23
confidence: 0.95
importance: 1.0
entities:
  - ThSyr
  - Cognitive Core V3
projects:
  - ThSyr
tags:
  - architecture
  - evaluation
  - epistemic
---

# Cognitive Core V3

O salto de inteligência do ThSyr deve ser medido por comportamento verificável,
não por quantidade de nós, prompts ou agentes. A arquitetura canônica é:

1. Epistemic Ledger: fatos com origem, validade, confiança e conflitos.
2. Memory Fabric: evidência bruta, chunks, entidades, claims e decisões.
3. Cognitive Operating Loop: perceber, modelar, recuperar, planejar, agir,
   observar, criticar, verificar, aprender e responder.
4. Evaluation and Feedback: tarefas reais, métricas, regressões e correção.

O primeiro incremento implementado é `engine/evaluation.py`, com benchmark
determinístico de recuperação híbrida e gate separado da suíte unitária. O
benchmark mede apenas recuperação e evidência proibida; uma taxa alta não
representa inteligência geral nem ausência de alucinações.

[[Hybrid_Retrieval]]
[[Executive_System]]
[[Memory_Architecture]]
[[Model_Gateway]]
[[Prefrontal_Cortex]]
[[ThSyr]]
