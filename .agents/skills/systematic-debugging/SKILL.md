---
name: systematic-debugging
description: Use when encountering any bug, test failure, build error, or unexpected behavior before proposing or applying fixes. Enforces 4-phase root cause investigation over symptom guessing.
---

# Systematic Debugging (Depuracao Sistematica em 4 Fases)

## Visao Geral

Principio fundamental: Sempre isolar a causa raiz antes de qualquer tentativa de correcao. Remendar sintomas e atestado de incapacidade analitica.

## A Lei de Ferro

```
NENHUMA CORRECAO SEM INVESTIGACAO DE CAUSA RAIZ PREVIA
```

Se a Fase 1 nao foi formalmente completada, e expressamente proibido propor ou aplicar patches no codigo.

## Quando Aplicar

Obrigatorio em qualquer anomalia tecnica:
- Falhas em suites de testes.
- Bugs em runtime ou ambiente de producao.
- Erros de compilacao, build ou typecheck.
- Degradacao imprevista de performance.
- Respostas inesperadas de APIs ou servicos.

Especialmente critico quando:
- Ha pressao por solucao rapida (o impulso heuristico de chutar deve ser suprimido).
- A correcao parecer "obvia demais".
- Tentativas anteriores de correcao falharam.

## As Quatro Fases Obrigatorias

### Fase 1: Investigacao de Causa Raiz

1. Inspecao Detalhada de Erros:
   - Nao ignorar mensagens de warning ou rastros de pilha.
   - Ler o stack trace completo: identificar arquivo, linha, funcao e tipo exato da excecao.
2. Reproducao Consistente:
   - Isolar o gatilho minimo que reproduz o erro de forma deterministica.
   - Se for intermitente, coletar telemetria e logs antes de intervir.
3. Inspecao de Alteracoes Recentes:
   - Analisar o `git diff` e o historico recente de commits.
   - Checar se houve mudanca de ambiente, dependencias ou versoes.
4. Rastreamento de Fluxo de Dados (Data Flow Tracing):
   - Onde o dado inconsistente foi originado?
   - Qual modulo forneceu a entrada defeituosa para a funcao que estourou?
   - Rastrear de tras para frente na cadeia de chamadas ate encontrar o ponto exato da mutacao indevida.
   - Corrigir na nascente, jamais no ponto onde o sintoma se manifestou.

### Fase 2: Analise de Padrao

1. Localizar Casos Funcionais Semelhantes:
   - Buscar no mesmo codebase trechos similares que estejam operando corretamente.
2. Comparar com Referencias Canonicas:
   - Ler a implementacao de referencia na integra, linha por linha.
3. Mapear Discrepancias:
   - Identificar minuciosamente o que difere entre o caso quebrado e o caso funcional.
   - Nao descartar detalhes com base na premissa de que "isso nao deveria afetar".

### Fase 3: Hipotese Unica e Teste Minimo

1. Formulacao da Hipotese:
   - Declarar explicitamente: "A falha decorre de [A] porque [B]".
2. Teste Cirurgico Minimo:
   - Alterar estritamente uma variavel por vez para validar ou refutar a hipotese.
   - Proibido empilhar alteracoes multiplas e rodar os testes.
3. Avaliacao de Resultado:
   - Hipotese refutada? Desfazer a alteracao imediatamente e formular nova hipotese limpa.
   - Hipotese comprovada? Avancar para a Fase 4.

### Fase 4: Implementacao e Blindagem

1. Criacao do Teste Vermelho (Red Test):
   - Criar o menor caso de teste possivel que falhe comprovando o bug original.
   - Executar o teste e observar a falha exata esperada.
2. Aplicacao do Patch Cirurgico:
   - Aplicar a correcao apenas na causa raiz identificada.
   - Zero refatoracoes oportunistas em conjunto com a correcao.
3. Validacao (Green) e Regressao:
   - Rodar o teste isolado: confirmar que passou.
   - Rodar a suite completa do projeto para atestar ausencia de efeito colateral.
4. Parada de Emergencia Arquitetural (Regra dos 3 Fixes):
   - Se 3 correcoes sucessivas falharem, PARE imediatamente.
   - 3 falhas consecutivas indicam erro na arquitetura ou no modelo conceitual, nao um bug pontual.
   - Reavaliar premissas e invariantes com o operador antes de tentar um quarto remendo.

## Bandeiras Vermelhas (Sinais de Violacao)

- Dizer "vou tentar alterar X para ver se resolve".
- Propor listas de possiveis mudancas sem analise previa de causa raiz.
- Tentar consertar varias coisas simultaneamente ("enquanto estou aqui, ajustei tambem...").
- Deixar a investigacao incompleta e assumir causas externas sem provas concretas.
