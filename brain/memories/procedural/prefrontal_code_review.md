---
id: proc_prefrontal_code_review
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
  - prefrontal
  - quality
  - anti_sycophancy
  - audit
---

# Procedimento: Revisão de Código e Portão Pré-Frontal

> Procedimento de auditoria interna executado antes de propor ou consolidar código no ecossistema.

## 1. Portões de Inibição Obrigatórios
1. Portão 1 (Anti-Sicofância): Testar ativamente se a solicitação ou proposta tem falhas lógicas, redundâncias ou superengenharia. Proibido validar ideias frágeis por conveniência.
2. Portão 2 (Restrições Reais): Garantir que nenhuma lei imutável foi quebrada (restrições físicas declaradas, limites estruturais, integridade ontológica de entidades e dados).
3. Portão 3 (Tolerância Zero a Emojis): Verificar a ausência total de caracteres gráficos/emojis em respostas, código, comentários, documentação e mensagens de commit.
4. Portão 4 (Redução de Entropia): Todo componente deve possuir tipagem explícita, caminhos portáveis e conformidade com os testes automatizados.

## 2. Sequência de Auditoria
1. Executar `python -m unittest discover -s tests -p "test_*.py"`.
2. Verificar se o status e métricas refletem dados reais.
3. Submeter qualquer rascunho de resposta ou commit ao `PreFrontalCortex.audit()`.
4. Em caso de inibição (`INHIBITED`), corrigir a violação antes de qualquer apresentação ao operador.

## Sinapses
- Conectado a [[Lobo_Frontal]].
- Conectado a [[Padroes_Engenharia]].
- Conectado a [[ThSyr]].
