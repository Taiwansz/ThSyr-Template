# Design Systems e Linguagens Visuais (Extracao dos Repositorios)

Diretrizes esteticas sintetizadas a partir de padroes de design editorial e industrial contemporaneos.

---

## 1. Principios Visuais Nucleares
- Tolerancia Zero ao Generico: Rejeicao expressa a cliches de IA (combinacoes preto + verde neon, roxo tecnologico amorfo, excesso de rosa, icones de alianca/coracao infantis).
- Contraste e Escala: Uso de diferenca de escala tipografica em vez de aumento descontrolado de peso (font-bold).
- Funcionalidade Estrita de Icones: Cada icone deve carregar significado funcional claro. Proibido espalhar icones como mero ornamento de preenchimento de espaco.

---

## 2. Arquétipo A: Editorial Botanico Sofisticado
- Direcao de Arte: Romantismo botanico editorial, camadas de vidro com acabamento nobre, sensacao de papelaria de luxo.
- Paleta Oficial Canônica:
  - Marinho Profundo: #0D152D / #141A3C (estrutura, fundo escuro, navegacao)
  - Marsala / Peonia: #78112C / #781B3A (acoes principais, assinaturas e enfase)
  - Ouro / Latao Nobre: #CCA43B / #C6AC46 (selos, acentos luminosos)
  - Creme / Marfim Natural: #FBF4DB / #FFF5CF (fundo principal, respiro)
  - Verde Salvia / Folhagem: #6E8268 / #7B896D (elementos botanicos, status suaves)
  - Terracota / Cobre Quente: #B86645 (acoes de destaque e contrastes quentes)
  - Papel Neutro de Leitura: #FFFAF0
- Tipografia:
  - Titulos e Nomes: Cormorant Garamond (300-500), Cinzel, Iowan Old Style ou Georgia.
  - Interface e Dados: Plus Jakarta Sans, Inter ou Avenir Next.
  - Gestos Manuscritos: Great Vibes (aplicado com parcimonia).
- Componentes Caracteristicos:
  - Arcos editoriais em headers e molduras de destaque.
  - Liquid Glassmorphism: transparencia, desfoque controlado, borda interna de luz e fallback solido para navegadores antigos.
  - Selecao de texto personalizada (::selection com fundo marsala e texto creme).

---

## 3. Arquétipo B: Industrial Pop & Dark Tech
- Direcao de Arte: Estetica funcional, limpa, moderna, inspirada em impressao suica, mesas tecnicas e interfaces de alta densidade sem ruido.
- Paleta Oficial Canônica:
  - Zinc Dark Mode & Loop Black: #0a0a0a e neutros profundos.
  - Technical Paper: #f0ede6 (leitura nobre aquecida).
  - Chicane Gold: #c8b560 (acentos de precisao).
  - Vermelho-Tomate & Branco: Contraste vibrante e jovem.
  - Azul-Petroleo & Amarelo-Mostarda: Destaques funcionais.
  - Champagne Gold & Emerald: Indicadores de precisao e telemetria.
- Tipografia e Dados:
  - Numeros tabulares (font-variant-numeric: tabular-nums) em todos os dashboards e tabelas financeiras/metricas.
  - Sans-serif geometrica limpa de alta legibilidade (Geist Sans, Outfit, Space Grotesk).
- Componentes Caracteristicos:
  - Floating pill navigation com backdrop blur de 20px.
  - Cards com Auto Layout estrito e listas interativas de hover em substituicao a bento grids uniformes.
  - Governanca Cognitiva: Aplicacao da Lei de Miller (7 +- 2) e Gestalt — agrupar dashboards legados em no maximo 4-5 blocos conceituais.
  - Zero emojis em interfaces de monitoramento, tabelas e graficos.

---

## 4. Benchmark Mandatorio de Excelencia
Consulte [[design_excellence_benchmark]] para as diretrizes tecnicas completas, curvas de easing (`cubic-bezier(0.16, 1, 0.3, 1)`), preloader cinematico e portao de saida (checklist) que governa todas as entregas do ThSyr.

