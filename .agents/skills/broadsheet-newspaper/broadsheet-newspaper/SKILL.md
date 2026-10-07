---
name: broadsheet-newspaper
description: Metodologia de engenharia editorial e gerador de periódicos impressos clássicos (broadsheet) em HTML/CSS estrito de alta fidelidade física. Produz jornais históricos (estilo The New York Times e The Times do século XIX e início do século XX) totalmente agnósticos a nichos (geopolítica, ciências, economia, história, artes, filosofia, tecnologia ou relatórios acadêmicos). Rigor tipográfico (UnifrakturMaguntia, Playfair Display, Old Standard TT, Cinzel), textura mineral de papel envelhecido, vinco central da dobra, divisores de chumbo, capitulares drop-caps e proibição absoluta de interfaces digitais, botões modernos ou AI-slop.
---

# BROADSHEET NEWSPAPER — METODOLOGIA DE IMPRENSA HISTORICA

Esta skill rege a concepcao, redacao, tipografia e compilacao de **jornais impressos broadsheet historicos** em HTML/CSS puro, simulando com rigor forense uma folha fisica de papel jornal centenario recem-saida da prensa de linotipia.

A skill e **estritamente agnostica a nichos**: ela se aplica com a mesma autoridade e sobriedade a politica global, descobertas cientificas, relatorios economicos, analises filosoficas, estudos historicos, literatura, crônicas ou engenharia tecnica.

---

## 1. Dogmas Inegociaveis de Design e Materialidade

1. **Erradicacao Total de Elementos de Interface Digital:**
   * O artefato gerado e uma folha fisica de papel jornal, nao uma pagina web moderna.
   * E terminantemente proibido inserir: barras de navegacao (`<nav>`), botoes flutuantes (`<button>`), seletores de modo escuro/claro, menus hamburguer, campos de formulario, modais, icones modernos em SVG/Lucide, rodapes de copyright digital, links com aparencia de botao ou carrosseis interativos.
   * O leitor consome o documento como se estivesse diante de uma mesa de carvalho examinando um exemplar impresso em 1890 ou 1930.

2. **Fisica de Papel Mineral e Tinta Tipografica:**
   * O documento utiliza tonalidade de papel jornal com calibracao cromatica mineral e envelhecida.
   * **Vinco de Dobra Central:** Presenca obrigatoria de gradiente vertical sutil simulando a dobra fisica da folha broadsheet (`newspaper-broadsheet::before`).
   * **Textura de Fibra:** Micro-granulacao de papel atraves de gradientes radiais sobrepostos.
   * **Tinta Densa e Fio de Chumbo:** Regras tipograficas de 1px a 3px (`double` ou `solid`) dividindo colunas e sessoes, replicando os fios de chumbo das matrizes de impressao mecanica.

3. **Hierarquia Tipografica de Imprensa Historica:**
   * **Masthead (Cabecalho Principal):** Blackletter / Gotica Alemana classica (`UnifrakturMaguntia`) ou serifas romanas monumentais (`Cinzel Decorative`, `Playfair Display SC`).
   * **Manchetes Principais e Secundarias:** Serifas editoriais pesadas (`Playfair Display`, `Prata`, `Bodoni Moda`).
   * **Corpo de Texto:** Tipos romanos de linotipia (`Old Standard TT` ou `EB Garamond`), com alinhamento rigorosamente justificado (`text-align: justify`), recuo de primeira linha (`text-indent: 1.2em`), espacamento entre letras controlado e hifenizacao ativa (`hyphens: auto`).
   * **Cartolas, Epigrafes e Caixas de Orelha:** Serifas romanas lapidares em caixa alta (`Cinzel`).
   * **Cotações, Tabelas, Indicadores e Teletipo:** Tipografia mecânica monoespaçada (`JetBrains Mono`).

4. **Capitular Monumental (Drop Cap):**
   * O primeiro paragrafo da manchete principal (*Lead Story*) e das grandes reportagens deve compulsoriamente abrir com uma letra capitular imponente (3 a 4 linhas de altura, em serifa historica ou gotica).

