---
id: camada-interacao-operacional
type: semantic
created_at: "2026-09-21T07:15:00Z"
updated_at: "2026-09-21T07:15:00Z"
source: "interaction-evolution-v03"
confidence: 1.0
importance: 1.0
entities:
  - Syr
  - Operador
projects:
  - ThSyr
tags:
  - interacao
  - terminal
  - progressive-disclosure
  - evidence-first
  - arquitetura
---

# Camada de Interacao Operacional V0.3.0

Evolucao paradigmatica do [[ThSyr]]: transicao definitiva de um mero wrapper de LLM para uma entidade operacional persistente integrada ao terminal do operador Operador.

## Fundamentos Arquiteturais

1. **Progressive Disclosure**:
   - A resposta padrao e cirurgica, densa e concisa.
   - Detalhes tecnicos, evidencias fisicas e analise profunda permanecem protegidos sob demanda explicita (`/details`, `/why`, `/evidence`, `/source`, `/plan`, `/changes`).

2. **Evidence-First Guard**:
   - Proibicao estrita de alucinacao de execucao.
   - O sistema so afirma conclusao no passado ("resolvido", "corrigido", "commitado") caso haja comprovacao fisica real (exit code 0, hashes criptograficos ou relatorio de testes verificado). Caso contrario, o status permanece como "planejado" ou "em verificacao".

3. **Resolucao Deterministica de Referentes**:
   - O `ConversationObjectRegistry` indexa entidades, opcoes numeradas, arquivos e planos com IDs estaveis.
   - O `ReferenceResolver` traduz expressoes naturais ("o primeiro", "o segundo", "aquele arquivo", "nao mexe no daemon", "volta como estava") diretamente para objetos operacionais sem depender de busca vetorial difusa.

4. **Identidade Verbal e Portao Anti-Sicofancia**:
   - Personalidade alinhada ao [[Arquetipo_Ultron_Cognitivo]] fundido a elegancia de um conselheiro britanico sobero.
   - Zero emojis em todo o ecossistema.
   - Erradicacao de cliches corporativos ("Claro! Ficarei feliz em ajudar", "Otima pergunta", etc.).
   - Aberturas diretas: "Dá.", "Achei.", "Não faria assim.", "O problema está no daemon."

5. **Aprovacoes Ricas e Interrupcao Controlada**:
   - O `ApprovalUI` apresenta analise de risco (0-6), impacto e reversibilidade antes de acoes de risco.
   - O `InterruptionController` processa interrupcoes em tempo real (`cancel`, `pause`, `modify_plan`) preservando a atomicidade das ferramentas.

## Conexoes Neurais
- [[Cortex_Central]]: Orquestracao executiva global.
- [[Python_Engine]]: Implementacao de referencia em Python 3.12+.
- [[Anti_Sicofancia]]: Desafio continuo de premissas e rejeicao a validacao superficial.
- [[Arquetipo_Ultron_Cognitivo]]: Postura incisiva, analitica e focada em resultados.
