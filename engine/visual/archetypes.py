"""
ThSyr Visual Archetypes & Niche Design Blueprints
Matrizes canonicas de nicho mapeadas a partir de referencias mundiais (Behance, Awwwards, Godly, SiteInspire).
"""

from typing import Any

NICHE_ARCHETYPES: dict[str, dict[str, Any]] = {
    "saas_devtools": {
        "name": "SaaS / DevTools / Deep Tech",
        "aliases": ["saas", "devtools", "tech", "api", "infra", "cloud", "developer", "terminal"],
        "benchmarks": ["Linear", "Vercel", "Supabase", "Raycast", "Resend"],
        "fonts": {
            "display": "Space Grotesk",
            "body": "Plus Jakarta Sans",
            "mono": "JetBrains Mono",
            "google_fonts_url": "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&family=JetBrains+Mono:wght@400;500;600&display=swap",
        },
        "palette": {
            "bg_deep": "#09090b",
            "bg_surface": "#121217",
            "bg_elevated": "#18181b",
            "border_hairline": "rgba(255, 255, 255, 0.08)",
            "border_active": "rgba(16, 185, 129, 0.4)",
            "accent_primary": "#10b981",  # Emerald
            "accent_secondary": "#06b6d4",  # Cyan
            "text_main": "#fafafa",
            "text_muted": "#71717a",
            "text_accent": "#34d399",
        },
        "spatial_composition": "Bento Grid assimetrico com card ancora de 60% (preview CLI ou console interativo) e cards satelites de 40%.",
        "marketing_heuristics": {
            "hook_focus": "Ergonomia de codigo, velocidade radical e zero latencia operacional.",
            "cta_primary": "Copiar Comando cURL / Iniciar em 30 Segundos",
            "social_proof": "Metricas numericas exatas (ex: 99.999% uptime, 1.4B logs/dia).",
            "friction_reducers": "Sem cadastro previo com cartao, terminal de experimentacao interativo.",
        },
        "anti_slop_rules": [
            "Proibido gradiente purpura generico em fundo branco ou preto.",
            "Proibido 3 feature cards simetricos em linha.",
            "Proibido Inter ou Roboto como display.",
        ],
    },
    "fintech_wealth": {
        "name": "FinTech / Wealth Management / Private Banking",
        "aliases": ["fintech", "banco", "financeiro", "investimentos", "crypto", "wealth", "pagamentos"],
        "benchmarks": ["Stripe", "Mercury", "Revolut Metal", "Wealthfront", "Ramp"],
        "fonts": {
            "display": "Clash Display",
            "body": "Satoshi",
            "mono": "JetBrains Mono",
            "google_fonts_url": "https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap",
        },
        "palette": {
            "bg_deep": "#0a0d14",
            "bg_surface": "#0f1420",
            "bg_elevated": "#161c2d",
            "border_hairline": "rgba(255, 255, 255, 0.07)",
            "border_active": "rgba(59, 130, 246, 0.45)",
            "accent_primary": "#3b82f6",  # Sapphire
            "accent_secondary": "#d4af37",  # Champagne Gold
            "text_main": "#f8fafc",
            "text_muted": "#64748b",
            "text_accent": "#60a5fa",
        },
        "spatial_composition": "Split-screen superior com simulador interativo de rentabilidade/taxas e camadas de sombra suave em cartoes.",
        "marketing_heuristics": {
            "hook_focus": "Transparencia patrimonial radical e eliminacao de taxas ocultas.",
            "cta_primary": "Simular Rentabilidade / Abrir Conta Corporativa",
            "social_proof": "Volume financeiro transacionado (ex: R$ 4.8B liquidados) e auditoria regulada.",
            "friction_reducers": "Calculadora de taxas em tempo real sem exigir preenchimento de lead.",
        },
        "anti_slop_rules": [
            "Proibido tabelas monotonas sem realce de dados.",
            "Proibido icones 3D inflados de plastico (skeuomorph cartoon).",
        ],
    },
    "luxury_craft": {
        "name": "Luxury / Alta Relojoaria / E-Commerce Monolitico",
        "aliases": ["luxo", "relogio", "joias", "moda", "perfume", "editorial_luxo", "alta_costura"],
        "benchmarks": ["Rolex", "Patek Philippe", "Apple Watch Ultra", "Aesop", "Jacquemus"],
        "fonts": {
            "display": "Fraunces",
            "sub_display": "Playfair Display",
            "body": "Plus Jakarta Sans",
            "mono": "JetBrains Mono",
            "google_fonts_url": "https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;600;700;800&family=Playfair+Display:ital,wght@0,600;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap",
        },
        "palette": {
            "bg_deep": "#050507",
            "bg_surface": "#0e0e12",
            "bg_elevated": "#14141a",
            "border_hairline": "rgba(212, 175, 55, 0.22)",
            "border_active": "rgba(212, 175, 55, 0.55)",
            "accent_primary": "#d4af37",  # Champagne Gold
            "accent_secondary": "#f5e8be",  # Light Gold
            "text_main": "#f5f5f7",
            "text_muted": "#71717a",
            "text_accent": "#e6c86e",
        },
        "spatial_composition": "Full-bleed imersivo com macro-whitespace, tipografia monumental centralizada e proporcoes aureas.",
        "marketing_heuristics": {
            "hook_focus": "Exclusividade de materiais, rigor milimetrico e heranca de manufatura.",
            "cta_primary": "Agendar Concierge Particular / Explorar o Acervo",
            "social_proof": "Linhagem historica, edicoes estritamente limitadas e numeradas.",
            "friction_reducers": "Sem agressividade comercial; jornada contemplativa e silenciosa.",
        },
        "anti_slop_rules": [
            "Proibido banners promocionais gritantes com contadores regressivos vulgares.",
            "Proibido sombras pretas duras e cantos arredondados excessivos (>24px).",
        ],
    },
    "gastronomy_artisan": {
        "name": "Gastronomia Artesanal / Dark Kitchen / Alimentacao Pro",
        "aliases": ["comida", "hamburgueria", "empada", "restaurante", "padaria", "cafe", "gastronomia", "delivery"],
        "benchmarks": ["André da Empada", "Shake Shack", "Tartine Bakery", "Blue Bottle Coffee"],
        "fonts": {
            "display": "Syne",
            "body": "DM Sans",
            "mono": "JetBrains Mono",
            "google_fonts_url": "https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Syne:wght@700;800&family=JetBrains+Mono:wght@500;700&display=swap",
        },
        "palette": {
            "bg_deep": "#0d0b08",
            "bg_surface": "#16130e",
            "bg_elevated": "#221d15",
            "border_hairline": "rgba(245, 158, 11, 0.2)",
            "border_active": "rgba(245, 158, 11, 0.5)",
            "accent_primary": "#d97706",  # Golden Amber
            "accent_secondary": "#b45309",  # Terracotta
            "text_main": "#fef3c7",
            "text_muted": "#a8a29e",
            "text_accent": "#f59e0b",
        },
        "spatial_composition": "Grid sensorial de pratos com badges de tempo de saida de forno e cardapio categorizado com ancoras táteis.",
        "marketing_heuristics": {
            "hook_focus": "Apelo gustativo imediato, ingredientes de origem e afeto artesanal.",
            "cta_primary": "Fazer Pedido no WhatsApp em 1 Clique",
            "social_proof": "Numero de fornadas entregues no mes e avaliacoes com fotos reais.",
            "friction_reducers": "Mensagem pré-formatada para o WhatsApp pronta para envio.",
        },
        "anti_slop_rules": [
            "Proibido fotos de banco genericas descontextualizadas.",
            "Proibido fundos brancos frios de hospital.",
        ],
    },
    "real_estate_architecture": {
        "name": "Real Estate / Arquitetura & Interiores de Alto Padrao",
        "aliases": ["imovel", "apartamento", "imobiliaria", "arquitetura", "construcao", "reforma", "design_interiores"],
        "benchmarks": ["Studio MK27", "Foster + Partners", "Arthur Casas", "Architectural Digest"],
        "fonts": {
            "display": "Cabinet Grotesk",
            "body": "General Sans",
            "mono": "Space Grotesk",
            "google_fonts_url": "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600&family=Space+Grotesk:wght@500;700&display=swap",
        },
        "palette": {
            "bg_deep": "#111113",
            "bg_surface": "#18181c",
            "bg_elevated": "#222228",
            "border_hairline": "rgba(255, 255, 255, 0.08)",
            "border_active": "rgba(120, 113, 108, 0.5)",
            "accent_primary": "#78716c",  # Stone
            "accent_secondary": "#c2410c",  # Corten Steel
            "text_main": "#f5f5f4",
            "text_muted": "#78716c",
            "text_accent": "#fb923c",
        },
        "spatial_composition": "Grid ortogonal austero, sliders de antes/depois, plantas humanizadas vetoriais com cotas milimetricas.",
        "marketing_heuristics": {
            "hook_focus": "Solidez patrimonial, isolamento acustico e harmonia bioclimatica.",
            "cta_primary": "Consultar Memorial Descritivo / Agendar Visita Privativa",
            "social_proof": "Projetos premiados, metro quadrado valorizado e certificacao LEED.",
            "friction_reducers": "Download do PDF de especificacao sem barreira de formulario.",
        },
        "anti_slop_rules": [
            "Proibido violar as restrições físicas estruturais definidas pelo operador.",
            "Proibido fontes manuscritas infantis.",
        ],
    },
    "education_engineering": {
        "name": "Educacao Tecnica / Portais de Engenharia & Whitepapers",
        "aliases": ["aula", "manual", "tutorial", "cisco", "redes", "banco_de_dados", "sql", "whitepaper", "documentacao"],
        "benchmarks": ["Stripe Press", "Apple Developer Portal", "Linear Docs", "Cloudflare Learning"],
        "fonts": {
            "display": "Cabinet Grotesk",
            "body": "Plus Jakarta Sans",
            "mono": "JetBrains Mono",
            "google_fonts_url": "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap",
        },
        "palette": {
            "bg_deep": "#060608",
            "bg_surface": "#0e0e12",
            "bg_elevated": "#15151e",
            "border_hairline": "rgba(212, 175, 55, 0.2)",
            "border_active": "rgba(212, 175, 55, 0.5)",
            "accent_primary": "#d4af37",  # Champagne Gold
            "accent_secondary": "#10b981",  # Emerald
            "text_main": "#f5f5f7",
            "text_muted": "#71717a",
            "text_accent": "#f5e8be",
        },
        "spatial_composition": "Layout de documentacao em 2 colunas com sidebar fixa de progresso (0-100%), stream central rico e blocos CLI com copia tatil.",
        "marketing_heuristics": {
            "hook_focus": "Rigor formal de engenharia, deducao matematica e validacao forense.",
            "cta_primary": "Copiar Script Completo / Baixar Arquivo .PKT",
            "social_proof": "Resultados de execucao de terminal (0% packet loss, rotas O IA confirmadas).",
            "friction_reducers": "Botoes de copia instantanea com feedback visual e atalhos de teclado.",
        },
        "anti_slop_rules": [
            "Proibido codigo incompleto ou com placeholders (TODO/implemente aqui).",
            "Proibido paleta cliche de terminal verde fluorescente anos 90.",
        ],
    },
    "creative_portfolio": {
        "name": "Creative Agency / Portfolio de Elite",
        "aliases": ["portfolio", "estudio", "agencia", "designer", "pessoal"],
        "benchmarks": ["Pentagram", "Collins", "B-Reel", "Active Theory"],
        "fonts": {
            "display": "Syne",
            "body": "DM Sans",
            "mono": "JetBrains Mono",
            "google_fonts_url": "https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Syne:wght@700;800&family=JetBrains+Mono:wght@500;700&display=swap",
        },
        "palette": {
            "bg_deep": "#000000",
            "bg_surface": "#09090b",
            "bg_elevated": "#121217",
            "border_hairline": "rgba(255, 255, 255, 0.1)",
            "border_active": "rgba(245, 158, 11, 0.5)",
            "accent_primary": "#f59e0b",  # Chicane Gold
            "accent_secondary": "#ef4444",  # Intense Red
            "text_main": "#ffffff",
            "text_muted": "#52525b",
            "text_accent": "#fbbf24",
        },
        "spatial_composition": "Display monumental com tracking -0.05em, lista interativa com hover reveal de pre-visualizacao e dock flutuante translúcido.",
        "marketing_heuristics": {
            "hook_focus": "Eloquencia afiada, dominio de arquitetura cognitiva e execucao sem concessao.",
            "cta_primary": "Conhecer o Ecossistema / Iniciar Contato Direto",
            "social_proof": "Projetos em producao com faturamento real e auditorias forenses.",
            "friction_reducers": "Navegacao fluida sem recarregamento e sem rodeios corporativos.",
        },
        "anti_slop_rules": [
            "Proibido frases de autoajuda ou apresentacoes genericas ('sou um desenvolvedor apaixonado').",
            "Proibido gradientes borrados pastel cliches.",
        ],
    },
    "events_ceremonial": {
        "name": "Eventos Nobres / Papelaria & Cerimonial Liturgico",
        "aliases": ["cerimonial", "convite", "celebracao", "liturgico", "festa_nobre"],
        "benchmarks": ["Smythson London", "Soho House Memberships", "Vogue Weddings"],
        "fonts": {
            "display": "Playfair Display",
            "sub_display": "Fraunces",
            "body": "Plus Jakarta Sans",
            "mono": "JetBrains Mono",
            "google_fonts_url": "https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap",
        },
        "palette": {
            "bg_deep": "#09111e",  # Navy Real
            "bg_surface": "#0d1a2d",
            "bg_elevated": "#14253f",
            "border_hairline": "rgba(212, 175, 55, 0.3)",
            "border_active": "rgba(212, 175, 55, 0.65)",
            "accent_primary": "#6d1a2c",  # Marsala
            "accent_secondary": "#d4af37",  # Ouro Nobre
            "text_main": "#fdfbf7",  # Creme Marfim
            "text_muted": "#8392a5",
            "text_accent": "#e6c86e",
        },
        "spatial_composition": "Envelope digital vetorial com selo de cera/monograma interativo e abertura cinematografica.",
        "marketing_heuristics": {
            "hook_focus": "Solemnidade litúrgica, afeto familiar e elegancia atemporal.",
            "cta_primary": "Confirmar Presenca / Presentear no PIX Direto",
            "social_proof": "Versiculos canonicos (Canticos 8:7 e Marcos 10:9).",
            "friction_reducers": "Copia e cola de chave PIX EMVCo nativa com QR Code gerado sem intermediarios.",
        },
        "anti_slop_rules": [
            "Proibido bebidas alcoolicas ou joias em orientacoes de presentes.",
            "Proibido alterar a paleta oficial (Marinho, Marsala, Ouro e Creme).",
        ],
    },
}


def get_niche_preset(query_or_niche: str) -> dict[str, Any]:
    """Identifica o nicho correspondente e retorna os tokens completos do arquétipo."""
    cleaned = query_or_niche.lower().strip()
    
    # Busca exata ou por chave
    if cleaned in NICHE_ARCHETYPES:
        return NICHE_ARCHETYPES[cleaned]
    
    # Busca por aliases
    for key, data in NICHE_ARCHETYPES.items():
        if cleaned in data.get("aliases", []):
            return data
        for alias in data.get("aliases", []):
            if alias in cleaned:
                return data
                
    # Fallback seguro com alta densidade e rigor (SaaS / DevTools)
    return NICHE_ARCHETYPES["saas_devtools"]


def list_available_niches() -> list[str]:
    """Lista as chaves de todos os nichos suportados."""
    return list(NICHE_ARCHETYPES.keys())
