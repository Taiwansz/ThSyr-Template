---
id: node-sensory-watcher
type: architecture
tags:
  - tech
  - perception
  - runtime
---

# Sensory Watcher

Camada de percepção do [[Continuous_Runtime]]. Observa workspaces, transforma mutações em eventos estruturados e alimenta memória operacional e telemetria local.

## Circuito implementado

1. `PollingWatcher` cria snapshots com hash SHA-256 e ignora diretórios/extensões ruidosos.
2. `WorkspaceMutationWorker` aplica debounce, agrupa mutações e persiste eventos via `EventStore`.
3. Eventos de alto sinal são identificados por arquivos sensíveis (`.env`, chaves, auth, webhook, RLS e security).
4. O worker atualiza `WorkingMemory` e publica `workspace_mutation` no `RuntimeEventBus`.
5. `RuntimeSSEServer` transmite os eventos em `http://127.0.0.1:7474/events`, com heartbeat.
6. Cada evento recebe resumo estrutural, extensões, contagem de linhas e tags de risco sem persistir conteúdo integral.

## Limites conscientes

O backend atual é polling compatível com Windows; não é ainda `ReadDirectoryChangesW`. A análise atual é estrutural, não semântica: não interpreta o significado do diff nem armazena conteúdo integral. O próximo salto é o backend nativo e a análise semântica explícita, não adicionar mais ruído ao sensor.

## Sinapses

- [[Continuous_Runtime]]
- [[Cortex_Central]]
- [[REM_Consolidator]]
- [[ThSyr]]
