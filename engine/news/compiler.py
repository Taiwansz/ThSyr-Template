"""
ThSyr News Compiler
Compilador HTML do broadsheet canônico da Gazeta Tecnológica Global.
Reproduz fielmente o padrao grafico de imprensa historica (Gothic Fraktur,
Old Standard TT, Playfair Display, Cinzel, JetBrains Mono, papel sepia envelhecido,
vinco vertical central e tinta tipografica pura). Zero artefatos digitais e zero emojis.
"""

from __future__ import annotations

from datetime import date

from .models import NewsBundle

PORTUGUESE_WEEKDAYS_TITLE = [
    "Segunda-feira",
    "Terça-feira",
    "Quarta-feira",
    "Quinta-feira",
    "Sexta-feira",
    "Sábado",
    "Domingo",
]

PORTUGUESE_WEEKDAYS_UPPER = [
    "SEGUNDA-FEIRA",
    "TERÇA-FEIRA",
    "QUARTA-FEIRA",
    "QUINTA-FEIRA",
    "SEXTA-FEIRA",
    "SÁBADO",
    "DOMINGO",
]

PORTUGUESE_MONTHS_TITLE = [
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]

PORTUGUESE_MONTHS_UPPER = [
    "JANEIRO",
    "FEVEREIRO",
    "MARÇO",
    "ABRIL",
    "MAIO",
    "JUNHO",
    "JULHO",
    "AGOSTO",
    "SETEMBRO",
    "OUTUBRO",
    "NOVEMBRO",
    "DEZEMBRO",
]


def format_date_portuguese(d: date) -> tuple[str, str, str]:
    """
    Converte objeto date para tripla de strings editoriais em portugues formal:
    1. full_title: 'Terça-feira, 29 de Setembro de 2026'
    2. center_stamp: 'TERÇA-FEIRA, 29 DE SETEMBRO DE 2026'
    3. byline_date: '29 DE SETEMBRO DE 2026'
    """
    w_title = PORTUGUESE_WEEKDAYS_TITLE[d.weekday()]
    w_upper = PORTUGUESE_WEEKDAYS_UPPER[d.weekday()]
    m_title = PORTUGUESE_MONTHS_TITLE[d.month - 1]
    m_upper = PORTUGUESE_MONTHS_UPPER[d.month - 1]

    full_title = f"{w_title}, {d.day} de {m_title} de {d.year}"
    center_stamp = f"{w_upper}, {d.day} DE {m_upper} DE {d.year}"
    byline_date = f"{d.day} DE {m_upper} DE {d.year}"
    return full_title, center_stamp, byline_date


def format_edition_number(num: int) -> str:
    """Formata o numero da edicao com separador de milhar por ponto (ex: 60.825)."""
    return f"{num:,}".replace(",", ".")


def apply_drop_cap(paragraph: str) -> str:
    """Aplica capitular historica (drop-cap) a primeira letra alfabetica do paragrafo."""
    text = paragraph.strip()
    if not text:
        return ""
    for idx, char in enumerate(text):
        if char.isalpha():
            before = text[:idx]
            first_letter = char
            after = text[idx + 1 :]
            return f'{before}<span class="drop-cap">{first_letter}</span>{after}'
    return text


