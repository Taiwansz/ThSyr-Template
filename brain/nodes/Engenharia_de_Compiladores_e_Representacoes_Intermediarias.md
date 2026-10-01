---
id: node-engenharia-compiladores
title: Engenharia de Compiladores e Representacoes Intermediarias
type: theoretical-foundations
lobe: parietal
importance: 0.99
tags:
  - compiladores
  - ast
  - ssa
  - llvm
  - ir
  - otimizacao
  - toklang
  - parietal
---

# Engenharia de Compiladores e Representacoes Intermediarias

Tratado de fundamentacao rigorosa sobre a pipeline canônica de transformacao de linguagens de programacao, construcao de grafos de sintaxe abstrata (AST), analise de fluxo de controle, representacoes intermediarias em forma SSA (Static Single Assignment) e alocacao otimizada de registradores por coloracao de grafos.

---

## 1. A Pipeline Canônica em Seis Fases

A transformacao de um fluxo bruto de caracteres em codigo executavel divide-se em duas macro-estruturas: **Front-End** (dependente da linguagem fonte) e **Back-End** (dependente da arquitetura alvo), mediadas por um **Middle-End** independente de maquina.

```
[ Codigo Fonte ]
       │
       ▼ (1) Analise Lexica (Lexer / Scanning)
[ Tokens Tipados ]
       │
       ▼ (2) Analise Sintatica (Parser)
[ Arvore de Sintaxe Abstrata (AST) ]
       │
       ▼ (3) Analise Semantica (Type Checker & Symbol Table)
[ AST Decorada / Tipada ]
       │
       ▼ (4) Geracao de Codigo Intermediario (IR Lowering)
[ Representacao Intermediaria (IR / SSA Form) ]
       │
       ▼ (5) Otimizacao Independente de Maquina (Passes Middle-End)
[ IR Otimizada ]
       │
       ▼ (6) Selecao de Instrucoes & Alocacao de Registradores (Back-End)
[ Codigo de Maquina / Assembly / Bytecode ]
```

---

## 2. Analise Lexica e Sintatica Rigorosa

1. **Analise Lexica (Scanners)**:
   - Modela padroes lexicos atraves de Expressões Regulares convertidas em Autômatos Finitos Nao-Deterministicos (AFN) via construcao de Thompson.
   - Determinacao via algoritmo de construcao de subconjuntos para gerar Autômatos Finitos Deterministicos (AFD).
   - Minimizacao de estados pelo algoritmo de Hopcroft ($O(n \log n)$).

2. **Analise Sintatica (Gramaticas Livres de Contexto - GLC)**:
   - Definicao formal: $G = (V, \Sigma, R, S)$, onde $V$ e o conjunto de variaveis nao-terminais, $\Sigma$ o alfabeto terminal, $R$ as regras de producao e $S$ o simbolo inicial.
   - **Parsers Top-Down (Descendentes)**: LL(k), Parsing Descendente Recursivo com Lookahead. Exigem gramaticas sem recursao a esquerda e com fatoracao a esquerda.
   - **Parsers Bottom-Up (Ascendentes)**: LR(0), SLR(1), LALR(1), LR(1). Operam por acoes de *Shift* (empilhar token) e *Reduce* (reduzir tokens a um nao-terminal da regra).
   - **Resolucao de Conflitos**:
     - *Shift-Reduce*: Ocorre quando o parser pode tanto empilhar mais um token quanto reduzir a cadeia corrente (ex: problema do *dangling else* resolvido por associatividade explicita).
     - *Reduce-Reduce*: Falha grave na gramatica indicando que multiplas regras competem pelo mesmo padrao sintatico.

---

## 3. A Forma SSA (Static Single Assignment) e Dominancia

A forma SSA revolucionou a fase de otimizacao (Middle-End) de compiladores industriais (LLVM, GCC, HotSpot JVM, V8) ao estabelecer que **cada variavel deve ser atribuida exatamente uma unica vez**, e que toda utilizacao de uma variavel deve ser dominada por sua definicao.

