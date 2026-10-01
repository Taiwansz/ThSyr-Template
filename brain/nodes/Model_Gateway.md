---
id: node-model-gateway
type: architecture
tags:
  - tech
  - core-gateway
  - models
---

# Model Gateway

Camada de abstracao e roteamento de modelos de linguagem de [[ThSyr]].

## Sinapses
- Conectado a [[Cortex_Central]], [[ThSyr]] e [[Python_Engine]].
- Roteia requisicoes dinamicamente entre 5 tiers: FAST, REASONING, VISION, EMBEDDING e BATCH.
- Implementa tolerancia a falhas com fallback em cascata automatico e provedor local deterministico para operacao offline.
- Persiste telemetria de latencia, consumo de tokens e custo estimado em `state/model_telemetry.json`.
- Integrado ao `CognitiveRouter` para geracao de respostas com auditoria do portao pre-frontal.
