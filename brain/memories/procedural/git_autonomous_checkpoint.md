---
id: proc_git_autonomous_checkpoint
type: procedural
created_at: 2026-09-15T12:00:00Z
updated_at: 2026-09-15T12:00:00Z
source: canonical_procedure
confidence: 1.0
importance: 0.95
entities:
  - Operador
projects:
  - ThSyr
tags:
  - git
  - sync
  - continuity
  - checkpoint
---

# Procedimento: Checkpoint e Sincronização Autônoma Git

> Runbook para persistência contínua e distribuição de estado cognitivo entre múltiplos dispositivos.

## 1. Princípio Fundamental
O operador nunca deve precisar solicitar manualmente comandos de sincronização (`git pull`, `git commit`, `git push`). O sistema opera em sincronia bidirecional contínua: atualiza na partida e persiste no encerramento ou em marcos relevantes.

## 2. Gatilhos de Sincronização
### 2.1 Inbound (Boot / Despertar Imediato)
- Ao ser acionado em qualquer sessão ou agente, executar imediatamente `git pull origin main` (ou fetch + fast-forward/rebase) antes de processar mensagens ou tomar decisões.

### 2.2 Outbound (Checkpoint e Persistência)
- Decisão arquitetural consolidada.
- Nova memória episódica, semântica ou procedural adicionada.
- Alteração estrutural no código da engine.
- Atualização do Session Handoff.
- Encerramento de sessão (Shutdown).

## 3. Formato de Mensagem de Commit
Todo commit gerado autonomamente deve utilizar escopo semântico legível:
- `feat(<componente>): <resumo>`
- `brain(memory): <resumo>`
- `state(handoff): <resumo>`
- `sync(state): <resumo>`

Regra rígida: NUNCA incluir emojis na mensagem de commit.

## 4. Fluxo de Execução
1. `git status --porcelain` para verificar se há alterações.
2. `git add -A` para rastrear as mudanças estruturadas.
3. `git commit -m "<escopo>: <mensagem>"`.
4. `git fetch origin` e reconciliação segura.
5. `git push origin main` com captura de logs de telemetria.

## Sinapses
- Conectado a [[Lobo_Frontal]].
- Conectado a [[Padroes_Engenharia]].
- Conectado a [[ThSyr]].
