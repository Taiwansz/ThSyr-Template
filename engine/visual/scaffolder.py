"""
ThSyr Visual Studio Scaffolder
Gerador autônomo de esqueletos HTML de estúdio com base nas matrizes canônicas de nicho.
"""

from typing import Any
from .archetypes import get_niche_preset


def generate_studio_scaffold(
    niche: str,
    title: str = "Studio Interface",
    headline: str = "Arquitetura Visual Sem Concessão",
    description: str = "Interface construida sob a diretriz de estetica distilada e fisica de microinteracoes.",
) -> str:
    """Gera um arquivo HTML completo pré-configurado com a paleta e tipografia do nicho."""
    preset = get_niche_preset(niche)
    palette = preset["palette"]
    fonts = preset["fonts"]
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | ThSyr Visual Studio</title>
  
  <!-- Fontes Canonicas do Nicho: {preset['name']} -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="{fonts['google_fonts_url']}" rel="stylesheet">
  
  <!-- Tailwind CSS via CDN com Configuracao Atomica -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          fontFamily: {{
            display: ['{fonts["display"]}', 'sans-serif'],
            body: ['{fonts["body"]}', 'sans-serif'],
            mono: ['{fonts.get("mono", "JetBrains Mono")}', 'monospace'],
          }},
          colors: {{
            brand: {{
              deep: '{palette["bg_deep"]}',
              surface: '{palette["bg_surface"]}',
              elevated: '{palette["bg_elevated"]}',
              accent: '{palette["accent_primary"]}',
              secondary: '{palette["accent_secondary"]}',
              main: '{palette["text_main"]}',
              muted: '{palette["text_muted"]}',
            }}
          }}
        }}
      }}
    }}
  </script>
  
  <!-- Lucide Icons -->
  <script src="https://unpkg.com/lucide@latest"></script>
  
  <style>
    :root {{
      --bg-deep: {palette["bg_deep"]};
      --bg-surface: {palette["bg_surface"]};
      --border-hairline: {palette["border_hairline"]};
      --border-active: {palette["border_active"]};
      --accent-primary: {palette["accent_primary"]};
      --text-main: {palette["text_main"]};
      --text-muted: {palette["text_muted"]};
      --spring-physics: cubic-bezier(0.16, 1, 0.3, 1);
    }}

    * {{
      box-sizing: border-box;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }}

    body {{
      background-color: var(--bg-deep);
      color: var(--text-main);
      font-family: '{fonts["body"]}', sans-serif;
      min-height: 100vh;
    }}

    .headline-font {{
      font-family: '{fonts["display"]}', sans-serif;
      letter-spacing: -0.035em;
    }}

    .btn-tactile {{
      transition: all 0.15s var(--spring-physics);
    }}
    .btn-tactile:active {{
      transform: scale(0.96);
    }}

    @media (prefers-reduced-motion: reduce) {{
      * {{
        transition: none !important;
        animation: none !important;
      }}
    }}
  </style>
