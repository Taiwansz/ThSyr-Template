---
id: node-quantizacao-aritmetica-fp8-int4
title: Quantizacao Aritmetica e Precisao Reduzida (FP8, INT4 e NF4)
type: systems-architecture
lobe: parietal
importance: 0.98
tags:
  - quantizacao
  - fp8
  - int4
  - nf4
  - awq
  - gptq
  - vram
  - parietal
---

# Quantizacao Aritmetica e Precisao Reduzida (FP8, INT4 e NF4)

Fundamentação matemática e de hardware sobre a compressão de tensores de redes neurais a partir de formatos contínuos de alta precisão para representações discretas de ponto fixo e ponto flutuante reduzido, maximizando a densidade de parâmetros por gigabyte de VRAM.

---

## 1. O Espaço Numérico dos Formatos de Ponto Flutuante

Qualquer número de ponto flutuante binário segue a representação canônica:

$$x = (-1)^s \cdot 2^{e - \text{bias}} \cdot \left(1 + \frac{m}{2^p}\right)$$

Onde $s$ é o bit de sinal, $e$ o expoente (alcance dinâmico), $m$ a mantissa/fração (precisão de resolução) e $\text{bias} = 2^{k-1} - 1$.

```
Comparativo Estrutural de Formatos Numéricos em Silício:
-----------------------------------------------------------------------------
Formato  | Bits Totais | Sinal | Expoente | Mantissa | Alcance Aprox.
-----------------------------------------------------------------------------
FP32     | 32 bits     | 1     | 8 bits   | 23 bits  | ~10^-38 a 10^38
FP16     | 16 bits     | 1     | 5 bits   | 10 bits  | ~6 x 10^-5 a 65.504
BF16     | 16 bits     | 1     | 8 bits   | 7 bits   | Identico ao FP32 (evita underflow)
FP8 E4M3 | 8 bits      | 1     | 4 bits   | 3 bits   | Foco em precisão (pesos e ativações)
FP8 E5M2 | 8 bits      | 1     | 5 bits   | 2 bits   | Foco em alcance (gradientes de treino)
INT8     | 8 bits      | 1     | N/A      | 7 bits   | -128 a 127 (inteiro com escala)
INT4     | 4 bits      | N/A   | N/A      | 4 bits   | 16 valores discretos
-----------------------------------------------------------------------------
```

---

## 2. Métodos de Quantização Linear

1. **Quantização Simétrica (Zero-Point Centralizado)**:
   Mapeia o intervalo real $[-\alpha, \alpha]$ para $[-2^{b-1}+1, 2^{b-1}-1]$:
   
   $$q = \text{clamp}\left(\text{round}\left(\frac{x}{S}\right), -q_{\max}, q_{\max}\right), \quad S = \frac{\alpha}{q_{\max}}$$
   
2. **Quantização Assimétrica**:
   Introduz um deslocamento inteiro (*Zero-Point* $Z$) para acomodar distribuições não-simétricas (ex: ativações pós-GELU ou ReLU que não assumem valores negativos):
   
   $$q = \text{round}\left(\frac{x}{S}\right) + Z, \quad S = \frac{x_{\max} - x_{\min}}{2^b - 1}, \quad Z = \text{round}\left(-\frac{x_{\min}}{S}\right)$$

---

## 3. As Técnicas de Compressão INT4 de Fronteira

### 1. GPTQ (Generalized Post-Training Quantization)
Baseado na expansão de Taylor de segunda ordem da perda em torno dos pesos ótimos:

$$\Delta w_q = -\frac{w_q - \text{quant}(w_q)}{[H^{-1}]_{qq}} \cdot H^{-1}_{:, q}$$

Onde $H$ é a matriz Hessiana das ativações ($H = 2 X X^T$). O GPTQ atualiza recursivamente todos os pesos não quantizados da coluna para compensar o erro numérico introduzido pelo peso que acabou de ser discretizado, preservando a coerência do modelo mesmo em 3 e 4 bits.

### 2. AWQ (Activation-aware Weight Quantization)
Observou que nem todos os pesos possuem a mesma importância:
- Apenas 0.1% a 1% dos canais de ativação acumulam valores aberrantes (*outliers* com magnitudes desproporcionais).
- O AWQ protege esses canais críticos multiplicando seus pesos por um fator de escala ótimo $s > 1$ antes da quantização, minimizando a distorção relativa nas ativações que mais impactam a perda final.

### 3. NF4 (NormalFloat 4) no QLoRA
O formato **NormalFloat 4** (Dettmers et al.) é o tipo de dado quanticamente ótimo para variáveis aleatórias com distribuição normal $\mathcal{N}(0, \sigma^2)$:
- Os 16 valores discretos de 4 bits são calculados como os quantis exatos de uma distribuição gaussiana unitária.
- Garante que cada intervalo discreto possua rigorosamente o mesmo número esperado de parâmetros, atingindo a cota máxima de entropia da informação de Shannon.

---

## 4. Impacto Direto no Hardware e no TokLang
- Um modelo LLaMA-3 de 70B exige **140 GB** de VRAM em FP16 (demanda duas GPUs de 80GB interconectadas por NVLink).
- O mesmo modelo quantizado em INT4/NF4 ocupa apenas **35 GB**, cabendo com folga em uma única placa de uso corporativo ou workstation local.
- O TokLang integra-se a esse ecossistema ao podar o contexto antes que ele atinja o conversor numérico, reduzindo a pegada de memória do KV Cache em dobro.

---

## Sinapses
- Conectado a [[Microarquitetura_de_Computadores_e_Fisica_do_Silicio]].
- Conectado a [[Grafos_Computacionais_MLIR_e_Otimizacao_de_Tensores]].
- Conectado a [[TokLang_Core_Engine]].
- Conectado a [[Compiladores]].
- Conectado a [[Lobo_Parietal]].
