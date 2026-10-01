---
id: node-session-handoff
type: architecture
tags:
  - state
  - continuity
  - git
---

# Session Handoff

Camada de continuidade distribuida e sincronizacao de estado de [[ThSyr]].

## Sinapses
- Conectado a [[Cortex_Central]], [[Sincronizacao_Autonoma]], [[Operador]] e [[ThSyr]].
- Mantem o estado operacional ativo em `state/handoff.json` e o espelho legivel em `brain/session_handoff.md`.
- Registra meta atual, etapas concluidas, tarefas pendentes, arquivos em edicao e questoes abertas.
- Viabiliza a transicao perfeita entre dispositivos e sessões sem perda de contexto ou retrabalho.
