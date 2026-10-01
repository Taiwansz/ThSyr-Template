---
id: daemon-autonomo-thsyr
title: Daemon Autonomo e Supervisor de Background
type: architecture
lobe: parietal
importance: 0.94
tags:
  - daemon
  - background
  - runtime
  - pid
  - supervisor
---

# Daemon Autonomo e Supervisor de Background

Subsistema de supervisao de processos continuos do ThSyr. Permite que o copilot cognitivo permaneca ativo, executando tarefas agendadas e auditorias mesmo sem um terminal de usuario em primeiro plano.

---

## 1. Responsabilidades Operacionais
- **Persistencia de PID:** Registro do identificador de processo em `state/daemon.pid` com remocao de travas obsoletas (*stale PIDs*).
- **Disparo Desacoplado:** Inicializacao de sessoes em background desacopladas (`DETACHED_PROCESS` no Windows, `start_new_session` em POSIX).
- **Controle de Ciclo de Vida:** Comandos `start`, `stop` e `status` com auditoria em tempo real.
- **Isolamento de Erros:** Execucao de workers com tratamento de excecao para evitar interrupcao em falhas transientes.
- **Telemetria local:** O processo residente inicia o runtime com o endpoint SSE loopback em `127.0.0.1:7474`, permitindo que o Neural Canvas acompanhe o circuito sem exposição externa.

---

## 2. Implementacao de Engenharia
- Modulo: `engine/runtime/daemon.py`
- Classe Central: `SyrDaemonManager`
- Testes: `tests/test_daemon.py`

---

## Sinapses
- Conectado a [[Cortex_Central]].
- Conectado a [[Python_Engine]].
- Conectado a [[Padroes_Engenharia]].
- Conectado a [[Continuous_Runtime]] e [[Sensory_Watcher]].
