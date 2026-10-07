# FISICA TIPOGRAFICA, LINOTIPIA E COMPOSICAO DE TEXTO

## 1. O Princípio dos Tipos Móveis e da Linotipia Mecânica

Nos jornais impressos dos séculos XIX e XX, o texto não era um arranjo fluido de pixels dinâmicos; ele era fundido em liga de chumbo, antimônio e estanho por máquinas de linotipia (como as célebres prensas Mergenthaler). Isso impunha regras físicas intransponíveis:

1. **Justificação Perfeita por Cunha de Aço:** 
   O texto corrido é obrigatoriamente alinhado em bloco à esquerda e à direita (`text-align: justify`). Para evitar "rios brancos" de espaços vazios entre as palavras, a hifenização automática (`hyphens: auto; -webkit-hyphens: auto;`) é mandatória.
2. **Recuo de Parágrafo sem Linha em Branco:**
   Na imprensa física, papel é espaço escasso. Nunca se adiciona espaçamento vertical (`margin-bottom: 1rem`) entre parágrafos consecutivos. Em vez disso, a transição entre parágrafos é marcada exclusivamente pelo **recuo de primeira linha** (`text-indent: 1.25em`).
3. **Fios de Chumbo Mecânicos:**
   As divisões entre colunas e matérias utilizam regras mecânicas de 1px a 3px:
   - Fio simples contínuo (`border-right: 1px solid var(--rule-solid)`).
   - Fio duplo imperial (`border-bottom: 3px double var(--rule-solid)`).
   - Fio pontilhado telegráfico (`border-bottom: 1px dotted var(--rule-muted)`).

---

## 2. A Pilha Tipográfica Sagrada

```css
:root {
  /* Masthead Monumental em Blackletter */
  --font-masthead: 'UnifrakturMaguntia', 'Old English Text MT', serif;

  /* Manchetes e Títulos Editoriais Nobres */
  --font-headline: 'Playfair Display', 'Bodoni MT', Georgia, serif;

  /* Corpo de Texto de Linotipia Clássica */
  --font-body: 'Old Standard TT', 'EB Garamond', 'Times New Roman', serif;

  /* Cartolas, Caixas de Orelha e Versaletes Lapidares */
  --font-subhead: 'Cinzel', 'Trajan Pro', serif;

  /* Indicadores Numéricos, Tabelas e Teletipo */
  --font-teletype: 'JetBrains Mono', 'Courier New', monospace;
}
```

### Importação de Fontes Web Autênticas
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800;900&family=Old+Standard+TT:ital,wght@0,400;0,700;1,400&family=Playfair+Display:ital,wght@0,400;0,600;0,700;0,900;1,400;1,700;1,900&family=UnifrakturMaguntia&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
```

---

## 3. Escala Proporcional de Corpos Tipográficos

| Função Editorial | Família | Tamanho (px) | Peso | Estilo & Transformação |
|---|---|---|---|---|
| **Masthead Principal** | `UnifrakturMaguntia` | 74px a 92px | Regular | Normal, centrado absoluto |
| **Sub-Masthead (Lema)** | `Cinzel` | 11px a 13px | 700 | Caixa Alta, `letter-spacing: 0.18em` |
| **Folio / Barra de Data** | `Cinzel` | 10px a 11px | 800 | Caixa Alta, `letter-spacing: 0.14em` |
| **Manchete Principal (Lead)** | `Playfair Display` | 46px a 56px | 900 | Normal ou Itálico, `line-height: 1.05` |
| **Sub-manchete (Deck)** | `Cinzel` | 13px a 15px | 700 | Caixa Alta, `line-height: 1.28` |
| **Procedência Telegráfica** | `Cinzel` | 11px | 800 | Caixa Alta, seguido de travessão (`—`) |
| **Corpo de Texto Regular** | `Old Standard TT` | 12.5px a 13.5px| 400 | Justificado, `line-height: 1.35` |
| **Capitular (Drop Cap)** | `Playfair Display` / `UnifrakturMaguntia` | 48px a 58px | 900 | Flutuante à esquerda, altura de 3 linhas |
| **Cartolas de Seção** | `Cinzel` | 9px a 11px | 800 | Caixa Alta, `letter-spacing: 0.22em` |
| **Cotações / Tabelas** | `JetBrains Mono` | 10.5px a 11px | 600 | Tabular numbers, alinhado à direita |

---

## 4. O Comportamento da Capitular (Drop Cap)

A capitular não deve ser um caractere solto e desajeitado. Ela deve se ancorar mecanicamente no bloco de texto da coluna:

```css
.lead-body-paragraph::first-letter,
.drop-cap {
  float: left;
  font-family: var(--font-headline);
  font-size: 52px;
  line-height: 44px;
  padding-top: 4px;
  padding-right: 8px;
  padding-bottom: 2px;
  color: var(--ink-primary);
  font-weight: 900;
}
```

---

## 5. Colunamento Real em CSS

Para criar colunas autênticas sem quebras artificiais de parágrafo:

```css
.editorial-multicolumn-3 {
  column-count: 3;
  column-gap: 22px;
  column-rule: 1px solid var(--rule-light);
  text-align: justify;
  hyphens: auto;
}

.editorial-multicolumn-2 {
  column-count: 2;
  column-gap: 20px;
  column-rule: 1px solid var(--rule-light);
  text-align: justify;
  hyphens: auto;
}
```
Isso assegura que o texto flua organicamente da primeira para a segunda e terceira colunas, exatamente como nas páginas compostas em chumbo.
