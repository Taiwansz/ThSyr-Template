---
id: node-rem-consolidator
type: architecture
tags:
  - tech
  - memory
  - runtime
---

# REM Consolidator

Primeiro consumidor cognitivo do [[Sensory_Watcher]]. Drena eventos do `RuntimeEventBus` em ciclos limitados e os transforma em memórias episódicas persistentes por meio do `MemoryManager`.

## Contrato

- Um ciclo vazio é `idle` e não cria arquivo.
- Eventos de workspace são agrupados em uma memória episódica limitada a 100 caminhos.
- Eventos de alto sinal recebem maior importância e a tag `high_signal`.
- O consumidor usa uma fila própria; a telemetria SSE não compete com a consolidação.

## Limites

O REM atual consolida metadados e resumos estruturais de mutação, não o conteúdo nem o significado semântico dos diffs. A análise não persiste texto de arquivos. A próxima evolução deve adicionar interpretação segura e explícita de diff, sem transformar cada alteração banal em memória permanente.

## Sinapses

- [[Sensory_Watcher]]
- [[Continuous_Runtime]]
- [[Cortex_Central]]
- [[Neural_Canvas]]
