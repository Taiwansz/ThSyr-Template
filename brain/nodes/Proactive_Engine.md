---
id: node-proactive-engine
type: architecture
tags:
  - cognition
  - proactive
  - decisions
---

# Proactive Engine

Motor de iniciativa e governanca de interrupcao de [[ThSyr]].

## Sinapses
- Conectado a [[Cortex_Central]], [[Continuous_Runtime]], [[Operador]] e [[ThSyr]].
- Determina matematicamente quando interromper o operador com base na formula canônica:
  `score = importance + urgency + actionability + confidence - interruption_cost`.
- Garante que informacoes irrelevantes sejam registradas silenciosamente no estado operacional, sem fragmentar a atencao de [[Operador]].
- Monitora autonomamente os prazos de entregas e compromissos críticos, alertando proativamente em caso de risco iminente.
