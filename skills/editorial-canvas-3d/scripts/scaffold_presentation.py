#!/usr/bin/env python3
"""
Scaffolder CLI Dinamico para Apresentacoes Editorial Canvas 3D (Versao 2.1).
Doutrina ThSyr de Engenharia de Frontend, Rigor Cientifico e Identidades Visuais Calibradas.
"""

import argparse
import os
import sys

BOILERPLATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "templates",
    "boilerplate_editorial.html"
)

AESTHETIC_PRESETS = {
    "swiss_light": {
        "name": "Editorial Claro Suíço",
        "google_fonts": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&family=Schibsted+Grotesk:wght@600;800;900&display=swap",
        "font_display": "'Schibsted Grotesk', system-ui, -apple-system, sans-serif",
        "font_mono": "'JetBrains Mono', ui-monospace, monospace",
        "css_vars": """  --void:#FFFFFF; --ink:#141310; --ink-2:#4E4A42; --ink-3:#7E7A70;
  --red:#B3392C; --blue:#1F5FA8; --yellow:#8A6A00; --bone:#3A3630;
  --emerald:#1B7A4B;""",
        "canvas_clear": "#FFFFFF",
        "vig_bg": "radial-gradient(ellipse 80% 64% at 50% 50%,transparent 0%,rgba(255,255,255,.55) 74%,rgba(255,255,255,.94) 100%)",
        "card_wide": "max-width:840px;background:rgba(255,255,255,.92);padding:44px 52px;border:1px solid rgba(20,19,16,.10);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);box-shadow:0 24px 48px -12px rgba(20,19,16,.06)",
        "col_0": "58,54,48",
        "col_1": "31,95,168",
        "col_2": "179,57,44",
        "col_3": "138,106,0",
        "col_4": "27,122,75"
    },
    "obsidian_dark": {
        "name": "Obsidiana Noturno / Titânio e Âmbar",
        "google_fonts": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&family=Space+Grotesk:wght@600;700;900&display=swap",
        "font_display": "'Space Grotesk', system-ui, -apple-system, sans-serif",
        "font_mono": "'JetBrains Mono', ui-monospace, monospace",
        "css_vars": """  --void:#0B0C0E; --ink:#F3F4F6; --ink-2:#A1A1AA; --ink-3:#71717A;
  --red:#EF4444; --blue:#06B6D4; --yellow:#F59E0B; --bone:#27272A;
  --emerald:#10B981;""",
        "canvas_clear": "#0B0C0E",
        "vig_bg": "radial-gradient(ellipse 80% 64% at 50% 50%,transparent 0%,rgba(11,12,14,.60) 74%,rgba(11,12,14,.96) 100%)",
        "card_wide": "max-width:840px;background:rgba(18,20,24,.88);padding:44px 52px;border:1px solid rgba(255,255,255,.12);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);box-shadow:0 24px 48px -12px rgba(0,0,0,.40)",
        "col_0": "113,113,122",
        "col_1": "6,182,212",
        "col_2": "239,68,68",
        "col_3": "245,158,11",
        "col_4": "16,185,129"
    },
    "heritage_parchment": {
        "name": "Algodão Cru / Pergaminho Clássico & Serif",
        "google_fonts": "https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;700;800&display=swap",
        "font_display": "'Instrument Serif', Georgia, serif",
        "font_mono": "'JetBrains Mono', ui-monospace, monospace",
        "css_vars": """  --void:#FBF9F5; --ink:#1C1814; --ink-2:#544E45; --ink-3:#877E72;
  --red:#99281C; --blue:#2A4B7C; --yellow:#8C682D; --bone:#403932;
  --emerald:#1F4E38;""",
        "canvas_clear": "#FBF9F5",
        "vig_bg": "radial-gradient(ellipse 80% 64% at 50% 50%,transparent 0%,rgba(251,249,245,.55) 74%,rgba(251,249,245,.94) 100%)",
        "card_wide": "max-width:840px;background:rgba(251,249,245,.92);padding:44px 52px;border:1px solid rgba(28,24,20,.14);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);box-shadow:0 24px 48px -12px rgba(28,24,20,.06)",
        "col_0": "64,57,50",
        "col_1": "42,75,124",
        "col_2": "153,40,28",
        "col_3": "140,104,45",
        "col_4": "31,78,56"
    },
    "cyber_brutalist": {
        "name": "Brutalismo Quântico / Dark Lab",
        "google_fonts": "https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@700;800;900&display=swap",
        "font_display": "'Syne', sans-serif",
        "font_mono": "'Space Mono', monospace",
        "css_vars": """  --void:#0D0E12; --ink:#E5E7EB; --ink-2:#9CA3AF; --ink-3:#6B7280;
  --red:#EA580C; --blue:#4F46E5; --yellow:#EAB308; --bone:#1F2937;
  --emerald:#22C55E;""",
        "canvas_clear": "#0D0E12",
        "vig_bg": "radial-gradient(ellipse 80% 64% at 50% 50%,transparent 0%,rgba(13,14,18,.60) 74%,rgba(13,14,18,.96) 100%)",
        "card_wide": "max-width:840px;background:rgba(20,22,28,.90);padding:44px 52px;border:1px solid rgba(255,255,255,.15);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);box-shadow:0 24px 48px -12px rgba(0,0,0,.50)",
        "col_0": "107,114,128",
        "col_1": "79,70,229",
        "col_2": "234,88,12",
        "col_3": "234,179,8",
        "col_4": "34,197,94"
    }
}

