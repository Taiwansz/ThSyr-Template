#!/usr/bin/env python3
"""
Broadsheet Newspaper Scaffolder CLI
Gera edições de jornais impressos históricos broadsheet em HTML/CSS estrito.
Totalmente agnóstico a nichos (política, economia, ciência, cultura, tecnologia).
Zero dependências externas frágeis e zero emojis.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
BOILERPLATE_PATH = TEMPLATES_DIR / "boilerplate_broadsheet.html"

ARCHETYPE_PRESETS = {
    "classic": {
        "title": "A Gazeta das Nações",
        "subtitle": "Órgão Diário e Independente da Opinião Pública, das Leis e dos Grandes Fatos",
        "latin_motto": "Veritas et Lux in Rebus Publicis",
        "location": "Lisboa & Rio de Janeiro",
        "price": "100 Réis",
        "weather": "Barômetro a 762 mm; Céu encoberto sobre o litoral; Ventos do Quadrante Sul.",
        "circulation": "Edição matutina com circulação expressa aos assinantes das províncias.",
        "lead_kicker": "Diplomacia & Comércio Internacional",
        "lead_headline": "Tratado de Navegação e Comércio é Ratificado em Sessão Solene",
        "lead_deck": "Representantes plenipotenciários concluem acordo aduaneiro após semanas de negociações árduas — Portos do Atlântico passam a operar sob a nova tarifa comercial unificada.",
        "lead_origin": "LONDRES, POR DESPACHO DIPLOMÁTICO",
        "lead_paragraphs": [
            "Chegaram a bom termo na tarde de ontem as exaustivas deliberações em torno do tratado geral de navegação costeira e tarifas consulares. O pacto, firmado perante os ministros de estado e os enviados extraordinários das potências aliadas, fixa em bases permanentes as franquias marítimas e assegura o livre trânsito de mercadorias manufaturadas e gêneros agrícolas de primeira necessidade.",
            "As controvérsias que ameaçavam a assinatura do documento diziam respeito aos direitos de ancoragem nos portos de escala e à reciprocidade de tratamento para as tripulações mercantes. Graças à intervenção do chanceler de negócios estrangeiros, prevaleceu a tese do equilíbrio tarifário recíproco, afastando o risco de retaliações aduaneiras.",
            "Nos termos do artigo sétimo, todas as embarcações com pavilhão regular gozarão das mesmas prerrogativas concedidas aos navios nacionais no que tange ao abastecimento de carvão, reparos de caldeiras e descarga de armazéns alfandegários. Os armadores da praça comercial manifestaram incontida satisfação perante a medida.",
            "A nova ordem fiscal entrará em vigor a partir do primeiro dia do próximo mês, cabendo às inspetorias de alfândega a publicação imediata das tabelas discriminadas de taxas e selos para conhecimento dos capitães e negociantes marítimos."
        ],
        "secondary_kicker": "Ordem Pública & Justiça",
        "secondary_headline": "Conselho de Estado Delibera sobre a Reforma Administrativa",
        "secondary_origin": "RIO DE JANEIRO, CORRESPONDÊNCIA PARTICULAR",
        "secondary_paragraphs": [
            "Reunido extraordinariamente no palácio ministerial, o Conselho de Estado apreciou o projeto de reorganização dos quadros burocráticos civis. A reforma visa coibir os atrasos nos despachos de requerimentos e uniformizar a arrecadação de emolumentos judiciais nas comarcas do interior.",
            "O relator da comissão enfatizou a necessidade de prestação rigorosa de contas por parte dos escrivães e coletores gerais, determinando inspeções trimestrais nas tesourarias distritais.",
            "O texto final subirá à sansão governamental no início da próxima quinzena, prevendo a extinção imediata de cargos ociosos criados sob regimes anteriores."
        ],
        "wires": [
            ("Paris, Pelo Telégrafo", "Chegada da Missão Científica", "A comissão de geógrafos e astrônomos retornou após dez meses de medições meridianas na África Equatorial. Os mapas e cadernos de observação serão apresentados à Academia."),
            ("Berlim, Por Cabo Submarino", "Acordo Postal Continental", "Foi firmado o protocolo de intercâmbio direto de malas postais terrestres com a Europa Central, reduzindo em quatro dias o trânsito de cartas ordinárias."),
            ("Washington, Via Veleiro Correio", "Abertura dos Canais Fluviais", "O congresso autorizou a dragagem dos trechos rochosos do rio principal, permitindo a passagem de vapores de grande calado até os entrepostos do oeste.")
        ],
        "table_title": "Cotações do Câmbio & Títulos Públicos",
        "table_cols": ("Discriminação", "Praça", "Fechamento"),
        "table_rows": [
            ("Apólices Gerais do Tesouro", "Nacional", "98 1/2"),
            ("Letras de Câmbio sobre Londres", "90 d/v", "27 1/4 d."),
            ("Francos Franceses (Papel)", "À vista", "380 Rs."),
            ("Ouro em Barra (Grama)", "Oficial", "4$200 Rs.")
        ],
        "essay_kicker": "Ensaio Político",
        "essay_title": "Dos Limites do Poder Moderador na Ordem Jurídica",
        "essay_paragraphs": [
            "A harmonia entre os poderes do Estado não pode repousar sobre o arbítrio de conveniências passageiras, mas sim sobre a firmeza dogmática dos preceitos constitucionais. Quando o legislador vacila diante das pressões facciosas, cumpre à magistratura zelar pela integridade do pacto federativo.",
            "Não há soberania legítima que possa subsistir sem a submissão voluntária de todos os cidadãos e governantes à impessoalidade da lei escrita."
        ],
        "chronicle_kicker": "Tribuna & Crônica",
        "chronicle_title": "O Movimento da Cidade e a Chegada dos Vapores",
        "chronicle_paragraph": "O cais do porto amanheceu ontem com incomum agitação decorrente da chegada do vapor transatlântico vindo de Southampton. Foram descarregadas caixas de maquinário têxtil, vinhos da Borgonha e fardos de papel impresso para as tipografias da capital."
    },
    "financial": {
        "title": "A Gazeta Mercantil & Financeira",
        "subtitle": "Registro Diário dos Mercados Globais, Crédito Bancário, Câmbio e Mercadorias",
        "latin_motto": "Pacta Sunt Servanda et Fides Publica",
        "location": "Londres, Nova York & São Paulo",
        "price": "2 Pence / 50 Centavos",
        "weather": "Clima de Negócios: Alta de liquidez bancária; Taxa de desconto em 4.5%.",
        "circulation": "Distribuído diariamente aos balcões de bancos, corretores de câmbio e armazéns gerais.",
        "lead_kicker": "Mercados & Política Monetária",
        "lead_headline": "Banco Central Eleva Taxa de Redesconto para Proteger Reservas Metálicas",
        "lead_deck": "Autoridade monetária atua para conter a evasão de divisas e estabilizar a cotação cambial — Operações de crédito comercial registram retração imediata na praça financeira.",
        "lead_origin": "CIDADE DE LONDRES, BALCÃO DA DÍVIDA",
        "lead_paragraphs": [
            "Em deliberação extraordinária concluída na abertura dos mercados desta manhã, o comitê diretivo do Banco Central determinou a elevação da taxa básica de redesconto em meio ponto percentual. A medida emergencial responde à pressão exercida pela saída de lingotes de ouro para o mercado transatlântico e visa assegurar o lastro das emissões fiduciárias em circulação.",
            "Os diretores das principais casas bancárias acolheram a decisão com serenidade, destacando que a estabilidade do padrão monetário é precondição indispensável para a manutenção dos contratos de longo prazo e para o financiamento das colheitas de exportação.",
            "O volume de transações na bolsa de títulos registrou forte oscilação nas primeiras horas de pregão. Os papéis da dívida consolidada recuaram ligeiramente em seus preços nominais, enquanto os depósitos a prazo fixo observaram um influxo expressivo de capitais à procura de remuneração garantida.",
            "Representantes da associação de comércio alertaram, contudo, que a restrição do crédito para desconto de duplicatas poderá desacelerar as encomendas da indústria manufatureira ao longo do próximo trimestre."
        ],
        "secondary_kicker": "Comércio Exterior & Safras",
        "secondary_headline": "Exportações de Café e Grãos Superam Estimativas da Alfândega",
        "secondary_origin": "PORTO DE SANTOS, DESPACHO ALFANDEGÁRIO",
        "secondary_paragraphs": [
            "Os relatórios oficiais de embarque referentes ao último mês confirmam um acréscimo de doze por cento no volume de sacas descarregadas nos armazéns reguladores. A demanda firme dos entrepostos europeus e norte-americanos garantiu a sustentação dos preços médios nos contratos futuros.",
            "As companhias de navegação a vapor já contrataram transporte extraordinário para dar vazão à safra que desce pelas linhas férreas do interior, operando com lotação máxima nos terminais de atracação.",
            "Os estoques reguladores permanecem em níveis confortáveis, garantindo o abastecimento doméstico sem sobressaltos inflacionários."
        ],
        "wires": [
            ("Nova York, Wall Street", "Índices Industriais em Equilíbrio", "As cotações das ferrovias e das siderúrgicas encerraram o dia com ligeiro ganho, amparadas pela publicação de lucros operacionais superiores às projeções."),
            ("Paris, Bolsa de Valores", "Demanda por Empréstimos Russos", "A nova emissão de títulos garantidos para obras de infraestrutura ferroviária obteve subscrição integral em menos de três horas de chamada de capital."),
            ("Buenos Aires, Mercado de Cereais", "Fretes Marítimos em Elevação", "A escassez de navios graneleiros na bacia do Prata provocou acréscimo de cinco centavos por tonelada transportada até os portos do canal da Mancha.")
        ],
        "table_title": "Índice de Commodities & Moedas Globais",
        "table_cols": ("Mercadoria / Ativo", "Unidade", "Preço Médio"),
        "table_rows": [
            ("Café Especial (Tipo 4)", "Saca 60kg", "145$000 Rs."),
            ("Algodão em Pluma", "Arroba", "38$500 Rs."),
            ("Trigo Argentino", "Tonelada", "£ 8 10s."),
            ("Libra Esterlina", "Câmbio", "4.86 USD")
        ],
        "essay_kicker": "Análise Financeira",
        "essay_title": "A Dinâmica do Crédito e o Risco de Saturacão Bancária",
        "essay_paragraphs": [
            "A expansão desmedida dos adiantamentos sobre títulos sem a correspondente contrapartida em depósitos genuínos constitui o gérmen clássico de todas as crises de liquidez. O papel do banqueiro não é inflar balanços artificiais, mas dosar com precisão cirúrgica a velocidade do meio circulante.",
            "A disciplina do capital exige prudência no presente para afastar as insolvências do amanhã."
        ],
        "chronicle_kicker": "Balcão dos Negócios",
        "chronicle_title": "Constituição de Nova Companhia de Estradas de Ferro",
        "chronicle_paragraph": "Foi registrada no cartório comercial a ata de fundação da Empresa Ferroviária Central, com capital autorizado integralizado por capitais locais e empréstimos londrinos. As obras do leito dos trilhos terão início no próximo mês."
    },
    "scientific": {
        "title": "O Registro Científico & Filosófico",
        "subtitle": "Anais da Sociedade das Ciências Naturais, Medicina Experimental e Astronomia",
        "latin_motto": "Scientia Potentia Est in Rerum Natura",
        "location": "Paris, Berlim & Coimbra",
        "price": "1 Franco / 200 Réis",
        "weather": "Observatório Astronômico: Visibilidade límpida; Barômetro em 760 mm; Temperatura média 16°C.",
        "circulation": "Edição quinzenal arquivada nas bibliotecas de universidades e laboratórios acadêmicos.",
        "lead_kicker": "Física Experimental & Radiação",
        "lead_headline": "Ensaios Laboratoriais Revelam Propriedades Inéditas da Matéria Radiante",
        "lead_deck": "Pesquisadores isolam novos compostos e registram fenômenos de emissão luminosa em tubos de vácuo profundo — Comunidade acadêmica debate a teoria da estrutura atômica.",
        "lead_origin": "UNIVERSIDADE DE PARIS, LABORATÓRIO DE QUÍMICA",
        "lead_paragraphs": [
            "Apresentou-se ontem perante a sessão plenária da Academia de Ciências a memória descritiva dos ensaios de fracionamento de minerais e precipitação química realizados nos últimos doze meses. Os resultados comprovam a existência de uma atividade energética espontânea e contínua em certos sais pesados, incapaz de ser explicada pelas leis convencionais da termodinâmica clássica.",
            "Os experimentos, conduzidos com eletrômetros de alta precisão e chapas fotográficas seladas em invólucros opacos de chumbo, demonstraram que as radiações emitidas atravessam lâminas delgadas de alumínio e provocam a ionização imediata do ar circundante.",
            "O decano da faculdade de física interveio no debate para destacar que os dados empíricos colocam em xeque o dogma da indivisibilidade do átomo material, sugerindo que as partículas elementares comportam arranjos internos de extraordinária complexidade eletromagnética.",
            "Uma comissão especial de químicos e matemáticos foi constituída para reproduzir as medições em aparelhos calibrados de calorimetria e fixar a massa atômica exata do novo elemento nos compêndios internacionais."
        ],
        "secondary_kicker": "Medicina & Patologia Celular",
        "secondary_headline": "Inoculação Preventiva Reduz a Mortalidade Hospitalar",
        "secondary_origin": "BERLIM, INSTITUTO DE PATOLOGIA",
        "secondary_paragraphs": [
            "Os relatórios clínicos das enfermarias de isolamento confirmam o êxito do protocolo de esterilização química dos instrumentos cirúrgicos e a administração de soros terapêuticos. As infecções pós-operatórias caíram para menos de quatro por cento dos casos atendidos.",
            "O diretor clínico ressaltou que a assepsia rigorosa das mãos e a desinfecção ambiental com ácido carbólico constituem dever inafastável da prática médica contemporânea.",
            "Os ensaios com culturas de micro-organismos atenuados abrem caminho para a proteção sistemática das populações urbanas contra epidemias contagiosas."
        ],
        "wires": [
            ("Observatório de Greenwich", "Observação de Nova Nebulosa Espiral", "O telescópio refrator de trinta polegadas captou variações luminosas regulares na constelação de Andrômeda, sugerindo distâncias que extrapolam a Via Láctea."),
            ("Universidade de Cambridge", "Teoria Cinética dos Gases", "O departamento de matemática aplicada publicou equações determinísticas que modelam a distribuição de velocidades moleculares sob variações extremas de pressão."),
            ("Viena, Sociedade Biológica", "Hereditariedade em Culturas Botânicas", "Experimentos botânicos com hibridação de leguminosas confirmam proporções matemáticas estritas na transmissão de características anatômicas através das gerações.")
        ],
        "table_title": "Tabela Periódica das Constantes e Massas Experimentais",
        "table_cols": ("Elemento / Constante", "Símbolo", "Valor Medido"),
        "table_rows": [
            ("Velocidade da Luz no Vácuo", "c", "299.792 km/s"),
            ("Equivalente Mecânico do Calor", "J", "4.184 J/cal"),
            ("Massa Atômica do Hidrogênio", "H", "1.008 u"),
            ("Pressão Atmosférica Normal", "P_0", "1.01325 bar")
        ],
        "essay_kicker": "Epistemologia Científica",
        "essay_title": "Da Primazia do Fato Empírico sobre a Especulação Metafísica",
        "essay_paragraphs": [
            "A ciência não avança por meio de silogismos abstratos tecidos em gabinetes isolados, mas pela confrontação severa e impiedosa de hipóteses contra o dado empírico mensurável. Uma teoria elegante que falhe perante um único experimento controlado não passa de poesia geométrica sem valor preditivo.",
            "O dever do cientista é a humildade absoluta diante da realidade fenomênica revelada pelo laboratório."
        ],
        "chronicle_kicker": "Registro de Invenções",
        "chronicle_title": "Depósito de Patente de Microscópio Binocular de Imersão",
        "chronicle_paragraph": "A fábrica de instrumentos ópticos de Jena depositou o memorial descritivo de um novo sistema de lentes acromáticas de fluorita, permitindo ampliações óticas de até duas mil vezes sem aberração cromática periférica."
    },
    "cultural": {
        "title": "A Tribuna das Belas-Artes & Letras",
        "subtitle": "Crítica Literária, Filosofia Moral, Teatro, Poética e Movimento das Ideias",
        "latin_motto": "Ars Longa, Vita Brevis in Aeternum",
        "location": "Paris, Coimbra & Rio de Janeiro",
        "price": "80 Réis / 50 Cêntimos",
        "weather": "Temporada Cultural: Abertura do Salão Anual de Belas-Artes e Ensaios da Temporada Lírica.",
        "circulation": "Leitura obrigatória nos círculos acadêmicos, livrarias e clubes literários.",
        "lead_kicker": "Literatura & Movimento das Letras",
        "lead_headline": "Publicação de Romance Monumental Provoca Intenso Debate Crítico",
        "lead_deck": "Nova obra literária rompe com os cânones do romantismo convencional e inaugura o realismo psicológico na prosa vernácula — Críticos dividem-se entre o espanto moral e a aclamação estética.",
        "lead_origin": "RIO DE JANEIRO, SALÃO DAS LETRAS",
        "lead_paragraphs": [
            "Apareceu ontem nas vitrines das principais livrarias da Rua do Ouvidor o novo volume em prosa que vinha despertando viva curiosidade nos círculos intelectuais. Trata-se de uma narrativa implacável que disseca as convenções sociais, as ilusões da vaidade humana e os compromissos hipócritas das classes letradas com uma sobriedade de estilo até então desconhecida no idioma.",
            "O autor, valendo-se de uma ironia sutil e de um narrador que examina as misérias do caráter com a impassibilidade de um anatomista dissecando tecidos inertes, renunciou deliberadamente aos arroubos sentimentais e aos finais redentores que caracterizavam a literatura de folhetim.",
            "Na tertúlia matutina do Grêmio Literário, os críticos tradicionalistas ergueram protestos contra o que chamaram de 'frieza perturbadora e ceticismo corrosivo', enquanto a mocidade acadêmica saudou o livro como a maioridade definitiva da literatura nacional.",
            "O livreiro-editor anunciou que a primeira tiragem de três mil exemplares encontra-se praticamente esgotada, estando as prensas da oficina tipográfica já preparadas para a impressão imediata de uma segunda edição com prefácio explicativo."
        ],
        "secondary_kicker": "Artes Plásticas & Salão Oficial",
        "secondary_headline": "Abertura da Exposição de Pintura e Escultura Histórica",
        "secondary_origin": "PARIS, SALÃO DOS CAMPOS ELÍSEOS",
        "secondary_paragraphs": [
            "O Salão Anual abriu suas portas apresentando mais de quinhentas telas e bronzes de mestres consagrados e novos talentos. Destaca-se a grande tela histórica retratando a defesa do parlamento contra as invasões absolutistas, elogiada pelo tratamento magistral do chiaroscuro.",
            "Os críticos notaram uma progressiva libertação da pincelada acadêmica rígida em favor de impressões luminosas mais atmosféricas e espontâneas captadas ao ar livre.",
            "As medalhas de honra serão outorgadas pelo júri oficial no encerramento da semana, sob a presidência do diretor da Escola de Belas-Artes."
        ],
        "wires": [
            ("Florença, Do Nosso Correspondente", "Restauração de Afrescos Renascentistas", "A oficina do mestre restaurador concluiu a limpeza química dos painéis do século XIV, revelando pigmentos de azul ultramarino e ouro brunido perfeitamente conservados."),
            ("Lisboa, Grêmio de Letras", "Conferência sobre a Poética Camoniana", "O professor de literatura proferiu conferência memorável demonstrando a métrica decassilábica e a arquitetura épica como ápice da língua portuguesa clássica."),
            ("Milão, Teatro Alla Scala", "Estreia Triunfal da Nova Ópera Lírica", "A récita inaugural da partitura dramática obteve vinte e duas chamadas de cortina para o compositor e solistas, com aclamação unânime da plateia.")
        ],
        "table_title": "Índice de Obras Raras & Leilões Bibliográficos",
        "table_cols": ("Edição / Autor", "Ano", "Último Lance"),
        "table_rows": [
            ("Os Lusíadas (Edição dos Piscos)", "1572", "1:200$000 Rs."),
            ("Ensaios de Michel de Montaigne", "1595", "450$000 Rs."),
            ("A Divina Comédia (Aldina em 8º)", "1515", "820$000 Rs."),
            ("Dicionário de Bluteau (8 vols)", "1712", "300$000 Rs.")
        ],
        "essay_kicker": "Estética Literária",
        "essay_title": "Da Necessidade do Desdém pela Vulgaridade Comercial nas Letras",
        "essay_paragraphs": [
            "A arte que procura comprazer o gosto rasteiro da multidão assina de antemão a própria certidão de óbito estético. A missão do escritor não é acalentar os preconceitos do seu tempo com fábulas amenas, mas erguer um monumento verbal dotado de peso, concisão e densidade metafísica duradoura.",
            "As modas dos séculos passam como folhas de outono; a palavra esculpida com rigor clássico permanece inalterada nas pedras da história."
        ],
        "chronicle_kicker": "Crônica Urbana",
        "chronicle_title": "Os Cafés da Rua Direita e as Controvérsias da Tarde",
        "chronicle_paragraph": "Às cinco da tarde, quando as brisas do crepúsculo dissipam o mormaço da praça, os diplomatas, advogados e jornalistas congregam-se sob os toldos dos cafés para comentar as notícias trazidas pelos correios marítimos e as últimas diatribes parlamentares."
    },
    "tech": {
        "title": "A Gazeta Tecnológica & Mecânica",
        "subtitle": "Registro Oficial de Invenções, Patentes, Eletricidade, Semicondutores e Máquinas",
        "latin_motto": "Mens Agitat Molem in Structura Machinae",
        "location": "Manchester, Vale do Silício & São Paulo",
        "price": "50 Centavos / 100 Réis",
        "weather": "Oficinas Mecânicas: Redes fabris em plena carga; Barômetro em 764 mm; Fornos siderúrgicos operando a 1.200°C.",
        "circulation": "Boletim técnico lido por engenheiros, projetistas de sistemas e mestres de forja.",
        "lead_kicker": "Litografia & Microarquitetura de Silício",
        "lead_headline": "Novo Processo Litográfico Alcança Precisão Sub-Nanométrica na Forja de Chips",
        "lead_deck": "Prensas de radiação ultravioleta extrema viabilizam a deposição de dezenas de bilhões de transistores por pastilha — Indústria de processadores supera o gargalo térmico de miniaturização.",
        "lead_origin": "EINDHOVEN, DESPACHO DA ENGENHARIA",
        "lead_paragraphs": [
            "Foi homologado perante o consórcio internacional de fundições o primeiro sistema industrial de litografia óptica operando em comprimento de onda ultravioleta extremo de alta abertura numérica. O equipamento, dotado de espelhos refletores lapidados com tolerância de frações atômicas e resfriamento criogênico contínuo, permite gravar circuitos condutores de apenas dois nanômetros sobre lâminas circulares de silício monocristalino.",
            "Os ensaios demonstraram que as novas matrizes de computação reduzem a dissipação térmica em trinta e cinco por cento por operação de ponto flutuante, viabilizando o processamento de modelos neurais maciços sem colapso energético das centrais de cálculo.",
            "O diretor técnico da corporação de semicondutores enfatizou que o projeto exigiu a substituição completa dos sistemas de transporte a laser e a introdução de câmaras de vácuo purificado contra contaminação por partículas de poeira.",
            "As primeiras remessas de circuitos integrados forjados sob o novo padrão deverão ser despachadas aos fabricantes de servidores nas próximas seis semanas, alterando a correlação de forças na infraestrutura computacional planetária."
        ],
        "secondary_kicker": "Compiladores & Engenharia de Software",
        "secondary_headline": "Pipeline de Compilação Adota Representações Intermediárias SSA",
        "secondary_origin": "VALE DO SILÍCIO, CENTRO DE ARQUITETURA",
        "secondary_paragraphs": [
            "A nova especificação do compilador de sistemas introduziu formalmente o algoritmo de alocação de registradores baseado em coloração de grafos de Chaitin-Briggs e eliminação agressiva de redundâncias globais. Os testes de benchmarking evidenciaram ganhos de vinte e oito por cento na taxa de execução de laços aninhados.",
            "Os projetistas destacaram que a transformação do código fonte para a forma SSA com nós phi garante a integridade formal da análise de fluxo de controle, impedindo vazamentos de memória e falhas de segmentação em tempo de execução.",
            "A suíte completa de testes de regressão automatizados obteve conformidade estrita de cem por cento, homologando a infraestrutura para sistemas de missão crítica."
        ],
        "wires": [
            ("Tóquio, Laboratório de Materiais", "Supercondutividade em Alta Pressão", "Equipe de metalurgistas registrou resistividade nula em ligas de hidreto de lantânio sob confinamento mecânico de bigornas de diamante."),
            ("Zurique, Instituto de Redes", "Roteamento em Malhas de Baixa Latência", "Novo protocolo de comutação assíncrona reduz a latência de cauda p99 em aglomerados distribuídos de servidores para menos de quatrocentos microssegundos."),
            ("Detroit, Usina de Força", "Geradores Turbocompressores a Vapor", "A central elétrica instalou turbinas axiais de duplo estágio capazes de fornecer quarenta megawatts contínuos às linhas fabris pesadas.")
        ],
        "table_title": "Telemetria de Desempenho & Parâmetros de Silício",
        "table_cols": ("Arquitetura / Parâmetro", "Norma", "Métrica de Bancada"),
        "table_rows": [
            ("Densidade de Transistores", "MTr/mm²", "285.4 MTr"),
            ("Frequência de Relógio Base", "GHz", "4.85 GHz"),
            ("Consumo Energético (TDP)", "Watts", "125 W"),
            ("Latência de Cache L3", "Ciclos", "14 ns")
        ],
        "essay_kicker": "Doutrina de Engenharia",
        "essay_title": "Da Lei de Amdahl à Barreira Térmica da Computação Moderna",
        "essay_paragraphs": [
            "Nenhuma abstração de software de alto nível pode contornar as leis imutáveis da física da matéria condensada. Quando a capacitância parasita das linhas de cobre e a corrente de fuga dos transistores impõem um limite intransponível ao relógio de ciclo, a única salvação do engenheiro reside no paralelismo estruturado e na pureza da especialização mecânica de hardware.",
            "O desperdício de instruções por camadas excessivas de frameworks abstratos é a maior traição ao trabalho do projetista de circuitos."
        ],
        "chronicle_kicker": "Boletim da Oficina",
        "chronicle_title": "Registro de Patente de Transistor de Porta Envolvente (GAA)",
        "chronicle_paragraph": "O escritório de propriedade industrial concedeu a carta patente da nova geometria tridimensional de nanoribbons de silício empilhados, assegurando o controle eletrostático completo do canal de condução contra o tunelamento quântico."
    }
}


def build_table_rows_html(rows: list[tuple[str, str, str]]) -> str:
    html_lines = []
    for col1, col2, col3 in rows:
        html_lines.append(
            f"              <tr>\n"
            f"                <td>{col1}</td>\n"
            f"                <td>{col2}</td>\n"
            f"                <td class=\"num\">{col3}</td>\n"
            f"              </tr>"
        )
    return "\n".join(html_lines)


def generate_newspaper_html(
    archetype: str = "classic",
    title: str | None = None,
    subtitle: str | None = None,
    latin_motto: str | None = None,
    location: str | None = None,
    date_str: str | None = None,
    volume: str = "XLVIII",
    edition: str = "17.432",
    price: str | None = None,
    lead_headline: str | None = None,
    lead_deck: str | None = None,
) -> str:
    """Gera o código HTML completo da edição broadsheet a partir do template canônico."""
    if archetype not in ARCHETYPE_PRESETS:
        archetype = "classic"

    preset = ARCHETYPE_PRESETS[archetype]

    # Resolver data por extenso em portugues
    if not date_str:
        now = datetime.now()
        meses = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]
        dias_semana = [
            "Segunda-feira", "Terça-feira", "Quarta-feira",
            "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"
        ]
        dia_sem = dias_semana[now.weekday()]
        mes_nome = meses[now.month - 1]
        date_str = f"{dia_sem}, {now.day} de {mes_nome} de {now.year}"

    # Ler boilerplate
    if not BOILERPLATE_PATH.is_file():
        raise FileNotFoundError(f"Template não encontrado em: {BOILERPLATE_PATH}")

    template_content = BOILERPLATE_PATH.read_text(encoding="utf-8")

    # Mapear variáveis
    replacements = {
        'data-archetype="classic"': f'data-archetype="{archetype}"',
        "{{NEWSPAPER_TITLE}}": title or preset["title"],
        "{{NEWSPAPER_SUBTITLE}}": subtitle or preset["subtitle"],
        "{{LATIN_MOTTO}}": latin_motto or preset["latin_motto"],
        "{{PUBLICATION_LOCATION}}": location or preset["location"],
        "{{EDITION_DATE}}": date_str,
        "{{VOLUME_NUMBER}}": volume,
        "{{EDITION_NUMBER}}": edition,
        "{{ISSUE_PRICE}}": price or preset["price"],
        "{{WEATHER_REPORT}}": preset["weather"],
        "{{CIRCULATION_NOTICE}}": preset["circulation"],
        "{{LEAD_KICKER}}": preset["lead_kicker"],
        "{{LEAD_HEADLINE}}": lead_headline or preset["lead_headline"],
        "{{LEAD_DECK}}": lead_deck or preset["lead_deck"],
        "{{LEAD_ORIGIN}}": preset["lead_origin"],
        "{{LEAD_PARAGRAPH_1}}": preset["lead_paragraphs"][0],
        "{{LEAD_PARAGRAPH_2}}": preset["lead_paragraphs"][1],
        "{{LEAD_PARAGRAPH_3}}": preset["lead_paragraphs"][2],
        "{{LEAD_PARAGRAPH_4}}": preset["lead_paragraphs"][3],
        "{{SECONDARY_KICKER}}": preset["secondary_kicker"],
        "{{SECONDARY_HEADLINE}}": preset["secondary_headline"],
        "{{SECONDARY_ORIGIN}}": preset["secondary_origin"],
        "{{SECONDARY_PARAGRAPH_1}}": preset["secondary_paragraphs"][0],
        "{{SECONDARY_PARAGRAPH_2}}": preset["secondary_paragraphs"][1],
        "{{SECONDARY_PARAGRAPH_3}}": preset["secondary_paragraphs"][2],
        "{{WIRE_1_TITLE}}": preset["wires"][0][1],
        "{{WIRE_1_ORIGIN}}": preset["wires"][0][0],
        "{{WIRE_1_BODY}}": preset["wires"][0][2],
        "{{WIRE_2_TITLE}}": preset["wires"][1][1],
        "{{WIRE_2_ORIGIN}}": preset["wires"][1][0],
        "{{WIRE_2_BODY}}": preset["wires"][1][2],
        "{{WIRE_3_TITLE}}": preset["wires"][2][1],
        "{{WIRE_3_ORIGIN}}": preset["wires"][2][0],
        "{{WIRE_3_BODY}}": preset["wires"][2][2],
        "{{TABLE_TITLE}}": preset["table_title"],
        "{{TABLE_COL_1}}": preset["table_cols"][0],
        "{{TABLE_COL_2}}": preset["table_cols"][1],
        "{{TABLE_COL_3}}": preset["table_cols"][2],
        "{{TABLE_ROWS}}": build_table_rows_html(preset["table_rows"]),
        "{{ESSAY_KICKER}}": preset["essay_kicker"],
        "{{ESSAY_TITLE}}": preset["essay_title"],
        "{{ESSAY_PARAGRAPH_1}}": preset["essay_paragraphs"][0],
        "{{ESSAY_PARAGRAPH_2}}": preset["essay_paragraphs"][1],
        "{{CHRONICLE_KICKER}}": preset["chronicle_kicker"],
        "{{CHRONICLE_TITLE}}": preset["chronicle_title"],
        "{{CHRONICLE_PARAGRAPH}}": preset["chronicle_paragraph"],
    }

    html = template_content
    for placeholder, val in replacements.items():
        html = html.replace(placeholder, val)

    return html


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Broadsheet Newspaper Scaffolder — Confecciona jornais impressos históricos em HTML."
    )
    parser.add_argument(
        "--archetype",
        choices=["classic", "financial", "scientific", "cultural", "tech"],
        default="classic",
        help="Arquétipo estético e editorial do periódico.",
    )
    parser.add_argument("--title", type=str, help="Nome principal do jornal (Masthead).")
    parser.add_argument("--subtitle", type=str, help="Sub-masthead ou declaração de propósito.")
    parser.add_argument("--motto", type=str, help="Lema em latim ou vernáculo.")
    parser.add_argument("--location", type=str, help="Cidade(s) de publicação.")
    parser.add_argument("--date", type=str, help="Data por extenso.")
    parser.add_argument("--volume", type=str, default="XLVIII", help="Volume em numerais romanos.")
    parser.add_argument("--edition", type=str, default="17.432", help="Número sequencial da edição.")
    parser.add_argument("--price", type=str, help="Preço simbólico do exemplar.")
    parser.add_argument("--lead-title", type=str, help="Manchete colossal da matéria principal.")
    parser.add_argument("--lead-deck", type=str, help="Sublide explicativo da matéria principal.")
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="newspaper_broadsheet.html",
        help="Arquivo HTML de destino.",
    )

    args = parser.parse_args()

    try:
        html = generate_newspaper_html(
            archetype=args.archetype,
            title=args.title,
            subtitle=args.subtitle,
            latin_motto=args.motto,
            location=args.location,
            date_str=args.date,
            volume=args.volume,
            edition=args.edition,
            price=args.price,
            lead_headline=args.lead_title,
            lead_deck=args.lead_deck,
        )

        out_path = Path(args.output).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8")

        print(f"[OK] Broadsheet gerado com sucesso.")
        print(f"     Arquivo: {out_path}")
        print(f"     Arquetipo: {args.archetype}")
        print(f"     Tamanho: {len(html)} bytes")
    except Exception as exc:
        print(f"[ERRO] Falha ao gerar broadsheet: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