</head>
<body class="selection:bg-brand-accent selection:text-black">

  <!-- Header Translucido Flutuante -->
  <header class="fixed top-4 left-6 right-6 h-16 z-50 rounded-2xl bg-brand-surface/75 backdrop-blur-xl border border-white/10 flex items-center justify-between px-6 shadow-2xl">
    <div class="flex items-center gap-3">
      <div class="w-8 h-8 rounded-lg bg-brand-elevated border border-white/10 flex items-center justify-center font-mono font-bold text-xs text-brand-accent">
        SYR
      </div>
      <div>
        <div class="text-xs font-bold tracking-tight text-white flex items-center gap-2">
          {title.upper()}
          <span class="text-[9px] uppercase tracking-widest px-1.5 py-0.5 rounded bg-brand-accent/10 text-brand-accent border border-brand-accent/20">Studio</span>
        </div>
        <div class="text-[10px] text-brand-muted">{preset['name']}</div>
      </div>
    </div>
    
    <nav class="hidden md:flex items-center gap-6 text-xs text-brand-muted font-medium">
      <a href="#arquitetura" class="hover:text-white transition-colors">Arquitetura</a>
      <a href="#metricas" class="hover:text-white transition-colors">Metricas</a>
      <a href="#contato" class="hover:text-white transition-colors">Operacao</a>
    </nav>

    <div class="flex items-center gap-3">
      <button class="btn-tactile px-4 py-2 rounded-xl bg-brand-accent text-black font-semibold text-xs shadow-lg shadow-brand-accent/20 hover:opacity-95">
        {preset['marketing_heuristics']['cta_primary']}
      </button>
    </div>
  </header>

  <!-- Palco Principal (Bento Grid com Ancora Dominante 60/40) -->
  <main class="pt-28 pb-16 px-6 max-w-7xl mx-auto flex flex-col gap-12">
    
    <!-- Hero Editorial -->
    <section class="flex flex-col gap-4 max-w-3xl pt-8">
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 w-fit text-xs font-mono text-brand-muted">
        <span class="w-1.5 h-1.5 rounded-full bg-brand-accent animate-pulse"></span>
        ESTUDIO DE ALTO PADRAO &middot; THSYR STUDIO
      </div>
      <h1 class="headline-font text-4xl md:text-6xl font-extrabold leading-tight text-white">
        {headline}
      </h1>
      <p class="text-sm md:text-base text-brand-muted leading-relaxed">
        {description}
      </p>
    </section>

    <!-- Bento Grid Assimetrico de Alta Fidelidade -->
    <section class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      
      <!-- Ancora Dominante (60% do peso / 7 colunas) -->
      <div class="lg:col-span-7 rounded-2xl bg-brand-surface border border-white/10 p-8 flex flex-col justify-between gap-8 relative overflow-hidden group hover:border-brand-accent/40 transition-colors">
        <div class="flex flex-col gap-2">
          <div class="text-xs font-mono uppercase tracking-widest text-brand-accent font-semibold">Modulo Principal</div>
          <h3 class="headline-font text-2xl font-bold text-white">Visao Geral do Sistema</h3>
          <p class="text-xs text-brand-muted leading-relaxed max-w-md">
            Preview interativo calibrado para o nicho de {preset['name']}. Composto por materiais translucidos e contraste cirurgico.
          </p>
        </div>

        <!-- Preview Mockup Card -->
        <div class="w-full h-56 rounded-xl bg-brand-elevated border border-white/5 p-4 flex flex-col justify-between font-mono text-xs text-brand-muted">
          <div class="flex items-center justify-between border-b border-white/5 pb-2">
            <span class="text-brand-accent">telemetria_viva.sys</span>
            <span class="text-[10px] text-emerald-400">ONLINE</span>
          </div>
          <div class="space-y-1 text-[11px] text-zinc-300">
            <div>&gt; Inicializando motor visual... [OK]</div>
            <div>&gt; Carregando paleta: {palette['accent_primary']}</div>
            <div>&gt; Status de conversao: Maximo</div>
          </div>
          <div class="flex items-center gap-2 text-[10px] text-brand-muted pt-2 border-t border-white/5">
            <i data-lucide="check-circle" class="w-3.5 h-3.5 text-brand-accent"></i>
            Validado contra AI-slop
          </div>
        </div>
      </div>

      <!-- Modulos Satelites (40% do peso / 5 colunas) -->
      <div class="lg:col-span-5 flex flex-col gap-6">
        
        <!-- Satelite 1 -->
        <div class="rounded-2xl bg-brand-surface border border-white/10 p-6 flex flex-col gap-3">
          <div class="w-8 h-8 rounded-lg bg-brand-accent/10 border border-brand-accent/20 flex items-center justify-center text-brand-accent">
            <i data-lucide="shield-check" class="w-4 h-4"></i>
          </div>
          <h4 class="headline-font text-lg font-bold text-white">Heuristica de Seguranca</h4>
          <p class="text-xs text-brand-muted leading-relaxed">
            {preset['marketing_heuristics']['social_proof']}
          </p>
        </div>

        <!-- Satelite 2 -->
        <div class="rounded-2xl bg-brand-surface border border-white/10 p-6 flex flex-col gap-3">
          <div class="w-8 h-8 rounded-lg bg-brand-secondary/10 border border-brand-secondary/20 flex items-center justify-center text-brand-secondary">
            <i data-lucide="zap" class="w-4 h-4"></i>
          </div>
          <h4 class="headline-font text-lg font-bold text-white">Friccao Zero</h4>
          <p class="text-xs text-brand-muted leading-relaxed">
            {preset['marketing_heuristics']['friction_reducers']}
          </p>
        </div>

      </div>

    </section>

  </main>

  <!-- Script de Inicializacao dos Icones Lucide -->
  <script>
    lucide.createIcons();
  </script>
</body>
</html>
"""
    return html