THEME_PRESETS = {
    "general": {
        "title": "Arquiteturas Soberanas e Engenharia de Silício",
        "author": "BANCADA TÉCNICA · SISTEMAS COMPLEXOS",
        "p1_metric": "O(V+E)", "p1_sub": "TOPOLOGIA DE GRAFOS", "p1_title": "Topologia e Roteamento", "p1_desc": "Mapeamento topológico de dependências e caminhos críticos no sistema.",
        "p2_metric": "3D", "p2_sub": "ESPACIALIDADE RELACIONAL", "p2_title": "Modelagem Multidimensional", "p2_desc": "Organização de entidades atômicas e satélites dimensionais para agregação analítica.",
        "p3_metric": "O(1)", "p3_sub": "INDEXAÇÃO CONTÍGUA", "p3_title": "Arquitetura Colunar", "p3_desc": "Estruturas de dados contíguas em memória sem pausas de coleta de lixo.",
        "p4_metric": "O(log n)", "p4_sub": "BALANCEAMENTO ESTRITO", "p4_title": "Estrutura Hierárquica", "p4_desc": "Árvores de busca e estruturas balanceadas de travessia determinística.",
        "p5_metric": "λ / μ", "p5_sub": "TEORIA DAS FILAS", "p5_title": "Vazão e Dinâmica de Carga", "p5_desc": "Comportamento assintótico sob pressão com limites estocásticos estritos.",
        "p6_metric": "2π · R", "p6_sub": "CICLO DISTRIBUÍDO", "p6_title": "Protocolos de Consenso", "p6_desc": "Topologia circular e tolerância a partição de rede em ambientes distribuídos.",
        "conc_title": "Síntese e Veredito de Arquitetura", "conc_desc": "Consolidação matemática de alto desempenho, resiliência estrutural e autonomia computacional."
    },
    "datawarehouse": {
        "title": "Modelagem Dimensional e Data Warehouse",
        "author": "TÓPICOS ESPECIAIS II · BANCO DE DADOS",
        "p1_metric": "DIM", "p1_sub": "MODELAGEM ESTRELA", "p1_title": "O Star Schema", "p1_desc": "Separação rigorosa entre métricas numéricas atômicas e atributos textuais de contexto.",
        "p2_metric": "FAT", "p2_sub": "GRANULARIDADE ATÔMICA", "p2_title": "A Tabela de Fatos", "p2_desc": "Armazenamento massivo de ocorrências temporais mensuráveis com chaves estrangeiras compostas.",
        "p3_metric": "SCD", "p3_sub": "SLOWLY CHANGING DIMENSIONS", "p3_title": "Histórico e Versão", "p3_desc": "Tratamento de mutabilidade dimensional via SCD Tipo 1 (sobrescrita) e Tipo 2 (versionamento).",
        "p4_metric": "B-TREE", "p4_sub": "INDEXAÇÃO BITMAP", "p4_title": "Índices Analíticos", "p4_desc": "Otimização de varredura OLAP com índices bitmap para colunas de baixa cardinalidade.",
        "p5_metric": "OLAP", "p5_sub": "OPERAÇÕES MULTIDIMENSIONAIS", "p5_title": "Drill-Down e Roll-Up", "p5_desc": "Agregações hierárquicas e cortes multidimensionais em tempo de consulta.",
        "p6_metric": "ETL", "p6_sub": "EXTRAÇÃO E CARGA", "p6_title": "Pipelines de Ingestão", "p6_desc": "Transformações em lote com consistência eventual e isolamento de carga operacional.",
        "conc_title": "Soberania e Inteligência Analítica", "conc_desc": "Data warehouse resiliente, consultas analíticas sub-segundo e governança de dados blindada."
    },
    "compiler": {
        "title": "Compiladores, AST e Engenharia de Bootstrap",
        "author": "CIÊNCIA DA COMPUTAÇÃO · TURMA N13208A",
        "p1_metric": "DFA", "p1_sub": "ANÁLISE LÉXICA", "p1_title": "Autômatos Finitos Determinísticos", "p1_desc": "Transição de estados e reconhecimento linear de tokens O(n) sem retrocesso.",
        "p2_metric": "AST", "p2_sub": "ANÁLISE SINTÁTICA", "p2_title": "Árvore de Sintaxe Abstrata", "p2_desc": "Hierarquia gramatical pura expurgada de delimitadores e ruído textual.",
        "p3_metric": "O(1)", "p3_sub": "BYTECODE E OTIMIZAÇÃO", "p3_title": "Despacho por Salto Indexado", "p3_desc": "Instruções tableswitch com indexação direta sem branches condicionais aninhados.",
        "p4_metric": "B-TREE", "p4_sub": "TABELA DE SÍMBOLOS", "p4_title": "Resolução de Escopo", "p4_desc": "Tabela de símbolos hierárquica para checagem estática de tipos e variáveis.",
        "p5_metric": "v1 → v2", "p5_sub": "ENG DE BOOTSTRAP", "p5_title": "Auto-Hospedagem (Self-Hosting)", "p5_desc": "Compilador cruzado v0 compilando a versão v1 até a auto-sustentação completa.",
        "p6_metric": "QUINE", "p6_sub": "REFLECTIONS ON TRUSTING TRUST", "p6_title": "O Ataque de Ken Thompson", "p6_desc": "Injeção de backdoor no binário sem vestígios no código-fonte auditável.",
        "conc_title": "Compilação Nativa e Soberania", "conc_desc": "Geração determinística de executáveis com verificação formal de corretude sintática."
    }
}

