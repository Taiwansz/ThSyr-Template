---
name: supabase-postgres-pro
description: "Expert Supabase and PostgreSQL backend engineering skill. Enforces leak-proof Row Level Security (RLS), high-performance queries using indexed EXISTS, robust PL/pgSQL triggers with SECURITY DEFINER, idempotent database migrations, safe Edge Functions, and automated TypeScript type generation."
argument-hint: "[schema | rls | trigger | migration | edge-function]"
license: MIT
metadata:
  author: Code Makers & PromptVault
  version: "1.0.0"
---

# Supabase & PostgreSQL Pro — Backend Engineering Skill

#categoria-code #database #supabase #postgres #rls #seguranca

Esta skill governa o design, modelagem e proteção do backend relacional usando PostgreSQL e Supabase. Ela elimina as falhas mais comuns cometidas por IAs: regras de RLS com recursão infinita, queries lentas sem índice, vazamento de chaves privilegiadas e triggers vulneráveis a escalação de privilégios.

---

## 1. Diretrizes Mandatórias de RLS (Row Level Security)

1. **RLS Obrigatório em 100% das Tabelas:**
   Nenhuma tabela pública pode existir sem RLS ativado:
   ```sql
   ALTER TABLE public.minha_tabela ENABLE ROW LEVEL SECURITY;
   ```
2. **Performance em Políticas com Subqueries (A Regra do EXISTS):**
   - [ERRO] **NUNCA use `IN`:** `USING (organization_id IN (SELECT org_id FROM memberships WHERE user_id = auth.uid()))` causa full-table scan e degrada drasticamente a performance.
   - [OK] **SEMPRE use `EXISTS`:**
     ```sql
     CREATE POLICY "Membros da organização podem visualizar"
     ON public.minha_tabela
     FOR SELECT
     TO authenticated
     USING (
       EXISTS (
         SELECT 1 FROM public.organization_members
         WHERE organization_members.organization_id = minha_tabela.organization_id
           AND organization_members.user_id = auth.uid()
       )
     );
     ```
3. **Indexação Mandatória de RLS:**
   Toda coluna referenciada em uma cláusula `USING` ou `WITH CHECK` (especialmente Foreign Keys e `user_id`) **DEVE possuir um índice B-Tree dedicado**:
   ```sql
   CREATE INDEX IF NOT EXISTS idx_organization_members_lookup 
   ON public.organization_members (organization_id, user_id);
   ```
4. **Separação por Operação:**
   Evite políticas genéricas `FOR ALL`. Defina políticas explícitas e granulares para `SELECT`, `INSERT`, `UPDATE` e `DELETE`.

---

## 2. Triggers em PL/pgSQL e Proteção de Privilégios

Ao criar triggers automáticos (como criar perfil após signup no `auth.users`):

```sql
-- 1. Função com SECURITY DEFINER e search_path fechado
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name, avatar_url, updated_at)
  VALUES (
    new.id,
    COALESCE(new.raw_user_meta_data->>'full_name', ''),
    COALESCE(new.raw_user_meta_data->>'avatar_url', ''),
    NOW()
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN new;
END;
$$;

-- 2. Trigger atrelado ao auth.users
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

> **Regra de Ouro:** Toda função `SECURITY DEFINER` roda com privilégios de superusuário do banco. É **obrigatório** declarar `SET search_path = public;` para evitar ataques de injeção de schemas maliciosos.

---

## 3. Padrão de Migrações (Supabase CLI)

- Toda alteração de schema deve ser gravada em um arquivo de migração versionado no diretório `supabase/migrations/`:
  - Formato: `<YYYYMMDDHHMMSS>_<descricao_em_snake_case>.sql`
- **Idempotência Obrigatória:**
  - `CREATE TABLE IF NOT EXISTS ...`
  - `CREATE INDEX IF NOT EXISTS ...`
  - `DO $$ BEGIN ... EXCEPTION WHEN duplicate_object THEN NULL; END $$;` para enums ou constraints.
- Ao final de cada migração, gere os tipos TypeScript para o frontend:
  ```bash
  npx supabase gen types typescript --local > types/supabase.ts
  ```

---

## 4. Regras de Fronteira (Client vs. Server)

| Recurso | Onde Executar | Chave Utilizada |
| :--- | :--- | :--- |
| **Leitura/Escrita de Dados do Usuário** | Browser ou Server Component | Chave Pública (`NEXT_PUBLIC_SUPABASE_ANON_KEY`) |
| **Autenticação / Login / Logout** | Browser ou Server Action | Chave Pública (`anon`) |
| **Operações Administrativas / Webhooks** | Edge Function ou Server Action | Chave Secreta (`SUPABASE_SERVICE_ROLE_KEY`) |
| **Geração de Relatórios Pesados / Jobs** | Edge Function em background | Service Role + validação de assinatura |

> [ALERTA]️ **ATENÇÃO:** A chave `SUPABASE_SERVICE_ROLE_KEY` tem passe livre e **ignora completamente o RLS**. Ela NUNCA pode ser enviada ao navegador, nem em variáveis públicas `NEXT_PUBLIC_*`.
