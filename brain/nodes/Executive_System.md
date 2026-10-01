---
id: node-executive-system
type: architecture
tags:
  - tech
  - core-executive
  - goals
---

# Executive System

Sistema de execucao orientada a objetivos de [[ThSyr]].

## Sinapses
- Conectado a [[Cortex_Central]], [[ThSyr]], [[Tool_Bus]] e [[Permission_Cortex]].
- Transforma objetivos de alto nivel (`Goal`) em planos de acao estruturados (`Plan`) compostos de etapas discretas (`Step`).
- Submete cada plano e etapa a validacao pre-frontal antes da execucao.
- Coleta evidencias estruturadas (`Observation`), avalia o resultado via `ExecutiveVerifier` e dispara replanning automatico em caso de desvio.
- Emite eventos estruturados para `state/events/` e atualiza a sessao ativa em [[Session_Handoff]].