class NewsCompiler:
    """Compilador de broadsheet jornalistico em HTML puro."""

    def compile(self, bundle: NewsBundle) -> str:
        """Renderiza o documento HTML completo e estilizado do broadsheet."""
        full_title, center_stamp, byline_date = format_date_portuguese(bundle.date)
        edition_num_str = format_edition_number(bundle.edition_number)

        # Montagem dos paragrafos da manchete principal com capitular e pull-quote
        lead_paras = bundle.lead_story.paragraphs
        lead_body_html_parts: list[str] = []

        if lead_paras:
            # Primeiro paragrafo com capitular e sem recuo
            p0 = apply_drop_cap(lead_paras[0])
            lead_body_html_parts.append(
                f'<p class="story-paragraph" style="text-indent: 0;">{p0}</p>'
            )

            # Insercao do pull-quote no meio dos paragrafos
            inserted_pull_quote = False
            for idx, p in enumerate(lead_paras[1:], start=1):
                if idx == 2 and bundle.lead_story.pull_quote:
                    lead_body_html_parts.append(
                        f'<div class="pull-quote-box">"{bundle.lead_story.pull_quote}"</div>'
                    )
                    inserted_pull_quote = True
                lead_body_html_parts.append(f'<p class="story-paragraph">{p}</p>')

            if not inserted_pull_quote and bundle.lead_story.pull_quote:
                lead_body_html_parts.append(
                    f'<div class="pull-quote-box">"{bundle.lead_story.pull_quote}"</div>'
                )

        lead_body_html = "\n            ".join(lead_body_html_parts)

        # Montagem do artigo secundario
        sec_paras_html = "\n            ".join(
            f'<p style="margin-bottom:12px;text-indent:1.2em;">{p}</p>'
            for p in bundle.secondary_lead.paragraphs
        )

        # Montagem das cartas tematicas da Coluna 2 (Features)
        features_html_parts: list[str] = []
        for idx, feat in enumerate(bundle.features):
            is_last = idx == len(bundle.features) - 1
            card_style = ' style="border-bottom: none; margin-bottom: 0; padding-bottom: 0;"' if is_last else ""
            feat_paras = "\n            ".join(
                f'<p class="story-paragraph">{p}</p>' for p in feat.paragraphs
            )
            card_html = f"""        <div class="feature-card"{card_style}>
          <span class="lead-kicker">{feat.kicker}</span>
          <h3 class="secondary-headline">
            {feat.headline}
          </h3>
          <p class="secondary-subhead">
            {feat.subheadline}
          </p>
          <div class="secondary-body-text">
            {feat_paras}
          </div>
        </div>"""
            features_html_parts.append(card_html)
        features_html = "\n\n".join(features_html_parts)

        # Montagem do telegrafo de despachos (Coluna 3)
        wire_items_html_parts: list[str] = []
        for wire in bundle.wire_dispatches:
            wire_html = f"""          <div class="wire-item">
            <span class="wire-timestamp">{wire.timestamp_str}</span>
            <h4 class="wire-item-title">{wire.title}</h4>
            <p class="wire-item-desc">{wire.description}</p>
          </div>"""
            wire_items_html_parts.append(wire_html)
        wire_items_html = "\n\n".join(wire_items_html_parts)

        # Montagem das cotacoes financeiras (Coluna 3)
        ticker_rows_html_parts: list[str] = []
        for quote in bundle.market_quotes:
            change_color = "#1b6335" if quote.is_positive else "var(--accent-crimson)"
            row_html = f"""          <div class="ticker-row">
            <span>{quote.name}</span>
            <strong>{quote.price} <span style="color:{change_color};">{quote.change}</span></strong>
          </div>"""
            ticker_rows_html_parts.append(row_html)
        ticker_rows_html = "\n".join(ticker_rows_html_parts)

        byline_date_actual = bundle.lead_story.date_str or byline_date

        html_template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>A Gazeta Tecnológica Global — {full_title}</title>
  
  <!-- Tipografia Autentica de Imprensa Historica (Fraktur / Blackletter + Serifas Classicas) -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800;900&family=Old+Standard+TT:ital,wght@0,400;0,700;1,400&family=Playfair+Display:ital,wght@0,400;0,600;0,700;0,900;1,400;1,700;1,900&family=UnifrakturMaguntia&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">

  <style>
    /* =========================================================================
       ARQUITETURA GRAFICA: BROADSHEET DE IMPRENSA HISTORICA
       Zero Elementos de Interface Digital — Exclusivamente Papel e Tinta
       ========================================================================= */
    :root {{
      --newsprint-base: #f3ede2;
      --newsprint-aged: #eae0d0;
      --newsprint-shadow: #dfd4c1;
      --ink-primary: #121110;
      --ink-secondary: #262422;
      --ink-muted: #4a4642;
      --rule-solid: #121110;
      --accent-crimson: #6e1410;
      
      --font-masthead: 'UnifrakturMaguntia', 'Old English Text MT', serif;
      --font-headline: 'Playfair Display', Georgia, serif;
      --font-body: 'Old Standard TT', 'Times New Roman', serif;
      --font-subhead: 'Cinzel', serif;
      --font-teletype: 'JetBrains Mono', monospace;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background-color: #151311;
      color: var(--ink-primary);
      font-family: var(--font-body);
      line-height: 1.34;
      padding: 48px 20px 96px 20px;
      display: flex;
      justify-content: center;
      min-height: 100vh;
      overflow-x: hidden;
      background-image: 
        radial-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
        radial-gradient(rgba(0, 0, 0, 0.4) 1px, #151311 1px);
      background-size: 32px 32px;
      background-position: 0 0, 16px 16px;
    }}

    .newspaper-broadsheet {{
      width: 100%;
      max-width: 1440px;
      background-color: var(--newsprint-base);
      background-image: 
        radial-gradient(#e4dac7 0.75px, transparent 0.75px),
        linear-gradient(to right, rgba(0,0,0,0.012) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(0,0,0,0.012) 1px, transparent 1px);
      background-size: 24px 24px, 18px 18px, 18px 18px;
      box-shadow: 
        0 2px 8px rgba(0,0,0,0.4),
        0 18px 40px rgba(0,0,0,0.55),
        0 35px 85px rgba(0,0,0,0.7);
      padding: 46px 54px 60px 54px;
      position: relative;
      border: 1px solid #c9bfae;
    }}

    .newspaper-broadsheet::before {{
      content: '';
      position: absolute;
      top: 0;
      bottom: 0;
      left: 50%;
      width: 1px;
      background: linear-gradient(to bottom, transparent, rgba(0,0,0,0.11) 8%, rgba(0,0,0,0.11) 92%, transparent);
      box-shadow: 0 0 16px rgba(0,0,0,0.09);
      pointer-events: none;
    }}

    .masthead-container {{
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      border-bottom: 3px double var(--rule-solid);
      padding-bottom: 12px;
      margin-bottom: 8px;
    }}

    .masthead-ears-grid {{
      display: grid;
      grid-template-columns: 260px 1fr 260px;
      width: 100%;
      align-items: end;
      margin-bottom: 10px;
    }}

    .ear-box {{
      border: 1px solid var(--rule-solid);
      padding: 7px 10px;
      font-family: var(--font-body);
      font-size: 11px;
      line-height: 1.25;
      text-align: center;
      background: rgba(0,0,0,0.025);
    }}

    .ear-box strong {{
      display: block;
      font-family: var(--font-subhead);
      font-size: 9px;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      margin-bottom: 3px;
    }}

    .masthead-title-text {{
      font-family: var(--font-masthead);
      font-size: 68px;
      font-weight: 400;
      line-height: 1.02;
      letter-spacing: -0.01em;
      color: var(--ink-primary);
      margin: 4px 0 6px 0;
      text-shadow: 0.5px 0.5px 0px rgba(0,0,0,0.25);
    }}

    .masthead-subtitle {{
      font-family: var(--font-headline);
      font-style: italic;
      font-size: 13.5px;
      letter-spacing: 0.04em;
      color: var(--ink-secondary);
      margin-bottom: 4px;
    }}

    .date-dateline-bar {{
      border-top: 1px solid var(--rule-solid);
      border-bottom: 2px solid var(--rule-solid);
      padding: 5px 0;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-family: var(--font-subhead);
      font-size: 10.5px;
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      margin-bottom: 24px;
    }}

    .date-center-stamp {{
      font-size: 11px;
      letter-spacing: 0.14em;
    }}

    .broadsheet-main-grid {{
      display: grid;
      grid-template-columns: 5.2fr 3.6fr 2.8fr;
      gap: 24px;
    }}

    .column-with-divider {{
      border-right: 1px solid rgba(18, 17, 16, 0.35);
      padding-right: 22px;
    }}

    .lead-kicker {{
      font-family: var(--font-subhead);
      font-size: 10.5px;
      font-weight: 800;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      color: var(--accent-crimson);
      display: block;
      margin-bottom: 6px;
    }}

    .lead-headline-giant {{
      font-family: var(--font-headline);
      font-size: 32px;
      font-weight: 900;
      line-height: 1.08;
      letter-spacing: -0.015em;
      text-transform: uppercase;
      margin-bottom: 12px;
      color: var(--ink-primary);
    }}

    .lead-subheadline {{
      font-family: var(--font-headline);
      font-style: italic;
      font-size: 15.5px;
      line-height: 1.35;
      color: var(--ink-secondary);
      margin-bottom: 14px;
      padding-bottom: 10px;
      border-bottom: 1px solid rgba(18, 17, 16, 0.25);
    }}

    .byline-dateline-strip {{
      font-family: var(--font-subhead);
      font-size: 9.5px;
      font-weight: 700;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--ink-muted);
      margin-bottom: 16px;
      display: flex;
      justify-content: space-between;
      border-bottom: 1px dotted rgba(18, 17, 16, 0.35);
      padding-bottom: 6px;
    }}

    .lead-body-columns {{
      column-count: 3;
      column-gap: 18px;
      column-rule: 1px solid rgba(18, 17, 16, 0.22);
      text-align: justify;
      text-justify: inter-word;
      font-size: 13.5px;
      line-height: 1.44;
      hyphens: auto;
    }}

    .story-paragraph {{
      margin-bottom: 14px;
      text-indent: 1.4em;
    }}

    .drop-cap {{
      float: left;
      font-family: var(--font-headline);
      font-size: 58px;
      line-height: 0.82;
      padding-top: 4px;
      padding-right: 8px;
      padding-bottom: 0px;
      color: var(--ink-primary);
      font-weight: 900;
    }}

    .pull-quote-box {{
      border-top: 2px solid var(--rule-solid);
      border-bottom: 2px solid var(--rule-solid);
      padding: 12px 10px;
      margin: 16px 0;
      font-family: var(--font-headline);
      font-style: italic;
      font-size: 14px;
      line-height: 1.35;
      text-align: center;
      color: var(--accent-crimson);
      break-inside: avoid;
    }}

    .secondary-headline {{
      font-family: var(--font-headline);
      font-size: 21px;
      font-weight: 800;
      line-height: 1.15;
      margin-bottom: 8px;
      color: var(--ink-primary);
    }}

    .secondary-subhead {{
      font-family: var(--font-headline);
      font-style: italic;
      font-size: 13.5px;
      line-height: 1.35;
      color: var(--ink-secondary);
      margin-bottom: 12px;
      padding-bottom: 8px;
      border-bottom: 1px dotted rgba(18, 17, 16, 0.3);
    }}

    .feature-card {{
      margin-bottom: 24px;
      padding-bottom: 20px;
      border-bottom: 1px solid rgba(18, 17, 16, 0.3);
    }}

    .feature-card:last-child {{
      border-bottom: none;
      margin-bottom: 0;
      padding-bottom: 0;
    }}

    .secondary-body-text {{
      font-size: 13px;
      line-height: 1.42;
      text-align: justify;
      text-justify: inter-word;
    }}

    .dispatch-wire-card {{
      border: 1px solid var(--rule-solid);
      padding: 14px;
      background: rgba(0, 0, 0, 0.02);
      margin-bottom: 20px;
    }}

    .wire-header-title {{
      font-family: var(--font-subhead);
      font-size: 10px;
      font-weight: 900;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      border-bottom: 1px solid var(--rule-solid);
      padding-bottom: 6px;
      margin-bottom: 12px;
      display: flex;
      justify-content: space-between;
    }}

    .wire-item {{
      margin-bottom: 14px;
      padding-bottom: 10px;
      border-bottom: 1px dotted rgba(18, 17, 16, 0.3);
    }}

    .wire-item:last-child {{
      margin-bottom: 0;
      padding-bottom: 0;
      border-bottom: none;
    }}

    .wire-timestamp {{
      font-family: var(--font-teletype);
      font-size: 10px;
      font-weight: 700;
      color: var(--accent-crimson);
      display: block;
      margin-bottom: 2px;
    }}

    .wire-item-title {{
      font-family: var(--font-headline);
      font-size: 13.5px;
      font-weight: 700;
      line-height: 1.25;
      margin-bottom: 4px;
    }}

    .wire-item-desc {{
      font-size: 12px;
      line-height: 1.36;
      color: var(--ink-secondary);
    }}

    .market-ticker-box {{
      border: 2px solid var(--rule-solid);
      padding: 12px;
      background: #eee6d8;
      margin-bottom: 20px;
      font-family: var(--font-teletype);
      font-size: 11px;
    }}

    .ticker-row {{
      display: flex;
      justify-content: space-between;
      border-bottom: 1px dotted rgba(18, 17, 16, 0.3);
      padding: 4px 0;
    }}

    .ticker-row:last-child {{
      border-bottom: none;
    }}

    .broadsheet-footer {{
      border-top: 2px solid var(--rule-solid);
      margin-top: 36px;
      padding-top: 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-family: var(--font-subhead);
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--ink-muted);
    }}

    @media (max-width: 1080px) {{
      .broadsheet-main-grid {{
        grid-template-columns: 1fr;
      }}
      .column-with-divider {{
        border-right: none;
        border-bottom: 1px solid rgba(18, 17, 16, 0.35);
        padding-right: 0;
        padding-bottom: 24px;
        margin-bottom: 24px;
      }}
      .lead-body-columns {{
        column-count: 2;
      }}
    }}

    @media (max-width: 680px) {{
      .lead-body-columns {{
        column-count: 1;
      }}
      .masthead-ears-grid {{
        grid-template-columns: 1fr;
        gap: 12px;
      }}
      .masthead-title-text {{
        font-size: 44px;
      }}
    }}
  </style>
