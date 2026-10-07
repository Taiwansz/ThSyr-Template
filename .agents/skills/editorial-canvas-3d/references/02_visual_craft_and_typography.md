# Direção Visual, Tipografia e Pureza Editorial

## 1. Princípios de Direção de Arte Anti-Slop

O padrão **Editorial Canvas 3D** é projetado para transmitir autoridade acadêmica, rigor científico e sofisticação de estúdio. Ele combate ativamente todos os clichês estéticos de inteligência artificial generativa.

### Vedações Formais Inegociáveis
1. **Proibição Absoluta de AI-Badges e Pílulas Arredondadas (`rounded-full`):**
   - É terminantemente proibido encapsular títulos, categorias, tags ou subtítulos dentro de ovais cinzas ou coloridos com cantos arredondados de cápsula farmacêutica.
   - Tags e kickers de fase devem ser estritamente tipográficos, estruturados com caixas retangulares técnicas, micro-quadrados coloridos de 8px e tracking generoso (`letter-spacing: 0.22em`).
2. **Proibição de AI-Purple e Gradientes Violeta Clichê:**
   - Banido qualquer uso de lilás elétrico, roxo néon ou meshes escuros genéricos associados a chatbots de consumo.
   - A paleta deve respirar materialidade de laboratório: carvão mineral, papel algodão puro, cobalto técnico e esmeralda de precisão.
3. **Proibição de Emojis:**
   - Tolerância zero a emojis em títulos, parágrafos, código, comentários, commits ou metadados (0 emojis).
   - Use numeração romana, ordinais técnicos (`01 ·`, `FASE 03`), símbolos matemáticos em LaTeX ou setas tipográficas limpas (`→`, `·`, `\approx`).
4. **Proibição de Sparkles e Ícones de Varinha:**
   - Nenhum ícone de estrelinha mágica ou brilho artificial é tolerado.

---

## 2. Tipografia Editorial de Duplo Eixo

A apresentação se sustenta no contraste entre uma família display editorial monumental e uma família monoespaçada de precisão técnica.

### Família Display: Schibsted Grotesk (Google Fonts)
- **Papel:** Títulos monumentais (`h1`), cabeçalhos de fase (`h2`) e números quantitativos dominantes (`.n`).
- **Pesos:** `900` (Black) e `800` (ExtraBold).
- **Tratamento:** Tracking negativo agressivo (`letter-spacing: -0.04em` a `-0.05em`) e entrelinha comprimida (`line-height: 0.96` a `1.02`).
- **Números Tabulares:** Uso obrigatório de `font-variant-numeric: tabular-nums` para alinhamento uniforme de dígitos.

### Família Técnica: JetBrains Mono (Google Fonts)
- **Papel:** Kickers de fase (`.tag`), unidades métricas (`.unit`), fatos e tabelas analíticas (`.facts`), código inline (`code`), HUD de estados e rótulos vetoriais no Canvas 3D.
- **Pesos:** `700` (Bold) e `800` (ExtraBold).
- **Tratamento:** Tracking expandido em maiúsculas (`letter-spacing: 0.2em` a `0.24em`).

---

## 3. Paleta de Cores Não-Óbvia (Matriz Mineral)

Definida através de variáveis CSS no elemento `:root`:

```css
:root {
  /* Plano de Fundo e Superfície */
  --void: #FFFFFF;              /* Branco puro absoluto */
  --vig-edge: rgba(255,255,255,0.94); /* Vinheta perimetral de contenção */

  /* Tipografia e Tinta */
  --ink: #141310;               /* Carvão mineral profundo (títulos e ênfase) */
  --ink-2: #4E4A42;             /* Carvão médio (corpo de texto e subtítulos) */
  --ink-3: #7E7A70;             /* Grafite claro (metadados e HUD) */
  --bone: #3A3630;              /* Base mineral de voxels neutros */

  /* Acentos Semânticos do Canvas */
  --blue: #1F5FA8;              /* Azul Cobalto: lógica, grafos, bytecode, parser */
  --red: #B3392C;               /* Carmim Técnico: ataques, injeções, anomalias, saturação */
  --yellow: #8A6A00;            /* Amarelo Ocre: desvios, roteamento, tráfego, filas */
  --emerald: #1B7A4B;           /* Esmeralda Soberano: auto-hospedagem, autonomia, estabilidade */
}
```

No contexto do JavaScript do Canvas, as mesmas cores são consumidas como strings RGB puras para controle contínuo de canal alfa:
```javascript
const COL = {
  0: '58,54,48',     // Carvão mineral neutro
  1: '31,95,168',    // Azul cobalto
  2: '179,57,44',    // Carmim técnico
  3: '138,106,0',    // Amarelo ocre
  4: '27,122,75'     // Esmeralda soberano
};
```

---

## 4. Sensibilidade Tátil e Microinterações Apple Design

Todos os elementos interativos (tags, linhas tabulares, botões de ação e HUD) possuem micro-resposta física com latência zero:

```css
/* Resposta imediata no toque ou clique (:active) */
.tag:active {
  transform: scale(0.97);
}
.facts div:active {
  transform: scale(0.985);
  background: rgba(20, 19, 16, 0.02);
}
.hint:active {
  transform: scale(0.96);
}
```
A física de desaceleração utiliza curvas de mola natural da Apple: `cubic-bezier(0.16, 1, 0.3, 1)`.