5. **Proibicao Absoluta de Emojis:**
   * Zero emojis em titulos, textos, tabelas, notas de rodape ou metadados. A autoridade de imprensa tradicional e mantida pela forca vernacular e visual tipografico puro.

---

## 2. Anatomia Canônica da Página Broadsheet

Uma edicao broadsheet completa organiza-se obrigatoriamente na seguinte sequencia vertical:

```
+-------------------------------------------------------------------------+
| [ Orelha Esquerda ]        LEMA / PROVÉRBIO LATINO      [ Orelha Direita ]|
|  Preco / Tempo / Edicao                                  Aviso / Resumo  |
+-------------------------------------------------------------------------+
|                       O MASTHEAD PRINCIPAL                              |
|                   (Nome Gótico Monumental do Jornal)                     |
+-------------------------------------------------------------------------+
|                      SUB-MASTHEAD / SUBTITULO                            |
|          "Orgao Diario e Independente da Opiniao Publica e das Letras"   |
+=========================================================================+
|  BARRA DE DATA: CIDADE / ESTADO | DATA EXTENSA | ANO / VOL | EDICAO     |
+=========================================================================+
| [COLUNA 1]        | [COLUNA 2, 3, 4 - CENTRO]        | [COLUNA 5 e 6]   |
| Despachos         | MANCHETE PRINCIPAL (LEAD STORY)  | SEGUNDA MATERIA  |
| Telegraficos      | Manchete colossal (Playfair)     | Analise / Ensaio |
| (Noticias curtas  | Sublide em 2 linhas (Cinzel)     | com imagem ou    |
| de correspondente | Lide com Drop Cap monumental     | tabela analitica |
| do exterior)      | Texto justificado em 3 colunas   |                  |
+-------------------+----------------------------------+------------------+
| TABELA DE DADOS   | ARTIGOS SECUNDARIOS & CRONICAS   | CARICATURA /     |
| Indicadores /     | Materias de cultura, ciencia ou  | GRAVURA /        |
| Cotacoes / Indices| controversias tematicas          | BOX EDITORIAL    |
+=========================================================================+
| EXPEDIENTE TIPOGRAFICO: Redacao, Oficina Mecanica, Tiragem e Direcao   |
+-------------------------------------------------------------------------+
```

---

## 3. Matriz de Arquétipos Editoriais (Agnósticos a Nichos)

A skill suporta 5 arquétipos cromáticos e conceituais pré-calibrados:

| Arquétipo | Denominação Típica | Paleta de Papel & Tinta | Foco Temático Ideal |
|---|---|---|---|
| **`classic`** | *A Gazeta Historica*, *The Daily Chronicle* | Fundo `#f3ede2`, envelhecido `#eae0d0`, tinta `#121110`, realce Carmesim `#6e1410` | Política internacional, geopolítica, história geral, acontecimentos públicos, filosofia e grandes debates. |
| **`financial`** | *The Financial Gazette*, *O Mercantil & Cambial* | Fundo Salmão Mineral `#f7e6d2`, envelhecido `#ebd5be`, tinta Carvão `#1a1816`, realce Índigo `#1c2d42` | Economia, mercados de capitais, comércio global, análises de commodities, inflação, empresas e finanças. |
| **`scientific`** | *The Scientific Register*, *Os Anais da Ciência* | Fundo Pergaminho Claro `#f5f0e6`, envelhecido `#e9e2d5`, tinta Grafite `#151515`, realce Verde Botânico `#1f3b2b` | Descobertas científicas, astronomia, medicina, biologia, física teórica, relatórios laboratoriais e ensaios acadêmicos. |
| **`cultural`** | *The Literary Review*, *A Tribuna das Belas-Artes* | Fundo Algodão Cru `#f9f6f0`, envelhecido `#ede8df`, tinta Castanho Mineral `#1f1c19`, realce Siena Queimado `#7c3a27` | Crítica literária, exposições de arte, crônicas históricas, ensaios teatrais, linguística e manifestos estéticos. |
| **`tech`** | *A Gazeta Tecnológica*, *The Mechanical Herald* | Fundo Cinza-Ardósia Mineral `#ece9e2`, envelhecido `#dfdbd2`, tinta Mineral `#101010`, realce Bronze `#5c4028` | Semicondutores, arquitetura de sistemas, litografia, engenharia mecatrônica, inteligência artificial e telecomunicações. |

