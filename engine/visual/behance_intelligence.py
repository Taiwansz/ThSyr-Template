"""
ThSyr Behance Design Intelligence Engine
Extracao de paletas nao-obvias, disposicao editorial de icones, textos e ritmo visual por ramo de comercio.
Baseado na desconstrucao forense de projetos premiados do Behance, Awwwards e Dribbble.
"""

from typing import Any

# CATALOGO DE RAMOS E COMERCIOS REAIS COM PALETAS NAO-OBVIAS DO BEHANCE
COMMERCE_BRANCH_INTELLIGENCE: dict[str, dict[str, Any]] = {
    "cafeteria_torrefacao": {
        "ramo": "Cafeteria Especial / Torrefacao Artesanal",
        "aliases": ["cafe", "cafeteria", "torrefacao", "coffee", "graos"],
        "filosofia_behance": "Fuga do marrom obvio e do amarelo clipart. Inspirado em embalagens de microlotes de especialidade e papelaria de estúdios nordicos.",
        "paleta_nao_obvia": {
            "bg_principal": "#f5f2eb",  # Papel algodao cru nao branqueado
            "bg_superficie": "#ffffff",  # Branco marfim
            "texto_titulo": "#1c1b18",  # Carvao torrado profundo (nunca preto puro)
            "texto_corpo": "#57534e",  # Cinza quente mineral
            "acento_primario": "#1e3a2b",  # Verde floresta botânico de folha de cafeeiro
            "acento_secundario": "#c25e38",  # Terracota de tijolo de estufa / argila
            "borda_hairline": "rgba(28, 27, 24, 0.08)",
            "selo_badge": "#e7e0d3",  # Tom de saco de juta texturizado
        },
        "tipografia": {
            "display": "Fraunces",
            "body": "Plus Jakarta Sans",
            "mono": "JetBrains Mono",
            "contraste_estilistico": "Titulos mesclando peso 700 com palavras pontuais em italico elegante.",
        },
        "disposicao_icones": {
            "regra": "Icones nunca ficam soltos no meio do card. Ficam integrados a selos circulares (stamps) com micro-bordas ou como marcadores inline sutis de 14px a 16px com stroke 1.25px.",
            "estilo": "Minimalista linear fino, com fundo circular de baixa opacidade.",
        },
        "disposicao_textos": {
            "eyebrow": "Caixa alta, tamanho 10px, tracking 0.25em, precedido por ponto sutil.",
            "titulo": "Display grande com quebra de linha deliberada para evitar viúvas e ritmo poetico.",
            "paragrafo": "Maximo de 3 linhas com entrelinhamento 1.65, garantindo respiro e clareza.",
            "dados": "Notas sensoriais e altitude em JetBrains Mono com labels minusculas acima do valor.",
        },
        "cenografia_marca": [
            "Carimbos circulares vetoriais com texto em curva (Est. 2026 / Microlote Selecionado).",
            "Tabela de atributos sensoriais (Acidez, Corpo, Docura, Torra) com barras de progresso finas.",
        ]
    },

    "advocacia_boutique": {
        "ramo": "Advocacia Boutique / Consultoria Juridica de Elite",
        "aliases": ["direito", "advocacia", "juridico", "advogado", "tributario", "compliance", "societario"],
        "filosofia_behance": "Abolicao total do azul BIC corporativo e do preto funerario. Inspiracao em escritórios londrinos e de Genebra.",
        "paleta_nao_obvia": {
            "bg_principal": "#0b120f",  # Verde abissal quase negro
            "bg_superficie": "#121b17",  # Superficie florestal profunda
            "texto_titulo": "#f4f3ef",  # Alabastro nobre
            "texto_corpo": "#8a968f",  # Cinza sálvia atenuado
            "acento_primario": "#c49a6c",  # Bronze antigo escovado
            "acento_secundario": "#3d5a49",  # Verde louro heraldico
            "borda_hairline": "rgba(196, 154, 108, 0.2)",
            "selo_badge": "rgba(196, 154, 108, 0.1)",
        },
        "tipografia": {
            "display": "Playfair Display",
            "sub_display": "Instrument Serif",
            "body": "General Sans",
            "mono": "JetBrains Mono",
            "contraste_estilistico": "Serif classico imponente com tracking -0.02em combinado a corpo sem serifa suico.",
        },
        "disposicao_icones": {
            "regra": "Substituicao de balancas e martelos cliches por monogramas geometricos vetoriais e marcadores de 12px com linhas hairline.",
            "estilo": "Linhas puras de 1px com acento bronze.",
        },
        "disposicao_textos": {
            "eyebrow": "AREA DE PRATICA &middot; JURISPRUDENCIA ESTRATEGICA (11px, tracking 0.2em).",
            "titulo": "Declaracoes de autoridade e teses juridicas com espacamento editorial.",
            "paragrafo": "Exposicao sóbria e direta, sem juridiques arcaico desnecessario.",
            "dados": "Valores de contencioso recuperados em numeros monumentais com casas decimais precisas.",
        },
        "cenografia_marca": [
            "Monograma heraldico minimalista vetorial SVG.",
            "Grid ortogonal com divisores de secao em hairline borders douradas sutis.",
        ]
    },

    "clinica_dermatologia_estetica": {
        "ramo": "Clinica Medica / Dermatologia & Estetica Avancada",
        "aliases": ["clinica", "dermatologia", "estetica", "medicina", "saude_luxo", "skin", "harmonizacao"],
        "filosofia_behance": "Erradicacao do ciano hospitalar frio e do rosa choque vulgar. Inspirado em estúdios de cosmecêutica suica e arquitetura biofilica.",
        "paleta_nao_obvia": {
            "bg_principal": "#f9f8f6",  # Linho mineral suave
            "bg_superficie": "#ffffff",  # Branco perola puro
            "texto_titulo": "#21201e",  # Grafite terra escuro
            "texto_corpo": "#6e6b66",  # Cinza pedra aquecido
            "acento_primario": "#bfa084",  # Areia dourada / Nude acetinado
            "acento_secundario": "#7a8a7c",  # Argila verde oliva serena
            "borda_hairline": "rgba(191, 160, 132, 0.25)",
            "selo_badge": "#f1ebe4",
        },
        "tipografia": {
            "display": "Fraunces",
            "body": "Satoshi",
            "mono": "JetBrains Mono",
            "contraste_estilistico": "Serif de alta costura com titulos suaves e macro-espacamento.",
        },
        "disposicao_icones": {
            "regra": "Icones delicados de 14px embutidos em pilulas arredondadas com fundo acetinado suave.",
            "estilo": "Tracos finos (stroke 1.2px) com cantos arredondados suaves.",
        },
        "disposicao_textos": {
            "eyebrow": "PROTOCOLO PERSONALIZADO &middot; MEDICINA INTEGRATIVA.",
            "titulo": "Afirmacoes de bem-estar e saude celular com elegancia natural.",
            "paragrafo": "Descricoes cientificas em tom calmo, transmitindo confianca e precisao.",
            "dados": "Tempo medio de recuperacao e satisfacao clinica auditada.",
        },
        "cenografia_marca": [
            "Fotografia com iluminacao natural suave e macro-foco de texturas de pele.",
            "Cards flutuantes com sombras organicas multicamadas (soft ambient glow).",
        ]
    },

    "barbearia_classica_craft": {
        "ramo": "Barbearia Tradicional / Cuidados Masculinos Premium",
        "aliases": ["barbearia", "barber", "cabelo_masculino", "barba", "pomada", "grooming"],
        "filosofia_behance": "Fuga do poste listrado americano e do desenho de caveira cliche. Inspirado na alfaiataria de Savile Row e carpintaria de noz-moscada.",
        "paleta_nao_obvia": {
            "bg_principal": "#0e0d0b",  # Nozes escuras e couro envelhecido
            "bg_superficie": "#171512",  # Carvalho defumado
            "texto_titulo": "#f1ece4",  # Espuma de barbear vintage / Marfim
            "texto_corpo": "#8c857b",  # Cinza cinzelado
            "acento_primario": "#c07a3e",  # Cobre de navalha e ambar
            "acento_secundario": "#4a2e1b",  # Tabaco curtido
            "borda_hairline": "rgba(192, 122, 62, 0.22)",
            "selo_badge": "rgba(192, 122, 62, 0.12)",
        },
        "tipografia": {
            "display": "Syne",
            "body": "DM Sans",
            "mono": "JetBrains Mono",
            "contraste_estilistico": "Display arrojado geometrico com detalhes tecnicos em mono.",
        },
        "disposicao_icones": {
            "regra": "Icones funcionais pequenos de tesoura, navalha ou toalha posicionados no topo direito dos cards de servico, com opacidade 80%.",
            "estilo": "Vetor afiado em cobre escovado.",
        },
        "disposicao_textos": {
            "eyebrow": "SERVICO MANUAL &middot; CORTE, TOALHA QUENTE & NAVALHA.",
            "titulo": "Titulos imponentes com corte reto e declaracao de pontualidade britanica.",
            "paragrafo": "Tempo de atendimento rigoroso e ritual descrito sem enrolacao.",
            "dados": "Preco e duracao em minutos destacados lado a lado.",
        },
        "cenografia_marca": [
            "Tabela de servicos com precificacao transparente e botao de agendamento imediato.",
            "Badges de profissionais com foto P&B de alto contraste e especialidade.",
        ]
    },

    "restaurante_gastronomia_afetiva": {
        "ramo": "Restaurante / Cozinha Autoral & Confort Food",
        "aliases": ["restaurante_autoral", "bistro", "culinaria", "massa", "trattoria", "empada_gourmet"],
        "filosofia_behance": "Evitar o vermelho ketchup e amarelo mostarda industriais. Inspirado em feiras organicas mediterrâneas e cadernos de receitas de família.",
        "paleta_nao_obvia": {
            "bg_principal": "#f7f5f0",  # Farinha de trigo artesanal
            "bg_superficie": "#ffffff",  # Ceramica branca esmaltada
            "texto_titulo": "#1b1814",  # Azeitona preta e ferro fundido
            "texto_corpo": "#5c554e",  # Cinza casca de pao
            "acento_primario": "#a8432a",  # Tomate seco defumado / Pomodoro rico
            "acento_secundario": "#385438",  # Manjericao fresco e azeite verde
            "borda_hairline": "rgba(168, 67, 42, 0.15)",
            "selo_badge": "#faeee8",
        },
        "tipografia": {
            "display": "Syne",
            "sub_display": "Fraunces",
            "body": "Plus Jakarta Sans",
            "mono": "JetBrains Mono",
            "contraste_estilistico": "Titulos expressivos que provocam apetite visual e corpo de leitura facil.",
        },
        "disposicao_icones": {
            "regra": "Icones de ingredientes (folha, chama, trigo, queijo) inline logo abaixo do nome do prato, indicando selos dieteticos.",
            "estilo": "Pequenos e discretos (14px), com cores semânticas suaves.",
        },
        "disposicao_textos": {
            "eyebrow": "FEITO DO ZERO &middot; FERMENTACAO NATURAL DE 48 HORAS.",
            "titulo": "Nomes de pratos destacados com precos em formato tabular limpo.",
            "paragrafo": "Listagem poetica dos ingredientes de origem e metodo de coccao.",
            "dados": "Tempo de preparo e rendimento das porcoes.",
        },
        "cenografia_marca": [
            "Menu bento grid com fotos macro apetitosas de crosta, queijo derretido e fumaca.",
            "Botao de pedido rapido flutuante no WhatsApp com selecao de pratos.",
        ]
    },

    "imobiliaria_incorporadora_design": {
        "ramo": "Incorporadora / Imoveis e Empreendimentos de Autor",
        "aliases": ["incorporadora", "lancamento_imovel", "apartamento_alto_padrao", "residencial"],
        "filosofia_behance": "Fuga do azul de corretora convencional. Inspiracao em publicacoes de arquitetura japonesa e brutalismo escandinavo.",
        "paleta_nao_obvia": {
            "bg_principal": "#101012",  # Grafite basalto
            "bg_superficie": "#17171a",  # Concreto mineral escuro
            "texto_titulo": "#f0ede6",  # Travertino romano claro
            "texto_corpo": "#7a7772",  # Cinza cimento
            "acento_primario": "#d19a66",  # Madeira carvalho quente
            "acento_secundario": "#8f6b4a",  # Couro sela
            "borda_hairline": "rgba(209, 154, 102, 0.2)",
            "selo_badge": "rgba(209, 154, 102, 0.1)",
        },
        "tipografia": {
            "display": "Cabinet Grotesk",
            "body": "General Sans",
            "mono": "Space Grotesk",
            "contraste_estilistico": "Geometria milimetrica pura, sem ornamentos superfluos.",
        },
        "disposicao_icones": {
            "regra": "Icones tecnicos de metragem, suites, vagas e orientacao solar organizados em barra de dados horizontal sob a imagem do imovel.",
            "estilo": "Linhas puras ultrafinas de 14px em carvalho quente.",
        },
        "disposicao_textos": {
            "eyebrow": "BAIRRO NOBRE &middot; ARQUITETURA AUTORAL ASSINADA.",
            "titulo": "Metragens monumentais com enfase em espaco e iluminacao zenital.",
            "paragrafo": "Memorial descritivo sintetico com foco em isolamento acustico e lazer privativo.",
            "dados": "Area privativa em m2 com digitos grandes em Space Grotesk.",
        },
        "cenografia_marca": [
            "Render arquitetonico full-width com tratamento crepuscular (golden hour).",
            "Seletor de plantas interativo sem recarregar a tela.",
        ]
    }
}


def get_behance_intelligence_for_branch(query_or_branch: str) -> dict[str, Any]:
    """Recupera as diretrizes estéticas nao-obvias do Behance para o ramo solicitado."""
    cleaned = query_or_branch.lower().strip()
    
    # 1. Match direto
    if cleaned in COMMERCE_BRANCH_INTELLIGENCE:
        return COMMERCE_BRANCH_INTELLIGENCE[cleaned]
        
    # 2. Match por alias
    for key, data in COMMERCE_BRANCH_INTELLIGENCE.items():
        if cleaned in data.get("aliases", []):
            return data
        for alias in data.get("aliases", []):
            if alias in cleaned:
                return data
                
    # Fallback refinado: Gastronomia Afetiva / Torrefacao Artesanal
    return COMMERCE_BRANCH_INTELLIGENCE["restaurante_gastronomia_afetiva"]
