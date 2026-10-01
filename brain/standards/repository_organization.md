# Padroes de Organizacao de Repositorios e Governanca de Projetos

Diretrizes organizacionais de alto padrao de engenharia e governanca documental.

---

## 1. Topologia Padrao de Pastas (Projetos Web / SaaS)
```
projeto/
├── .agents/                       # Skills e regras locais do agente
├── .github/                       # Pipelines de CI/CD e automacao
├── app/ ou src/app/               # Rotas e layouts do Next.js App Router
├── components/                    # Componentes divididos por dominio e ui/
│   ├── ui/                        # Botoes, dialogs, inputs atomicos (shadcn/ui style)
│   └── Brand.tsx                  # Componentes de marca em SVG puro
├── lib/                           # Clientes (Supabase, Resend) e helpers puros
├── design/ ou docs/               # Documentacao viva de marca e arquitetura
│   ├── BRAND_GUIDE.md             # Manual oficial de design system
│   ├── IDENTIDADE.md              # Tokens e especificacoes visuais
│   └── EXPLORACAO.md              # Registros de testes e descartes de direcao
├── public/                        # Imagens, favicons e brand/ (vetores oficiais)
├── .env.example                   # Template rigoroso de variaveis de ambiente
├── playwright.config.ts           # Configuracao de testes E2E
└── README.md                      # Documentacao concisa, mapa de notas e guia de setup
```

---

## 2. Governanca Documental em Markdown
- Arquitetura de Notas Interconectadas: Uso de wikilinks (duplos colchetes), tags e mapas conceituais para que qualquer IA ou colaborador consiga navegar pelo conhecimento sem perder contexto.
- Registro de Exploracoes e Descartes: Decisoes descartadas (como geracao de imagens com fundo inadequado ou paletas cliches) devem ser arquivadas em EXPLORACAO.md para evitar reincidencia de erros passados.
- Preservacao contra Amnesia: Todo projeto relevante deve manter um BRAND_GUIDE.md ou constitution com as escolhas imutaveis.

---

## 3. Diretriz Canonica de Nomenclatura de Diretorios do Operador
- **Regra Mandatoria de Caixa Alta:** Todo e qualquer diretorio de organizacao, agrupamento ou categorizacao do operador deve ser nomeado estritamente em **CAIXA ALTA (TODAS AS LETRAS MAIUSCULAS)**.
- **Proibicao de Underscores:** E expressamente proibido o uso de sublinhados/underscores (`_`) em nomes de pastas. A separacao entre palavras deve utilizar espacos regulares.
- **Exemplos Canonicos:**
  - Raiz de Downloads: `OPERADOR`, `SISTEMA`
  - Subpastas: `PROJETOS`, `PESQUISAS`, `INFRAESTRUTURA`, `ENGENHARIA`, `INSTALADORES`, `METODOLOGIA`, `IDENTIDADE VISUAL`, `DOCUMENTACAO`, `FOTOS`.