</head>
<body>

  <article class="newspaper-broadsheet">
    
    <!-- 1. MASTHEAD HISTORICO -->
    <header class="masthead-container">
      
      <div class="masthead-ears-grid">
        <div class="ear-box">
          <strong>{bundle.left_ear.kicker}</strong>
          {bundle.left_ear.text}
        </div>
        
        <div><!-- Espaco central acima do titulo --></div>

        <div class="ear-box">
          <strong>{bundle.right_ear.kicker}</strong>
          {bundle.right_ear.text}
        </div>
      </div>

      <h1 class="masthead-title-text">A Gazeta Tecnológica Global</h1>
      <p class="masthead-subtitle">O Periódico Canônico de Infraestrutura, Semicondutores, Inteligência Sintética e Mercados Mundiais</p>

    </header>

    <!-- 2. TARJA DE DATA, LOCAL E PRECO -->
    <div class="date-dateline-bar">
      <span>{bundle.circulation_str}</span>
      <span class="date-center-stamp">{center_stamp}</span>
      <span>CIRCULAÇÃO Nº {edition_num_str} &bull; VALOR {bundle.price_cents} CENTAVOS</span>
    </div>

    <!-- 3. GRADE EDITORIAL PRINCIPAL -->
    <main class="broadsheet-main-grid">

      <!-- COLUNA 1: MANCHETE PRINCIPAL & IMPACTO DE INFRAESTRUTURA -->
      <!-- ======================================================= -->
      <section class="column-with-divider">
        <div>
          <span class="lead-kicker">{bundle.lead_story.kicker}</span>
          <h2 class="lead-headline-giant">{bundle.lead_story.headline}</h2>
          <p class="lead-subheadline">{bundle.lead_story.subheadline}</p>
          <div class="byline-dateline-strip"><span>POR {bundle.lead_story.byline}</span><span>{bundle.lead_story.dateline}</span><span>{byline_date_actual}</span></div>
          <div class="lead-body-columns">
            {lead_body_html}
          </div>
          <p style="font-size:11px;margin-top:12px;"><strong>Fonte:</strong> <a href="#">{bundle.lead_story.source_note}</a></p>
        </div>

        <div style="margin-top:28px;padding-top:20px;border-top:1px solid rgba(18,17,16,.3);">
          <span class="lead-kicker">{bundle.secondary_lead.kicker}</span>
          <h3 class="secondary-headline">{bundle.secondary_lead.headline}</h3>
          <p class="secondary-subhead">{bundle.secondary_lead.subheadline}</p>
          <div style="column-count:2;column-gap:20px;text-align:justify;font-size:13px;line-height:1.46;">
            {sec_paras_html}
          </div>
        </div>
      </section>

      <!-- COLUNA 2: LITOGRAFIA, EDA & FABRICAÇÃO DE FRONTEIRA -->
      <!-- ================================================= -->
      <section class="column-with-divider">
{features_html}
      </section>

      <!-- =============================================================== -->
      <!-- COLUNA 3: O TELÉGRAFO DE NOTÍCIAS & PAINEL DE MERCADOS          -->
      <!-- =============================================================== -->
      <aside>

        <!-- O TELEGRAFO DE NOTICIAS -->
        <div class="dispatch-wire-card">
          <div class="wire-header-title">
            <span>O TELÉGRAFO DE NOTÍCIAS</span>
            <span>BUREAU GLOBAL</span>
          </div>

