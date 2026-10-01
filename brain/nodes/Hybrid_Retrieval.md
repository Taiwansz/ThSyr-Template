---
id: node-hybrid-retrieval
type: architecture
tags:
  - tech
  - search
  - memory
---

# Hybrid Retrieval

Mecanismo unificado de busca e recuperacao de memorias de [[ThSyr]].

## Sinapses
- Conectado a [[Cortex_Central]], [[ThSyr]] e [[Python_Engine]].
- Executa pontuacao composta de 6 fatores:
  `score = 0.25 * lexico + 0.25 * semantico + 0.20 * grafo + 0.15 * importancia + 0.10 * recencia + 0.05 * contexto`.
- Integra dicionario de sinonimos operacionais em linguagem natural.
- Filtra nós puramente conectivos para evitar poluicao de contexto.
- Fornece pacotes compactos de contexto para o `CognitiveRouter`.