def scaffold(output_path: str, title: str, author: str, date_str: str, topic: str, aesthetic: str):
    if not os.path.exists(BOILERPLATE_PATH):
        print(f"Erro: Boilerplate nao encontrado em {BOILERPLATE_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(BOILERPLATE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    preset = THEME_PRESETS.get(topic, THEME_PRESETS["general"])
    aes = AESTHETIC_PRESETS.get(aesthetic, AESTHETIC_PRESETS["swiss_light"])

    # Titulo e subtitulo
    effective_title = title if title else preset["title"]
    effective_author = author.upper() if author else preset["author"]

    parts = effective_title.split(" - ") if " - " in effective_title else [effective_title, ""]
    line1 = parts[0].strip()
    line2 = parts[1].strip() if len(parts) > 1 else ""

    # Injetar estetica no boilerplate
    # 1. Google fonts
    content = content.replace(
        'href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&family=Schibsted+Grotesk:wght@600;800;900&display=swap"',
        f'href="{aes["google_fonts"]}"'
    )
    # 2. Font family do body
    content = content.replace(
        "font-family:'Schibsted Grotesk',system-ui,-apple-system,sans-serif;",
        f"font-family:{aes['font_display']};"
    )
    # 3. CSS variables
    default_vars = """:root{
  --void:#FFFFFF; --ink:#141310; --ink-2:#4E4A42; --ink-3:#7E7A70;
  --red:#B3392C; --blue:#1F5FA8; --yellow:#8A6A00; --bone:#3A3630;
  --emerald:#1B7A4B;
}"""
    target_vars = f""":root{{
{aes['css_vars']}
}}"""
    content = content.replace(default_vars, target_vars)

    # 4. Canvas Clear Color
    content = content.replace("gx.fillStyle = '#FFFFFF';", f"gx.fillStyle = '{aes['canvas_clear']}';")

    # 5. Radial vignette
    default_vig = "background:radial-gradient(ellipse 80% 64% at 50% 50%,transparent 0%,rgba(255,255,255,.55) 74%,rgba(255,255,255,.94) 100%)"
    content = content.replace(default_vig, f"background:{aes['vig_bg']}")

    # 6. Card wide
    default_card = ".panel.mid .box.wide{max-width:840px;background:rgba(255,255,255,.92);padding:44px 52px;border:1px solid rgba(20,19,16,.10);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);box-shadow:0 24px 48px -12px rgba(20,19,16,.06)}"
    target_card = f".panel.mid .box.wide{{{aes['card_wide']}}}"
    content = content.replace(default_card, target_card)

    # 7. Paleta COL
    default_col = """const COL = {
  0: '58,54,48',     // Carvao mineral neutro
  1: '31,95,168',    // Azul cobalto
  2: '179,57,44',    // Carmim tecnico
  3: '138,106,0',    // Amarelo ocre
  4: '27,122,75'     // Esmeralda soberano
};"""
    target_col = f"""const COL = {{
  0: '{aes['col_0']}',
  1: '{aes['col_1']}',
  2: '{aes['col_2']}',
  3: '{aes['col_3']}',
  4: '{aes['col_4']}'
}};"""
    content = content.replace(default_col, target_col)

    # Placeholders de conteudo
    replacements = {
        "{{TITULO_DA_APRESENTACAO}}": effective_title,
        "{{AUTOR_OU_DISCIPLINA}}": effective_author,
        "{{DATA}}": date_str,
        "{{TITULO_MONUMENTAL_LINHA1}}": line1,
        "{{TITULO_MONUMENTAL_LINHA2}}": line2,
        "{{SUBTITULO_EXPOSITIVO}}": f"Relatorio analitico e demonstracao tecnica de {effective_title}.",
        "{{METRICA_FASE_1}}": preset["p1_metric"],
        "{{SUBMETRICA_FASE_1}}": preset["p1_sub"],
        "{{TITULO_FASE_1}}": preset["p1_title"],
        "{{DESCRICAO_FASE_1}}": preset["p1_desc"],
        "{{METRICA_FASE_2}}": preset["p2_metric"],
        "{{SUBMETRICA_FASE_2}}": preset["p2_sub"],
        "{{TITULO_FASE_2}}": preset["p2_title"],
        "{{DESCRICAO_FASE_2}}": preset["p2_desc"],
        "{{METRICA_FASE_3}}": preset["p3_metric"],
        "{{SUBMETRICA_FASE_3}}": preset["p3_sub"],
        "{{TITULO_FASE_3}}": preset["p3_title"],
        "{{DESCRICAO_FASE_3}}": preset["p3_desc"],
        "{{METRICA_FASE_4}}": preset["p4_metric"],
        "{{SUBMETRICA_FASE_4}}": preset["p4_sub"],
        "{{TITULO_FASE_4}}": preset["p4_title"],
        "{{DESCRICAO_FASE_4}}": preset["p4_desc"],
        "{{METRICA_FASE_5}}": preset["p5_metric"],
        "{{SUBMETRICA_FASE_5}}": preset["p5_sub"],
        "{{TITULO_FASE_5}}": preset["p5_title"],
        "{{DESCRICAO_FASE_5}}": preset["p5_desc"],
        "{{METRICA_FASE_6}}": preset["p6_metric"],
        "{{SUBMETRICA_FASE_6}}": preset["p6_sub"],
        "{{TITULO_FASE_6}}": preset["p6_title"],
        "{{DESCRICAO_FASE_6}}": preset["p6_desc"],
        "{{TITULO_CONCLUSAO}}": preset["conc_title"],
        "{{SINTESE_CONCLUSAO}}": preset["conc_desc"]
    }

    for key, val in replacements.items():
        content = content.replace(key, val)

    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Apresentacao Editorial Canvas 3D gerada com sucesso em: {output_path} (Estilo: {aes['name']})")

def main():
    parser = argparse.ArgumentParser(description="Scaffold de Apresentacao Editorial Canvas 3D (V2.1)")
    parser.add_argument("--output", "-o", required=True, help="Caminho do arquivo HTML de saida")
    parser.add_argument("--title", "-t", default=None, help="Titulo da apresentacao")
    parser.add_argument("--author", "-a", default=None, help="Autor ou disciplina")
    parser.add_argument("--date", "-d", default="06 DE OUTUBRO DE 2026", help="Data da apresentacao")
    parser.add_argument(
        "--topic",
        choices=["general", "datawarehouse", "compiler"],
        default="general",
        help="Preset tematico de topologia e metricas"
    )
    parser.add_argument(
        "--aesthetic",
        choices=["swiss_light", "obsidian_dark", "heritage_parchment", "cyber_brutalist"],
        default="swiss_light",
        help="Estilo e identidade visual de estúdio"
    )

    args = parser.parse_args()
    scaffold(args.output, args.title, args.author, args.date, args.topic, args.aesthetic)

if __name__ == "__main__":
    main()
