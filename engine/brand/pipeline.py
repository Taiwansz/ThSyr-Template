"""
ThSyr Brand Strategy, Methodology and Conceptual Pipeline
Codifica a metodologia de design de identidade visual: 8 tipos de marca,
14 tecnicas visuais, catalogo de cliches setoriais e protocolo de refinamento optico.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

MARK_TYPES: Dict[str, Dict[str, Any]] = {
    "wordmark": {
        "name": "Wordmark (Logotipo tipografico)",
        "description": "Texto puro estilizado com intervencao geometrica nas letras.",
        "best_for": "Nomes curtos (<=7 letras), sonoros, novos no mercado precisando de reconhecimento de nome.",
        "avoid_when": "Nome muito longo ou generico.",
        "optical_rule": "Intervencao cirurgica em no maximo 1 ou 2 glifos; espacamento optico e compensacao de peso nas juncoes.",
    },
    "lettermark": {
        "name": "Lettermark / Monograma",
        "description": "Sigla de 2 a 4 letras interligadas ou estruturadas em bloco.",
        "best_for": "Organizacoes consolidadas ou com nomes longos/compostos.",
        "avoid_when": "Marcas novas sem orcamento de educacao de mercado.",
        "optical_rule": "Garantir legibilidade imediata das iniciais no teste squint/embaçado.",
    },
    "letterform": {
        "name": "Letterform (Monograma de letra unica)",
        "description": "Uma unica letra destilada em um simbolo autonomo funcional.",
        "best_for": "Apps móveis, plataformas digitais e favicons que precisam de impacto a 16px.",
        "avoid_when": "A letra nao tem diferenciacao na categoria.",
        "optical_rule": "Overshoot de 1 a 3% nas curvas; evitar que a letra pareca uma fonte padrao do sistema.",
    },
    "pictorial": {
        "name": "Pictorial (Simbolo figurativo)",
        "description": "Representacao estilizada e geometrica de um objeto real reconhecivel.",
        "best_for": "Marcas cujo nome e literal (ex: Apple, Target) ou que ancoram em metafora direta.",
        "avoid_when": "Servicos abstratos e difusos onde o objeto empobrece a proposta de valor.",
        "optical_rule": "Economia de ancoras: reduza o objeto ao menor numero de formas geometricas puras.",
    },
    "abstract": {
        "name": "Simbolo Abstrato",
        "description": "Forma geometrica nao-figurativa que evoca atributos emocionais ou conceituais.",
        "best_for": "Empresas com produtos multiplos, tecnologia profunda, infraestrutura.",
        "avoid_when": "Quando se torna uma forma generica amorfa sem tensao ou intencionalidade.",
        "optical_rule": "Equilibrio optico de massa; alinhamento a angulos limpos (0°, 45°, 90°).",
    },
    "mascot": {
        "name": "Mascote / Personagem",
        "description": "Figura antropomorfica ou criatura com personalidade expressiva.",
        "best_for": "Consumo de massa, publico infantil, games, comunidades e marcas sociais.",
        "avoid_when": "Marcas B2B austeras, financas institucionais, advocacia.",
        "optical_rule": "Criar versao simplificada de alto contraste para reproducao em tamanhos microscopicos.",
    },
    "emblem": {
        "name": "Emblema / Selo",
        "description": "Texto e simbolo encapsulados dentro de uma moldura geometrica (escudo, crista, circulo).",
        "best_for": "Educacao, clubes esportivos, automotivo tradicional, cervejarias, heranca.",
        "avoid_when": "Interfaces digitais compactas onde o detalhamento interno colapsa em mancha.",
        "optical_rule": "Espessuras minimas de traco para nao fechar no teste de reducao a 24px.",
    },
    "combination": {
        "name": "Marca Combinada (Lockup Simbolo + Texto)",
        "description": "Simbolo independente acoplado a um wordmark estruturado.",
        "best_for": "Padrao industrial moderno: maxima versatilidade para avatares e headers.",
        "avoid_when": "Simbolo e texto competem por atencao em vez de se complementarem.",
        "optical_rule": "Hierarquia clara: o simbolo define o ritmo e a altura do wordmark.",
    },
}

VISUAL_TECHNIQUES: Dict[str, Dict[str, str]] = {
    "negative-space": {
        "name": "Espaco Negativo",
        "description": "Uma segunda figura esculpida no espaco vazio entre os elementos.",
        "effect": "Recompensa visual e memorabilidade instantanea.",
    },
    "geometric-construction": {
        "name": "Construcao Geometrica Rigorosa",
        "description": "Uso exclusivo de arcos circulares, angulos puros e proporcoes matematicas.",
        "effect": "Sensacao de ordem, precisao de engenharia e atemporalidade.",
    },
    "letter-substitution": {
        "name": "Substituicao de Glifo",
        "description": "Uma das letras do wordmark e sutilmente modificada para atuar como simbolo.",
        "effect": "Unidade organica entre nome e icone.",
    },
    "duality-interlock": {
        "name": "Intertravamento e Dualidade",
        "description": "Dois conceitos ou formas que se encaixam como engrenagens ou no de fita.",
        "effect": "Parceria, conexao, seguranca e convergencia.",
    },
    "continuous-line": {
        "name": "Linha Continua / Monoline",
        "description": "Traco com espessura constante que percorre a figura sem interrupcao.",
        "effect": "Fluidez, elegancia moderna e clareza estrutural.",
    },
    "gestalt-closure": {
        "name": "Fechamento Gestaltico",
        "description": "Formas incompletas que o cerebro humano completa automaticamente.",
        "effect": "Engajamento cognitivo profundo do observador.",
    },
    "modular-system": {
        "name": "Sistema Modular / Grid de Celulas",
        "description": "Elementos identicos repetidos em escala ou rotacao controlada.",
        "effect": "Escalabilidade, arquitetura de sistemas e robustez.",
    },
    "chiral-symmetry": {
        "name": "Simetria Quiral / Rotacional",
        "description": "Simetria baseada em rotacoes ao redor de um eixo central com dinamismo.",
        "effect": "Movimento continuo e estabilidade dinamica.",
    },
}

INDUSTRY_CLICHES: Dict[str, Dict[str, Any]] = {
    "fintech": {
        "cliches": ["seta verde para cima", "escudo azul", "globo de redes", "circulos concentricos genericos"],
        "antidote": "Linhas sobrias, ancoras tipograficas pesadas, espaco negativo cirurgico e paletas proprietarias (evitar azul tech padrao).",
    },
    "developer-tools": {
        "cliches": ["brackets < / >", "prompt terminal $", "no de grafo com tres pontos", "cubo isometrico roxo"],
        "antidote": "Formas monoliticas de alta densidade, geometria de corte limpo, precisao de hardware.",
    },
    "health-biotech": {
        "cliches": ["cruz medica verde/azul", "folha verde saindo de gota", "dupla helice de DNA generica", "silhueta humana com bracos abertos"],
        "antidote": "Micro-geometrias rigorosas, tipografia de alta legibilidade, cores com peso mineral e biologico real.",
    },
    "food-cafe": {
        "cliches": ["xicara de cafe com fumaca", "grao de cafe estilizado", "garfo e faca cruzados", "circulo carimbo artesanal"],
        "antidote": "Geometrias abstratas de calor, marca nominativa autoral, monogramas austeros de heranca.",
    },
    "law-consulting": {
        "cliches": ["balanca da justica", "coluna grega", "escudo heraldico", "pena de escrever"],
        "antidote": "Wordmarks refinados com proporcoes editoriais e modais de serifas de transicao.",
    },
}

OPTICAL_REFINEMENT_RULES: List[Dict[str, str]] = [
    {
        "rule": "Overshoot Circular (1% a 3%)",
        "explanation": "Formas circulares e pontiagudas parecem menores que retangulos de mesma altura. Devem ultrapassar as linhas de guia.",
    },
    {
        "rule": "Compensacao do 'Efeito Osso' (Bone Effect)",
        "explanation": "Retangulos com cantos excessivamente arredondados afundam visualmente no meio. Usar curvaturas com transicao de Bézier continua.",
    },
    {
        "rule": "Alívio em Juncoes e Tracos Horizontais",
        "explanation": "Tracos horizontais parecem mais grossos que verticais; reduzir espessura horizontal em ~5-10% e afinar juncoes em V para evitar manchas de tinta.",
    },
    {
        "rule": "Centro Optico vs Centro Geometrico",
        "explanation": "O olho percebe o centro de massa ligeiramente acima do centro matematico (deslocar ~2% a 4% para cima).",
    },
    {
        "rule": "Teste de Inversao Monocromatica",
        "explanation": "Marcas brancas em fundo escuro irradiam luz e parecem mais pesadas. A versao reversa precisa ter tracos ligeiramente afinados.",
    },
    {
        "rule": "Teste dos 16 Pixels (Shelf & Favicon Test)",
        "explanation": "A ideia essencial da marca DEVE ser legivel e reconhecivel em 16x16 pixels sem colapsar em ruido.",
    },
]


@dataclass
class DesignBrief:
    brand_name: str
    industry: str
    adjectives: List[str]
    offering: str
    promise: str
    cliches_to_avoid: List[str]
    antidote: str
    recommended_mark_types: List[str]
    recommended_techniques: List[str]
    word_map_nouns: List[str]
    word_map_metaphors: List[str]

    def render_markdown(self) -> str:
        lines = [
            f"# Design Brief Estruturado — {self.brand_name}",
            "",
            f"**Industria / Categoria:** {self.industry}",
            f"**Oferta:** {self.offering}",
            f"**Promessa Nuclear:** {self.promise}",
            f"**Adjetivos Tonais:** {', '.join(self.adjectives)}",
            "",
            "## 1. Alerta Pre-Frontal de Cliches a Evitar",
            *(f"- PROIBIDO: {c}" for c in self.cliches_to_avoid),
            f"- **Antidoto:** {self.antidote}",
            "",
            "## 2. Tipos de Marca Recomendados",
            *(f"- **{MARK_TYPES[m]['name']}:** {MARK_TYPES[m]['best_for']}" for m in self.recommended_mark_types if m in MARK_TYPES),
            "",
            "## 3. Tecnicas Visuais Prioritarias",
            *(f"- **{VISUAL_TECHNIQUES[t]['name']}:** {VISUAL_TECHNIQUES[t]['description']}" for t in self.recommended_techniques if t in VISUAL_TECHNIQUES),
            "",
            "## 4. Mapa Semantico e Metáforas Construtivas",
            f"- **Substantivos:** {', '.join(self.word_map_nouns)}",
            f"- **Metaforas Visuais:** {', '.join(self.word_map_metaphors)}",
            "",
            "## 5. Regras Mandatorias de Refinamento Optico",
            *(f"- **{r['rule']}:** {r['explanation']}" for r in OPTICAL_REFINEMENT_RULES),
        ]
        return "\n".join(lines)


class BrandStrategyEngine:
    """Motor de orquestracao conceitual e analise de estrategia de marca."""

    def generate_brief(
        self,
        brand_name: str,
        industry: str,
        adjectives: Optional[List[str]] = None,
        offering: str = "",
        promise: str = "",
    ) -> DesignBrief:
        adj = adjectives or ["preciso", "atemporal", "robusto"]
        ind_key = industry.lower().replace(" ", "-")

        cliche_info = INDUSTRY_CLICHES.get(ind_key)
        if not cliche_info:
            for k, v in INDUSTRY_CLICHES.items():
                if k in ind_key or ind_key in k:
                    cliche_info = v
                    break

        cliches = cliche_info["cliches"] if cliche_info else ["gradiente amorfo sem intencionalidade", "simbolo generico sem relacao com o nome"]
        antidote = cliche_info["antidote"] if cliche_info else "Geometria disciplinada em preto e branco com ancoras solidas."

        # Recomendacao de mark type com base no tamanho do nome
        name_clean = brand_name.strip()
        rec_types = []
        if len(name_clean) <= 6:
            rec_types.extend(["wordmark", "letterform", "combination"])
        else:
            rec_types.extend(["combination", "abstract", "lettermark"])

        # Tecnicas visuais candidatas
        rec_techs = ["geometric-construction", "negative-space", "modular-system"]

        # Word map
        nouns = [name_clean, industry, "estrutura", "ancora", "modulo"]
        metaphors = ["solidez", "precisao de silicio", "tensao balanceada", "vetor limpo"]

        return DesignBrief(
            brand_name=brand_name,
            industry=industry,
            adjectives=adj,
            offering=offering or f"Solucao em {industry}",
            promise=promise or "Excelencia e distincao categorial",
            cliches_to_avoid=cliches,
            antidote=antidote,
            recommended_mark_types=rec_types,
            recommended_techniques=rec_techs,
            word_map_nouns=nouns,
            word_map_metaphors=metaphors,
        )
