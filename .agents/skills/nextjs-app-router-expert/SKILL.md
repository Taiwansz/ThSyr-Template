---
name: nextjs-app-router-expert
description: "Production engineering skill for Next.js 15+ App Router and React 19. Enforces strict Server vs. Client component boundaries, secured Server Actions validated with Zod and Supabase auth, modern React 19 form actions (useActionState, useOptimistic), optimal data fetching without waterfalls, and precise cache revalidation."
argument-hint: "[server-actions | boundaries | forms | cache]"
license: MIT
metadata:
  author: Code Makers & PromptVault
  version: "1.0.0"
---

# Next.js 15+ App Router & React 19 Expert Skill

#categoria-code #nextjs #react19 #app-router #server-actions #frontend

Esta skill governa a arquitetura moderna de aplicações em Next.js (App Router) e React 19. Ela erradica os vícios mais destrutivos de código gerado por IA: o uso indiscriminado de `'use client'`, Server Actions abertas sem autenticação interna, hooks depreciados do React 18 e travamentos de cache.

---

## 1. A Fronteira Server vs. Client (A Regra das Folhas da Árvore)

- **Default é Server Component:** Todo arquivo `page.tsx`, `layout.tsx` e componente estrutural deve ser Server Component (sem diretiva `'use client'`).
- **Isole a Interatividade nas Folhas:** Coloque `'use client'` exclusivamente nos nós terminais (botões com clique, inputs controlados, menus drop-down com estado local).
- **Injeção de Filhos (Children Pattern):**
  Se um componente interativo precisa envolver conteúdo estático/pesado do servidor, passe-o como `children`:
  ```tsx
  // [OK] CORRETO: ModalClient é 'use client', mas o conteúdo interno é renderizado no servidor
  <ModalClient>
    <ServerDataList items={items} />
  </ModalClient>
  ```

---

## 2. Padrão Mandatório de Server Actions Blindadas

>  **VULNERABILIDADE CRÍTICA:** Server Actions geram endpoints HTTP públicos (`POST`). **Nunca presuma que a chamada partiu de um usuário autorizado só porque o botão estava condicionado no frontend.**

Toda Server Action deve seguir rigorosamente as 4 etapas abaixo:

```tsx
'use server';

import { z } from 'zod';
import { createClient } from '@/lib/supabase/server';
import { revalidatePath } from 'next/cache';

// 1. Schema Zod obrigatório para validação de payload
const UpdateProfileSchema = z.object({
  fullName: z.string().min(2, 'Nome muito curto').max(100),
  bio: z.string().max(500).optional(),
});

export type FormState = {
  success?: boolean;
  message?: string;
  errors?: Record<string, string[]>;
};

export async function updateProfileAction(
  prevState: FormState,
  formData: FormData
): Promise<FormState> {
  // 2. Validação estrita de autenticação e sessão no servidor
  const supabase = await createClient();
  const { data: { user }, error: authError } = await supabase.auth.getUser();

  if (authError || !user) {
    return { success: false, message: 'Não autorizado. Faça login novamente.' };
  }

  // 3. Validação dos dados via Zod
  const rawData = {
    fullName: formData.get('fullName'),
    bio: formData.get('bio'),
  };

  const parsed = UpdateProfileSchema.safeParse(rawData);
  if (!parsed.success) {
    return {
      success: false,
      errors: parsed.error.flatten().fieldErrors,
      message: 'Dados inválidos.',
    };
  }

  // 4. Execução da mutação no banco
  const { error: dbError } = await supabase
    .from('profiles')
    .update({ full_name: parsed.data.fullName, bio: parsed.data.bio })
    .eq('id', user.id);

  if (dbError) {
    return { success: false, message: 'Erro ao salvar alterações no banco.' };
  }

  // 5. Revalidação cirúrgica de cache
  revalidatePath('/dashboard/profile');
  return { success: true, message: 'Perfil atualizado com sucesso!' };
}
```

---

## 3. Formulários com React 19 (`useActionState` + `useOptimistic`)

- [ERRO] **BANIDO:** `useFormState` e `useFormStatus` importados de `react-dom` (padrão antigo do React 18).
- [OK] **OBRIGATÓRIO:** `useActionState` importado diretamente de `react`:

```tsx
'use client';

import { useActionState } from 'react';
import { updateProfileAction, FormState } from '@/actions/profile';

const initialState: FormState = { message: '' };

export function ProfileForm() {
  const [state, formAction, isPending] = useActionState(updateProfileAction, initialState);

  return (
    <form action={formAction} className="space-y-4">
      <div>
        <label htmlFor="fullName">Nome Completo</label>
        <input id="fullName" name="fullName" disabled={isPending} className="input" />
        {state.errors?.fullName && (
          <p className="text-red-500 text-sm">{state.errors.fullName[0]}</p>
        )}
      </div>

      <button type="submit" disabled={isPending} className="btn-primary">
        {isPending ? 'Salvando...' : 'Atualizar Perfil'}
      </button>

      {state.message && (
        <p className={state.success ? 'text-green-500' : 'text-red-500'}>
          {state.message}
        </p>
      )}
    </form>
  );
}
```

---

## 4. Evitando Waterfalls de Dados (Data Fetching Concorrente)

- [ERRO] **Evite waterfalls sequenciais:**
  ```tsx
  // Lento: o segundo await espera o primeiro terminar
  const user = await getUser();
  const orders = await getOrders(user.id);
  const notifications = await getNotifications();
  ```
- [OK] **Execute em paralelo com `Promise.all` ou Suspense Streaming:**
  ```tsx
  const [user, notifications] = await Promise.all([
    getUser(),
    getNotifications(),
  ]);
  ```
- Para seções independentes e pesadas, use `<Suspense fallback={<Skeleton />}>` para não atrasar o primeiro byte (TTFB) da página.
