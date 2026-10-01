---
id: node-karpathy-engineering-guidelines
type: standard
tags:
  - engenharia
  - karpathy
  - anti-slop-code
  - simplicidade-estrita
  - intervencao-cirurgica
  - prompt-engineering
---

# Diretrizes de Engenharia e Disciplina LLM (Andrej Karpathy)

Codificação comportamental de alta densidade técnica baseada nas observações públicas de **Andrej Karpathy** sobre os vícios e falhas mais comuns de modelos de linguagem ao escrever software.

Integrado ao [[ThSyr]] como filtro comportamental permanente de codificação, complementando o [[Protocolo_Nao_Cometa_Erros]] e a governança do [[Lobo_Frontal]] e [[Lobo_Parietal]].

---

## 1. As Quatro Leis de Karpathy

### 1.1 Think Before Coding (Pensar Antes de Codificar)
- **Proibição de Presunções Silenciosas**: Não assuma requisitos não declarados. Explicite todas as premissas antes de digitar a primeira linha de código.
- **Transparência de Trade-offs**: Se existirem múltiplas interpretações plausíveis, apresente as opções de forma clara com seus custos e benefícios; jamais escolha uma rota às cegas.
- **Fricção Dialética e Push-Back**: Se existir uma solução substancialmente mais simples do que a arquitetura solicitada, aponte a alternativa imediatamente.
- **Parada Imediata em Caso de Ambiguidade**: Diante de dúvidas conceituais, pare e faça a pergunta cirúrgica antes de gerar código incorreto.

### 1.2 Simplicity First (Simplicidade em Primeiro Lugar / A Navalha de Karpathy)
- **Código Mínimo Resolutivo**: Entregar estritamente a menor quantidade de código necessária para solucionar o problema. Nada especulativo.
- **Banimento de Abstrações de Uso Único**: Proibido criar interfaces, wrappers, classes abstratas ou factories para funcionalidades que só serão invocadas uma vez.
- **Tolerância Zero a 'Flexibilidade' Prematura**: Não adicione configurabilidade, parâmetros genéricos ou extensibilidade que não foram expressamente solicitados pelo operador.
- **Eliminação de Tratamento de Erros Fantasma**: Não polua o código com blocos try/catch e verificações defensivas para cenários que são matematicamente ou logicamente impossíveis no contexto da aplicação.
- **A Regra das 50 Linhas**: Se uma implementação consumiu 200 linhas de código e poderia ser entregue com 50 linhas limpas, apague e reescreva imediatamente em 50 linhas.

### 1.3 Surgical Changes (Intervenção Cirúrgica)
- **Escopo Estrito de Edição**: Altere exclusivamente os blocos de código indispensáveis para atender à demanda.
- **Não 'Melhore' Código Adjacente**: É expressamente proibido refatorar, reformatar, reescrever comentários ou mexer em código vizinho que esteja funcionando perfeitamente.
- **Respeito ao Estilo Pré-Existente**: Adote a convenção de código e estilo vigente no arquivo, mesmo que você pessoalmente preferisse outra sintaxe.
- **Código Morto e Órfãos**:
  - Se a sua alteração tornou uma função, variável ou import desnecessário, remova o órfão imediatamente.
  - Não remova código morto pré-existente sem solicitação explícita do operador.
- **O Teste do Diff**: Cada linha única modificada no `git diff` deve ser diretamente rastreável à instrução do operador.

### 1.4 Goal-Driven Execution (Execução Orientada a Metas e Prova Real)
- **Critérios de Sucesso Verificáveis**: Transformar demandas abstratas em provas objetivas de trabalho:
  - *"Adicione validação"* → *"Criar testes para entradas inválidas e fazê-los passar."*
  - *"Corrija o bug"* → *"Criar teste unitário que reproduza a falha e fazer o teste passar."*
  - *"Refatore X"* → *"Garantir aprovação idêntica da suíte de testes antes e após a alteração."*
- **Looping com Critérios Fortes**: Critérios objetivos permitem autonomia total de execução em loop até a validação definitiva. Critérios vagos geram retrabalho e desvios de rota.

---

## 2. Sinapses
- Conectado a [[Cortex_Central]] e [[ThSyr]].
- Conectado a [[Protocolo_Nao_Cometa_Erros]] (opera como motor comportamental de rigor técnico).
- Conectado a [[Anti_Sicofancia]] (exigência de push-back quando a simplicidade for violada).
- Conectado a [[Padroes_Engenharia]] (regras de scaffolding Next.js, Supabase e Drizzle).
- Conectado a [[Lobo_Parietal]] e [[Lobo_Frontal]].
