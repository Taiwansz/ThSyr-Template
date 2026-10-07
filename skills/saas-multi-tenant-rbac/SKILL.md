---
name: saas-multi-tenant-rbac
description: "Enterprise multi-tenant architecture and Role-Based Access Control (RBAC) skill for SaaS applications (enterprise multi-tenant SaaS). Enforces isolated PostgreSQL relational schemas (organizations, members, roles, invitations), tamper-proof Supabase RLS policies with zero cross-tenant data leakage, and Next.js workspace routing middleware."
argument-hint: "[schema | rbac | invitations | tenant-isolation]"
license: MIT
metadata:
  author: Code Makers & PromptVault
  version: "1.0.0"
---

# SaaS Multi-Tenant & RBAC Architecture Skill

#categoria-code #saas #multitenant #rbac #supabase #postgres #seguranca

Esta skill governa a arquitetura multi-inquilino (*multi-tenant*) e o controle de acesso baseado em papéis (*RBAC*) para aplicações SaaS como aplicacoes SaaS corporativas de alta escala. Ela garante isolamento matemático entre empresas/workspaces e previne vazamento de dados em rotas compartilhadas.

---

## 1. O Schema Relacional no PostgreSQL (Supabase)

```sql
-- 1. Enum de papéis hierárquicos
CREATE TYPE public.org_role AS ENUM ('owner', 'admin', 'member', 'viewer');

-- 2. Tabela de Organizações / Workspaces
CREATE TABLE IF NOT EXISTS public.organizations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  slug text NOT NULL UNIQUE,
  billing_status text NOT NULL DEFAULT 'active', -- 'active', 'past_due', 'trialing'
  created_at timestamptz DEFAULT now()
);

-- 3. Tabela de Membros da Organização
CREATE TABLE IF NOT EXISTS public.organization_members (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  role public.org_role NOT NULL DEFAULT 'member',
  created_at timestamptz DEFAULT now(),
  CONSTRAINT unique_user_per_org UNIQUE (organization_id, user_id)
);

-- Índices vitais para RLS de alta performance
CREATE INDEX IF NOT EXISTS idx_org_members_lookup ON public.organization_members (organization_id, user_id);
CREATE INDEX IF NOT EXISTS idx_org_members_user ON public.organization_members (user_id);

-- 4. Tabela de Convites por E-mail (Magic Token)
CREATE TABLE IF NOT EXISTS public.organization_invitations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id uuid NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
  email text NOT NULL,
  role public.org_role NOT NULL DEFAULT 'member',
  token text NOT NULL UNIQUE,
  expires_at timestamptz NOT NULL,
  created_at timestamptz DEFAULT now()
);
```

---

## 2. Função de Permissão e RLS Multi-Tenant Blindado

Para evitar escrever subqueries repetitivas, crie uma função auxiliar em PL/pgSQL:

```sql
CREATE OR REPLACE FUNCTION public.has_org_permission(
  target_org_id uuid,
  required_role public.org_role DEFAULT 'viewer'
)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  user_role public.org_role;
BEGIN
  -- Busca o papel do usuário autenticado na organização alvo
  SELECT role INTO user_role
  FROM public.organization_members
  WHERE organization_id = target_org_id
    AND user_id = auth.uid();

  IF user_role IS NULL THEN
    RETURN false;
  END IF;

  -- Hierarquia: owner > admin > member > viewer
  IF required_role = 'viewer' THEN
    RETURN true;
  ELSIF required_role = 'member' AND user_role IN ('owner', 'admin', 'member') THEN
    RETURN true;
  ELSIF required_role = 'admin' AND user_role IN ('owner', 'admin') THEN
    RETURN true;
  ELSIF required_role = 'owner' AND user_role = 'owner' THEN
    RETURN true;
  END IF;

  RETURN false;
END;
$$;
```

### Aplicando em Tabelas de Negócio (Ex: `projects`, `clients`):
```sql
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;

-- Leitura: Qualquer membro com acesso 'viewer' ou superior pode ver os projetos da organização
CREATE POLICY "Membros podem visualizar projetos da sua org"
ON public.projects
FOR SELECT
TO authenticated
USING (public.has_org_permission(organization_id, 'viewer'));

-- Escrita: Apenas membros ou admins podem criar/editar
CREATE POLICY "Operadores podem gerenciar projetos da sua org"
ON public.projects
FOR INSERT
TO authenticated
WITH CHECK (public.has_org_permission(organization_id, 'member'));

-- Exclusão: Apenas admins ou owners podem deletar
CREATE POLICY "Admins podem deletar projetos"
ON public.projects
FOR DELETE
TO authenticated
USING (public.has_org_permission(organization_id, 'admin'));
```

---

## 3. Roteamento de Workspaces no Next.js (App Router)

Adote a estrutura de rotas com slug dinâmico: `app/(dashboard)/[orgSlug]/...`

### Middleware de Proteção de Tenant (`middleware.ts`):
```typescript
import { NextRequest, NextResponse } from 'next/server';
import { createServerClient } from '@supabase/ssr';

export async function middleware(req: NextRequest) {
  const res = NextResponse.next();
  const pathname = req.nextUrl.pathname;

  // Ignorar arquivos estáticos e rotas de autenticação
  if (pathname.startsWith('/_next') || pathname.startsWith('/login') || pathname.startsWith('/api')) {
    return res;
  }

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() { return req.cookies.getAll(); },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) => req.cookies.set(name, value));
        },
      },
    }
  );

  const { data: { user } } = await supabase.auth.getUser();

  if (!user && pathname !== '/login') {
    return NextResponse.redirect(new URL('/login', req.url));
  }

  return res;
}
```
