---
name: project-onboarding-bootstrap
description: "Instant repository scaffolding and onboarding automation skill. Generates tailored root CLAUDE.md files, clean Next.js + Supabase directory structures (/actions, /components/ui, /lib/supabase, /types), essential .gitignore hygiene, and GitHub Actions CI pipelines (lint, typecheck, build) in 10 seconds."
argument-hint: "[init | claude-md | ci-cd | scaffold]"
license: MIT
metadata:
  author: Code Makers & PromptVault
  version: "1.0.0"
---

# Project Onboarding Bootstrap — Setup de Novos Repositórios em 10s

#categoria-code #automacao #devops #ci-cd #bootstrap #produtividade #github

Esta skill automatiza a configuração inicial de qualquer novo repositório de software. Em vez de gastar 30 minutos configurando regras manuais de linter, pastas e instruções para a IA, esta skill injeta a infraestrutura completa de governança em 10 segundos.

---

## 1. O Template de `CLAUDE.md` Gerado na Raiz do Projeto

Ao inicializar qualquer repositório, o agente deve gerar um `CLAUDE.md` personalizado na raiz:

```markdown
# Diretrizes Gerais do Projeto — [Nome do Projeto]

## 1. Stack Oficial
- **Frontend:** Next.js 15+ (App Router), React 19, Tailwind CSS.
- **Backend & Auth:** Supabase (PostgreSQL, Row Level Security).
- **Hospedagem:** Vercel (Edge Runtime).

## 2. Metodologia de Desenvolvimento (Framework Universal)
- **PRIMEIRO ENTENDER. DEPOIS PLANEJAR. SÓ ENTÃO EXECUTAR.**
- Respeite as etapas do projeto: não inicie código antes da arquitetura e schema aprovados.
- Ao fazer alterações em produção, aplique estritamente as regras de **Hotfix Cirúrgico** (proibido redesign ou refatorações desnecessárias).

## 3. Padrões de Código Mandatórios
- **Server vs. Client:** Mantenha componentes como Server Components por padrão. Isole `'use client'` nas folhas da árvore.
- **Server Actions:** Valide todo payload com Zod e verifique a sessão do usuário com Supabase antes de mutações.
- **Banco de Dados:** RLS obrigatório em 100% das tabelas criadas. Use `EXISTS` indexado para checagens relacionais.
- **Edição Cirúrgica:** Nunca reescreva arquivos inteiros; forneça apenas blocos de diff cirúrgicos.
- **Motion & UI:** Use animações com propósito (60fps GPU-accelerated) e respeite `prefers-reduced-motion`.
```

---

## 2. Estrutura de Diretórios Padronizada

```
meu-projeto/
├── .github/
│   └── workflows/
│       └── ci.yml             # Pipeline de verificação automática
├── actions/                   # Server Actions protegidas ('use server' + Zod)
├── app/                       # Rotas do Next.js (App Router)
│   ├── (auth)/                # Rotas de login / cadastro
│   ├── (dashboard)/           # Rotas autenticadas do sistema
│   ├── api/webhooks/          # Rotas de webhooks (Stripe / WhatsApp)
│   ├── layout.tsx             # Root layout com fontes locais e providers
│   └── page.tsx               # Landing page principal
├── components/
│   ├── ui/                    # Componentes base (shadcn/ui / primitivos)
│   └── shared/                # Componentes compostos (Navbar, Footer, Modais)
├── lib/
│   ├── supabase/
│   │   ├── client.ts          # Supabase browser client (anon key)
│   │   ├── server.ts          # Supabase server client para Server Components
│   │   └── admin.ts           # Supabase admin client (service_role exclusivo)
│   └── utils.ts               # Funções utilitárias (cn, formatações)
├── types/
│   ├── database.types.ts      # Tipos gerados automaticamente pelo Supabase CLI
│   └── index.ts               # Tipos de negócio compartilhados
├── CLAUDE.md                  # Instruções de projeto para agentes de IA
└── .gitignore                 # Higiene de arquivos (.env, node_modules)
```

---

## 3. GitHub Action de CI/CD Pré-Configurada (`.github/workflows/ci.yml`)

Garante que nenhuma branch quebre o build antes do merge para a `main`:

```yaml
name: CI Quality Gate

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  verify:
    name: Lint, Typecheck & Build
    runs-on: ubuntu-latest
    steps:
      - name: Checkout do Código
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'

      - name: Instalar Dependências
        run: npm ci

      - name: Checagem de Tipos (TypeScript)
        run: npm run type-check --if-present

      - name: Linter (ESLint)
        run: npm run lint

      - name: Validação de Build
        run: npm run build
        env:
          NEXT_PUBLIC_SUPABASE_URL: ${{ secrets.NEXT_PUBLIC_SUPABASE_URL || 'https://fake.supabase.co' }}
          NEXT_PUBLIC_SUPABASE_ANON_KEY: ${{ secrets.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'fake-key' }}
```
