---
id: node-permission-cortex
type: architecture
tags:
  - security
  - permissions
  - prefrontal
---

# Permission Cortex

Modulo de governanca operacional e controle de risco de [[ThSyr]].

## Sinapses
- Conectado a [[Cortex_Central]], [[Anti_Sicofancia]], [[Tool_Bus]] e [[Executive_System]].
- Classifica todas as chamadas de ferramentas em 7 niveis estritos de risco (0 a 6).
- Permite execucao autonoma para leituras e criacoes reversiveis locais (niveis 0 a 2).
- Bloqueia comandos destrutivos e operacoes em projeto sem aprovacao do operador (niveis 3 e 4).
- Exige confirmacao humana explicita e forte para exclusao de dados (nivel 5) e bloqueia acoes criticas de credenciais (nivel 6).
- Garante que a autonomia do agente nunca comprometa a integridade dos dados de [[Operador]].
