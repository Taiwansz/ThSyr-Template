---
id: node-tool-bus
type: architecture
tags:
  - tech
  - core-tools
  - execution
---

# Tool Bus

Barramento centralizado e tipado de ferramentas de [[ThSyr]].

## Sinapses
- Conectado a [[Cortex_Central]], [[Executive_System]], [[Permission_Cortex]] e [[Python_Engine]].
- Catalogo tipado com schemas estritos de entrada e saida, limites de timeout e estrategias de reversibilidade.
- Fornece adaptadores padronizados para filesystem, git, execucao segura de shell e hipocampo de memoria.
- Submete todas as requisicoes a avaliacao de seguranca previa do [[Permission_Cortex]] antes de qualquer execucao.
- Emite eventos de auditoria operacional em `state/events/`.
