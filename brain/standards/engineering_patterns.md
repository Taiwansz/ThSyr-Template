# Padroes de Engenharia de Software (Extracao dos Repositorios)

Diretrizes tecnicas sintetizadas a partir da analise de arquiteturas modulares e boas praticas de engenharia de software.

---

## 1. Stack e Arquitetura Frontend
- Framework: Next.js (App Router exclusivo).
- Separacao de Fronteiras: Server Components por padrao para busca de dados e renderizacao inicial. Client Components demarcados com "use client" apenas quando houver estado local, eventos de clique ou animacoes de browser.
- Server Actions: Acoes de mutacao com validacao estrita de dados (Zod) e autenticacao previa.
- Estilizacao: Tailwind CSS estruturado com variaveis CSS semanticas (--color-background, --color-surface, etc.) integradas no tailwind.config.js / @import "tailwindcss".
- Iconografia: Lucide React e colecoes proprietarias em SVG puro com viewBox 48x48 e espessura de traco entre 1.4px e 1.6px.

---

## 2. Persistencia e Dados
- Backend as a Service: Supabase (@supabase/ssr e @supabase/supabase-js).
- Politica de Seguranca: Row Level Security (RLS) habilitado em 100% das tabelas PostgreSQL com politicas expressas baseadas em auth.uid().
- ORM e Migrations: Drizzle ORM (drizzle-orm, drizzle.config.ts) ou drivers diretos (pg) com migrations versionadas. Chaves de servico restritas exclusivamente ao backend.

---

## 3. Garantia de Qualidade e Testes
- E2E: Playwright (playwright.config.ts) com testes multi-viewport obrigatorios (Desktop 1440px vs Mobile 390px).
- Politica de Erros em Console: Tolerancia zero a erros ou warnings no console do navegador durante execucao de testes.
- Scripts de Verificacao: Todo package.json deve manter:
  - dev, build, start
  - lint (ESLint configurado)
  - typecheck (tsc --noEmit)
  - test:e2e (Playwright)
  - verify (script combinando lint, typecheck e testes)

---

## 4. Convencao de Commits e Controle de Versao
- Padrao Conventional Commits estrito:
  - feat: nova funcionalidade
  - fix: correcao de bug
  - style: alteracoes visuais e de design system sem alteracao de logica
  - chore: manutencao de dependencias e configuracoes
  - refactor: refatoracao de codigo
  - docs: atualizacoes documentais
- Branch principal: main.

---

## 5. Protocolo Agentico para Projetos de Grande Porte (SDD + RPI)
- Consultar compulsoriamente [[spec_driven_development]] e a regra de governanca em `.agents/rules/spec-driven-agentic-protocol.md`.
- Scaffolding documental obrigatorio em `docs/specs/` (`main.md`, `architecture.md`, `domain.md`, `security.md`, `api-contracts.md`, `quality.md`).
- Consulta e navegacao topologica via [[Graphify_Code_Architecture]].
- Selecao de estruturas de dados e analise de complexidade Big-O estritas (proibicao de loops quadraticos $O(n^2)$ e paginacao obrigatoria).

## Sinapses
- Conectado a [[Padroes_Engenharia]].
- Conectado a [[spec_driven_development]].
- Conectado a [[Graphify_Code_Architecture]].
- Conectado a [[Cortex_Central]].
- Conectado a [[Lobo_Parietal]].
