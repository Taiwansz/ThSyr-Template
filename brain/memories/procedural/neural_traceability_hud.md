---
id: proc_neural_traceability_hud
type: procedural
created_at: 2026-09-16T00:30:00Z
updated_at: 2026-09-16T00:30:00Z
source: canonical_procedure
confidence: 1.0
importance: 0.90
entities:
  - Operador
projects:
  - ThSyr
tags:
  - telemetry
  - neural_canvas
  - hud
  - explainability
  - d3
---

# Procedimento: Rastreabilidade Sináptica e HUD do Neural Canvas

> Protocolo de visualização e monitoramento reativo em tempo real dos nódulos e circuitos neurais mobilizados pelo ThSyr.

## 1. Arquitetura de Rastreabilidade (Método 2)
A rastreabilidade sináptica opera em um ciclo fechado entre o motor neurocognitivo e a interface gráfica:

1. **Ativação**: Toda solicitação avaliada via `CognitiveRouter.route()` dispara `SynapticEngine.activate()`.
2. **Registro de Pulso**: O módulo `engine/neural_pulse.py` grava o estado em dois canais:
   - `state/active_synapses.json`: Consumo estruturado para APIs, telemetria e o Continuous Runtime.
   - `brain/active_synapses.js`: Script dinâmico com payload `window.__THSYR_PULSE__` para contornar bloqueios de CORS e permitir execução 100% offline em navegadores via protocolo `file:///`.
3. **Reatividade no D3 (`brain/neural_canvas.html`)**:
   - Um watcher executa a cada 1200ms recarregando a tag `<script>`.
   - Ao detectar um novo identificador de pulso, o canvas:
     - Acende o HUD no canto superior direito com indicador **PULSO ATIVO**.
     - Exibe a consulta, as sementes disparadas e a lista de neurônios com barras de energia proporcionais.
     - Realça os nós com halos luminosos (*glow filters*) na cor do seu respectivo lobo.
     - Destaca as arestas sinápticas com animação de corrente pulsante.
     - Transiciona a câmera suavemente (*smooth zoom/pan*) até o centro de massa do circuito mobilizado.

## 2. Como Utilizar
- Para abrir o canvas no navegador padrão:
  `python thsyr.py graph`
- Para inspecionar uma consulta e disparar o pulso neural:
  `python thsyr.py think "sua pergunta aqui"`
- Para disparar manualmente via Python:
  `from engine.neural_pulse import record_neural_pulse`

## Sinapses
- Conectado a [[Lobo_Frontal]].
- Conectado a [[Padroes_Engenharia]].
- Conectado a [[ThSyr]].