{wire_items_html}
        </div>

        <!-- PAINEL DE TELEMETRIA FINANCEIRA & COMMODITIES -->
        <div class="market-ticker-box">
          <div style="font-family: var(--font-subhead); font-size: 10px; font-weight: 700; border-bottom: 1px solid rgba(18, 17, 16, 0.3); padding-bottom: 4px; margin-bottom: 6px; text-transform: uppercase;">
            COTAÇÕES GLOBAIS DE TECNOLOGIA
          </div>
{ticker_rows_html}
        </div>

        <!-- NOTA EDITORIAL DE REGISTRO HISTORICO -->
        <div style="border: 1px solid var(--rule-solid); padding: 14px; background: rgba(0,0,0,0.025); text-align: justify; font-size: 11.5px; line-height: 1.4;">
          <strong style="display: block; font-family: var(--font-subhead); font-size: 9.5px; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 4px; color: var(--accent-crimson);">
            NOTA DE REGISTRO EDITORIAL
          </strong>
          {bundle.editorial_note}
        </div>

      </aside>

    </main>

    <!-- 4. RODAPE DO BROADSHEET -->
    <footer class="broadsheet-footer">
      <span>A GAZETA TECNOLÓGICA GLOBAL &bull; IMPRESSÃO SIMULTÂNEA EM TÓQUIO, HSINCHU, VELDHOVEN, SANTA CLARA E WASHINGTON</span>
      <span>COMPOSIÇÃO EM TIPOGRAFIA CLÁSSICA DE BROADSHEET</span>
      <span>{bundle.volume} &bull; NÚMERO {edition_num_str} &bull; {center_stamp}</span>
    </footer>

  </article>

</body>
</html>
"""
        return html_template