---

## 4. Redação Jornalística e Anti-Slop (Diretrizes Editoriais)

* **Princípio da Pirâmide Invertida:**
  O primeiro parágrafo de cada notícia responde imediatamente às seis perguntas capitais da imprensa de alta estirpe: *O quê*, *Quem*, *Quando*, *Onde*, *Por quê* e *De que maneira*.
* **Voz Ativa e Factual:**
  Proibido o uso de chavões modernos, jargões efêmeros de redes sociais ("revolucionário", "imperdível", "game-changer", "veja a seguir", "insights"). Use verbos de ação vigorosos e precisão terminológica.
* **Sobriedade Histórica:**
  O tom deve soar como um correspondente de prestígio em Londres, Paris, Berlim ou Rio de Janeiro em meados de 1890 ou 1920: denso, culto, comedido e implacável em relação a fatos e evidências.
* **Créditos e Despachos:**
  Toda notícia deve conter cabeçalho de procedência telegráfica em caixa alta (ex: `LONDRES, 6 DE OUTUBRO —`, `WASHINGTON, POR CABO SUBMARINO —`, `GENEBRA, DO NOSSO CORRESPONDENTE —`).

---

## 5. Ferramental CLI e Validação Algorítmica

A skill inclui scripts autônomos na pasta `scripts/` (em Python puro, sem dependências externas frágeis):

### 1. Criar Nova Edição Broadsheet
```bash
python scripts/scaffold_newspaper.py \
  --archetype classic \
  --title "A Gazeta das Nações" \
  --motto "Veritas et Lux in Rebus Publicis" \
  --location "Lisboa & Rio de Janeiro" \
  --volume "XLVIII" \
  --edition "14.892" \
  --price "100 Réis" \
  --lead-title "Tratado Comercial de Navegação e Assinatura dos Acordos Continentais" \
  --output "minha_edicao.html"
```

### 2. Auditar Conformidade Editorial
```bash
python scripts/verify_newspaper.py minha_edicao.html
```
O validador audita 8 critérios inegociáveis:
* Ausência absoluta de emojis.
* Ausência total de tags e classes digitais (`<button>`, `<input>`, `<nav>`, modais).
* Presença da tipografia de linotipia (`Playfair Display`, `Old Standard TT`, `Cinzel`, `UnifrakturMaguntia`).
* Presença da folha broadsheet (`.newspaper-broadsheet`) e textura de papel mineral.
* Presença de vinco vertical central da dobra de página.
* Presença de manchete principal com lide em capitular (*drop cap*).
* Presença da barra de data, orelhas e expediente tipográfico.
* Grid colunar justificado e divisores mecânicos de chumbo.

### 3. Captura Visual em Alta Resolução (Opcional com Playwright)
```bash
python scripts/capture_newspaper.py minha_edicao.html --output preview_broadsheet.png
```

---

## 6. Checklist de Homologação Final

Antes de declarar o jornal concluído para o professor ou operador:
- [ ] O arquivo HTML é autônomo e abre diretamente em qualquer navegador desktop.
- [ ] O design se mantém em folha de broadsheet centrada de 1440px de largura com vinco e textura tátil.
- [ ] A tipografia transmite o peso de uma prensa de tipos móveis (Gótica + Serifas + Cinzel + Justificação rigorosa).
- [ ] Não há nenhum vestígio de website moderno (zero botões, zero controles digitais).
- [ ] O texto editorial está 100% livre de emojis e redigido em português formal refinado ou conforme o idioma especificado.
- [ ] O script `verify_newspaper.py` emitiu pontuação 100/100 (APPROVED).