### 1. Funcoes Phi ($\phi$)
Quando múltiplos caminhos de execucao no Grafo de Fluxo de Controle (Control Flow Graph - CFG) convergem em um bloco basico, uma funcao $\phi$ e inserida para selecionar o valor correto com base no bloco predecessor de onde a execucao fluiu:

$$x_3 = \phi(x_1, x_2)$$

### 2. Dominancia e Fronteiras de Dominancia
- **Dominancia ($A \text{ dom } B$)**: Um no $A$ domina o no $B$ no CFG se todo caminho do no de entrada ate $B$ passa obrigatoriamente por $A$.
- **Fronteira de Dominancia ($DF(A)$)**: O conjunto de nos $Y$ tal que $A$ domina um predecessor de $Y$, mas nao domina $Y$ estritamente.
- **Teorema de Cytron et al.**: A insercao minima de funcoes $\phi$ para uma variavel ocorre nas fronteiras de dominancia dos blocos onde a variavel e atribuida.

---

## 4. Passes Canônicos de Otimizacao (Middle-End)

1. **Constant Propagation & Folding**: Avaliacao de expressoes constantes em tempo de compilacao (ex: `2 * 3.14159 * r` vira `6.28318 * r`).
2. **Dead Code Elimination (DCE)**: Remocao de instrucoes cujos resultados nao afetam a saida observavel do programa ou caminhos inatingiveis.
3. **Common Subexpression Elimination (CSE) via GVN (Global Value Numbering)**: Identificacao de calculos redundantes em diferentes blocos basicos.
4. **Loop Invariant Code Motion (LICM)**: Deslocamento de calculos que nao variam dentro de lacos para o cabecalho exterior do laco (*preheader*).
5. **Inlining de Funcoes**: Substituicao da chamada de funcao pelo corpo correspondente, eliminando o overhead de prologo/epilogo da pilha e habilitando otimizacoes contextuais.

---

## 5. Back-End: Alocacao de Registradores por Coloracao de Grafos

A CPU possui um numero finito de registradores fisicos (ex: 16 em x86-64, 32 em AArch64/ARM). O compilador gera codigo inicialmente com infinitos "pseudo-registradores" virtuais.

1. **Analise de Vida de Variaveis (Liveness Analysis)**:
   - Determina o intervalo no qual cada variavel precisa ser preservada na memoria de registros.
2. **Grafo de Interferência**:
   - Cada pseudo-registrador torna-se um vertice. Uma aresta conecta dois vertices se suas vidas uteis se sobrepoem no tempo (nao podem compartilhar o mesmo registrador fisico).
3. **Algoritmo de Chaitin-Briggs**:
   - Reduz a alocacao ao problema matematico de $K$-coloracao de grafos (NP-Completo), onde $K$ e o numero de registradores fisicos disponiveis.
   - Heuristica de Kempe: Se um vertice possui grau $< K$, ele e temporariamente removido da pilha, pois certamente podera receber uma cor quando os vizinhos forem coloridos.
   - **Spilling**: Se todos os vertices restantes tiverem grau $\ge K$, o compilador escolhe um vertice de menor custo de custo benefico para sofrer *spill* (ser descarregado na pilha na memoria RAM via instrucoes `STORE` e `LOAD`).

---

## 6. Conexao Estrategica com o TokLang
O compilador TokLang opera essencialmente como um compilador semantico de instrucoes para modelos de linguagem:
- O `@budget` e `@constraint` atuam como restricoes estaticas de tipo e de registradores (limite finito de tokens de contexto da LLM).
- A poda semantica de stop-words e documentos redundantes e analoga a um passe de **Dead Code Elimination** e **Constant Folding** operando sobre a matriz de atencao $QK^T$.

---

## Sinapses
- Conectado a [[Compiladores]].
- Conectado a [[TokLang_Core_Engine]].
- Conectado a [[Lobo_Parietal]].
- Conectado a [[Microarquitetura_de_Computadores_e_Fisica_do_Silicio]].
- Conectado a [[Grafos_Computacionais_MLIR_e_Otimizacao_de_Tensores]].
