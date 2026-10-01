---
id: node-padroes-engenharia
type: standard
tags:
  - engenharia
  - padrao-tecnico
  - arquitetura
---

# Padroes de Engenharia de Software

Conjunto canonico de regras de desenvolvimento de software extraido dos repositorios de [[Operador]].

## Sinapses
- Conectado a [[Cortex_Central]], [[Nextjs_Stack]], [[Supabase_Stack]], [[Atlas_Engineering_OS]].

## Mandatos
1. Next.js App Router: Server Components por padrao, Server Actions com validacao Zod.
2. Persistencia: Supabase com RLS habilitado e indexado em 100% das tabelas. Drizzle ORM para queries tipadas.
3. Testes Obrigatorios: Playwright E2E em Desktop (1440px) e Mobile (390px) com politica de zero erros no console.
4. Conventional Commits: Padronizacao estrita de mensagens de commit.
5. [[Karpathy_Engineering_Guidelines]]: Simplicidade estrita, alteracoes cirurgicas sem refatorar o adjacente e criterio verificavel de sucesso.
