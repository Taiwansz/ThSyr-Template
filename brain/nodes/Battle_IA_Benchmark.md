---
id: node-battle-ia
type: project
tags:
  - ai
  - benchmark
  - llm
  - bertscore
  - zero-fallback
  - nvidia-nim
---

# Battle IA: Bancada Experimental Científica de LLMs (Zero Fallback)

Bancada de avaliação empírica e experimental conduzida pelo [[Operador]], servindo como alicerce quantitativo e experimental para o módulo de compressão semântica e benchmarking de modelos de linguagem.

## 1. Provedores e Infraestrutura Real
- **Política Estrita:** ZERO FALLBACK. Proibição absoluta de mocks, simulações ou dados sintéticos. Ausência de retorno de gateway dispara interrupção fatal (`RuntimeError` / `KeyError`).
- **Gateway Oficial:** NVIDIA NIM Cloud API (`https://integrate.api.nvidia.com/v1/chat/completions`).
- **Cluster Físico:** NVIDIA HGX A100 SXM4 (80GB).
- **Modelo de Referência Ativo:** `meta/llama-3.2-11b-vision-instruct` (baixa latência de prefill <600ms e conformidade técnica estrita).
- **Modelos Auditados com Timeout/Indisponibilidade:** `moonshotai/kimi-k3` e `nvidia/nemotron-3-super-120b-a12b`.

## 2. Desenho Experimental (3 Casos x 4 Técnicas = 12 Testes Reais)
- **Casos de Aplicação:**
  1. *Caso 1:* Raciocínio em Sistemas Distribuídos e Tolerância a Falhas (Raft, Paxos, Quórum, Split-Brain).
  2. *Caso 2:* Engenharia de Dados e SQL ANSI sobre DDL Complexo (CTE e Window Function `DENSE_RANK()`).
  3. *Caso 3:* Governança e Auditoria Regulatória de Dados (LGPD - Arts. 5º, 7º e 11º).
- **Técnicas de Prompting e Compressão:**
  - Few-shot (Baseline de Referência com exemplos completos).
  - Zero-shot (Instrução direta sem exemplificação).
  - LLMLingua (Taxa de Compressão 2x - 50% remoção de tokens supérfluos).
  - LLMLingua (Taxa de Compressão 4x - 75% remoção agressiva).

## 3. Métricas Físicas Coletadas
- **Time-to-First-Token (TTFT):** Cronometrado no socket TLS via streaming Server-Sent Events (SSE).
- **Tokens Faturados Oficiais:** Extraídos diretamente do objeto `usage` retornado pela infraestrutura da NVIDIA.
- **Fidelidade Semântica (BERTScore F1):** Avaliação de alinhamento contextual frente ao gabarito canônico.
- **Retenção de Entidades Críticas:** Validação léxica de identificadores e termos-chave de engenharia/direito.
- **Redução de FLOPs de Atenção O(n²):** Mensuração do alívio computacional na camada de Self-Attention.
- **Projeção de Eficiência Econômica:** Custo extrapolado para lotes industriais de 100.000 requisições.

## 4. Artefatos Produzidos
- Base de dados bruta: `battle_ia_resultados_brutos.json`.
- Figuras Científicas em 300 DPI (`figura_10_1` a `10_4`).
- Relatório analítico de validação experimental.

## Sinapses
- Conectado a [[Operador]], [[Model_Gateway]], [[Cortex_Central]] e [[TokLang_Core_Engine]].
