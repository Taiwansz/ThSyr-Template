---
id: node-continuous-runtime
type: architecture
tags:
  - tech
  - core-runtime
  - scheduler
---

# Continuous Runtime

Motor de execucao persistente e segundo plano de [[ThSyr]].

## Sinapses
- Conectado a [[Cortex_Central]], [[ThSyr]], [[Python_Engine]], [[Proactive_Engine]] e [[Sincronizacao_Autonoma]].
- Transcende a arquitetura de chat passivo atraves de um Event Loop continuo e scheduler de tarefas.
- Opera o `SyncWorker` para verificar alteracoes no git e disparar auto-checkpoints sem necessidade de intervencao manual.
- Opera o `MemoryWorker` para auditoria e consolidacao da saude da memoria.
- Integra o sensor de eventos temporais e monitoramento de prazos em tempo real.
- Especificação de evolução contínua mapeada no documento `docs/RFC_CONTINUOUS_COGNITIVE_SIDECAR.md` (Fases 9 a 13: Watcher Sensorial, Toasts nativos do Windows, Ciclo REM e Live SSE).

## Estado verificado — 2026-09-22

- [[Sensory_Watcher]] implementado com polling determinístico, debounce, filtros de ruído, persistência atômica e classificação de alto sinal.
- O `WorkspaceMutationWorker` atualiza a working memory sem sobrescrever o foco manual e publica eventos no `RuntimeEventBus`.
- `RuntimeSSEServer` expõe `/events` somente em loopback (`127.0.0.1`), com heartbeat e desconexão limpa.
- A prova vertical foi executada: mutação de workspace -> watcher -> barramento -> cliente SSE.
- Ainda não implementados: `ReadDirectoryChangesW`, análise semântica de diffs, HUD além do Neural Canvas e execução de ações TokLang.
- TokLang agora possui compilação determinística para prompt limitado por orçamento; execução de ações ainda permanece fora do DSL.
