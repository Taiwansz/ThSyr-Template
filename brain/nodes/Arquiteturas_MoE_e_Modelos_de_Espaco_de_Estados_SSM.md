---
id: node-moe-ssm-architectures
title: Arquiteturas MoE e Modelos de Espaco de Estados (SSM)
type: frontier-ai
lobe: parietal
importance: 0.99
tags:
  - moe
  - ssm
  - mamba
  - transformers
  - deepseek
  - mixtral
  - flops
  - parietal
---

# Arquiteturas MoE e Modelos de Espaco de Estados (SSM)

Tratado sobre as duas maiores rupturas arquiteturais contra o monopólio dos Transformers densos convencionais: a esparsidade dinâmica via Mixture of Experts (MoE) e a linearidade temporal via State Space Models (Mamba/SSM).

---

## 1. Mixture of Experts (MoE): Esparsidade Paramétrica Dinâmica

Enquanto um modelo denso tradicional ativa 100% de seus pesos para cada token processado, uma arquitetura MoE substitui as camadas lineares densas de Feed-Forward Network (FFN) por um conjunto de $E$ sub-redes especializadas ("Especialistas" ou *Experts*), governadas por um mecanismo de roteamento (*Gating Router*).

### 1. Equação do Roteador Top-K
Para uma representação de token $x$, a probabilidade de roteamento para o especialista $i$ é dada por um softmax sobre logits esparsos:

$$H(x) = \text{Softmax}(\text{TopK}(x \cdot W_g + \epsilon))$$

Onde $W_g$ é a matriz de projeção do roteador e $\text{TopK}$ zera os pesos de todos os especialistas fora dos $K$ maiores (comumente $K=2$ ou $K=8$ em arquiteturas modernas como Mixtral e DeepSeek-V2/V3).

### 2. Saída da Camada MoE
A ativação final é a soma ponderada das saídas dos especialistas selecionados:

$$y = \sum_{i \in \text{TopK}} H(x)_i \cdot \text{Expert}_i(x)$$

### 3. Desafios Estruturais Críticos:
- **Routing Collapse (Colapso de Roteamento)**: A tendência empírica do roteador de favorecer os mesmos especialistas repetidamente, sobrecarregando alguns e atrofiando outros. Exige a introdução de uma perda auxiliar de balanceamento de carga (*Load Balancing Auxiliary Loss*):
  
  $$\mathcal{L}_{\text{balance}} = \alpha \cdot E \sum_{i=1}^E f_i \cdot P_i$$
  
  Onde $f_i$ é a fração de tokens despachada para o especialista $i$ e $P_i$ a média de probabilidade atribuída pelo roteador.
- **Expert Capacity Factor**: Limite superior de tokens que um especialista pode receber em um lote para evitar estouro de memória e dessincronização de paralelismo inter-nós (*All-to-All communication bottleneck*).

---

## 2. Modelos de Espaço de Estados (SSM) e Mamba

Os Transformers escalam quadraticamente ($O(N^2)$) em relação ao comprimento do contexto $N$ devido à matriz de atenção. Os Modelos de Espaço de Estados mapeiam um sinal de entrada contínuo $x(t) \in \mathbb{R}$ para uma representação latente $h(t) \in \mathbb{R}^N$ e uma saída $y(t) \in \mathbb{R}$ através de equações diferenciais lineares:

$$h'(t) = A h(t) + B x(t), \quad y(t) = C h(t)$$

### 1. Discretização para Computação Digital
Utilizando a regra de retenção de ordem zero (Zero-Order Hold - ZOH) com passo temporal $\Delta$:

$$\bar{A} = \exp(\Delta A), \quad \bar{B} = (\Delta A)^{-1}(\exp(\Delta A) - I) \cdot \Delta B$$

Equação de recorrência discreta:

$$h_t = \bar{A} h_t-1 + \bar{B} x_t, \quad y_t = C h_t$$

### 2. A Inovação do Mamba: Mecanismo de Seleção (S6)
Em SSMs clássicos (S4), as matrizes $A, B, C$ eram invariantes no tempo (LTI - Linear Time-Invariant). O Mamba (Gu & Dao) introduziu a seletividade dinâmica:
- As matrizes $B$, $C$ e o passo $\Delta$ tornam-se **funções diretas da entrada** $x_t$.
- Permite que o modelo decida deterministicamente quais informações memorizar ou descartar em seu estado oculto compacto.
- **Complexidade**: Tempo de inferência rigorosamente linear ($O(N)$) e consumo constante de memória na decodificação ($O(1)$), eliminando a necessidade do gigantesco KV Cache dos Transformers.

---

## 3. Convergência com o TokLang
A arquitetura TokLang pode utilizar matrizes de estado compactas para sumarizar dependências de longo alcance antes de injetar os blocos compactados nos Transformers, unindo a velocidade $O(N)$ do Mamba com a capacidade de raciocínio in-context do mecanismo de atenção.

---

## Sinapses
- Conectado a [[Compiladores]].
- Conectado a [[TokLang_Core_Engine]].
- Conectado a [[Grafos_Computacionais_MLIR_e_Otimizacao_de_Tensores]].
- Conectado a [[Microarquitetura_de_Computadores_e_Fisica_do_Silicio]].
- Conectado a [[Lobo_Parietal]].
