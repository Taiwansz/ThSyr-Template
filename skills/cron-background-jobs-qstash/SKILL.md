---
name: cron-background-jobs-qstash
description: "Serverless background jobs, delayed queues, and cron scheduling engineering skill using Upstash QStash, Vercel Cron, and Supabase pg_cron. Solves serverless execution timeouts, provides guaranteed at-least-once delivery, exponential backoff retries, and scheduled triggers for appointment reminders and subscription billing."
argument-hint: "[qstash | cron | background-jobs | delays | retries | scheduling]"
license: MIT
metadata:
  author: Code Makers & PromptVault
  version: "1.0.0"
---

# Serverless Background Jobs & Scheduled Queues (Upstash QStash + Vercel Cron)

#categoria-code #background-jobs #qstash #cron #serverless #filas #lembretes #agendamentos

Esta skill rege a execução de tarefas assíncronas em segundo plano, agendamentos futuros (delayed jobs) e rotinas periódicas (crons) em arquiteturas serverless (Vercel / Next.js). Ela elimina o erro fatal de usar `setTimeout` no backend ou travar a requisição HTTP do usuário aguardando chamadas lentas de WhatsApp e gateways externos.

---

## 1. O Problema Fundamental do Serverless

>  **REGRA CENTRAL:** Na Vercel ou qualquer runtime serverless, assim que a função retorna uma resposta HTTP (`return NextResponse.json()`), **o processo é imediatamente congelado ou destruído**.
> Qualquer `setTimeout`, `Promise` solta sem `await` ou loop em memória será interrompido sem aviso.

### Três Ferramentas para Três Cenários:
1. **Upstash QStash (Jobs Agendados / Delayed Queues):** Ideal para "faça algo daqui a 2 horas" (ex: enviar lembrete de agendamento por WhatsApp, checar se o Pix foi pago após 15 minutos).
2. **Vercel Cron (`vercel.json`):** Ideal para tarefas periódicas em horário fixo (ex: rodar todo dia às 03:00 da manhã para fechar relatórios ou auditar assinaturas).
3. **Supabase `pg_cron`:** Ideal para tarefas que vivem e morrem 100% dentro do banco de dados (ex: deletar sessões expiradas a cada hora).

---

## 2. Padrão Upstash QStash (Agendamento Seguro de Mensagens & Tarefas)

Instalação:
```bash
npm install @upstash/qstash
```

### 2.A Publicando uma Tarefa Futura (Delayed Job)

Exemplo: No momento em que um agendamento é criado, agendamos um WhatsApp de lembrete para 2 horas antes do horário marcado:

```typescript
// lib/queue/scheduler.ts
import { Client } from '@upstash/qstash';

const qstash = new Client({ token: process.env.QSTASH_TOKEN! });

interface ScheduleReminderParams {
  appointmentId: string;
  customerPhone: string;
  customerName: string;
  appointmentTimestamp: number; // Unix timestamp em ms
}

export async function scheduleAppointmentReminder({
  appointmentId,
  customerPhone,
  customerName,
  appointmentTimestamp,
}: ScheduleReminderParams) {
  // Calcular delay em segundos: 2 horas antes (7200s)
  const twoHoursBefore = appointmentTimestamp - 2 * 60 * 60 * 1000;
  const delaySeconds = Math.max(0, Math.floor((twoHoursBefore - Date.now()) / 1000));

  const targetUrl = `${process.env.NEXT_PUBLIC_APP_URL}/api/jobs/send-whatsapp-reminder`;

  const res = await qstash.publishJSON({
    url: targetUrl,
    body: {
      appointmentId,
      customerPhone,
      customerName,
    },
    delay: delaySeconds, // Executa no momento exato
    retries: 3,          // Tenta até 3 vezes com backoff exponencial se a API do WhatsApp oscilar
  });

  return { messageId: res.messageId };
}
```

---

### 2.B Endpoint Receptor com Verificação Criptográfica de Assinatura

O endpoint de destino **deve validar a assinatura** para garantir que apenas o QStash possa disparar a rotina:

```typescript
// app/api/jobs/send-whatsapp-reminder/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { Receiver } from '@upstash/qstash';
import { createClient } from '@supabase/supabase-js';

const receiver = new Receiver({
  currentSigningKey: process.env.QSTASH_CURRENT_SIGNING_KEY!,
  nextSigningKey: process.env.QSTASH_NEXT_SIGNING_KEY!,
});

const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.SUPABASE_SERVICE_ROLE_KEY!);

export async function POST(req: NextRequest) {
  try {
    const rawBody = await req.text();
    const signature = req.headers.get('upstash-signature')!;

    // 1. Validar que a requisição veio do QStash oficial
    const isValid = await receiver.verify({
      signature,
      body: rawBody,
    });

    if (!isValid) {
      return NextResponse.json({ error: 'Assinatura inválida' }, { status: 401 });
    }

    const { appointmentId, customerPhone, customerName } = JSON.parse(rawBody);

    // 2. Verificar se o agendamento ainda está ativo (não foi cancelado nesse intervalo)
    const { data: appt } = await supabase
      .from('appointments')
      .select('status, service_name, starts_at')
      .eq('id', appointmentId)
      .single();

    if (appt?.status !== 'confirmed') {
      // Agendamento foi cancelado antes do disparo; descarta sem disparar
      return NextResponse.json({ skipped: true, reason: 'Agendamento cancelado' });
    }

    // 3. Disparo da mensagem via Evolution API / Z-API
    await fetch(`${process.env.WHATSAPP_API_URL}/message/sendText`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        apikey: process.env.WHATSAPP_API_KEY!,
      },
      body: JSON.stringify({
        number: customerPhone,
        text: `Olá, ${customerName}! Passando para lembrar do seu horário de *${appt.service_name}* daqui a 2 horas. Te esperamos! ---️`,
      }),
    });

    return NextResponse.json({ success: true });
  } catch (err: any) {
    console.error('Falha no background job:', err);
    // Retornar status >= 400 faz o QStash aplicar retentativa automática
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
```

---

## 3. Padrão Vercel Cron (`vercel.json`)

Para rotinas periódicas diárias ou horárias:

```json
// vercel.json
{
  "crons": [
    {
      "path": "/api/cron/release-expired-slots",
      "schedule": "*/10 * * * *"
    },
    {
      "path": "/api/cron/daily-billing-summary",
      "schedule": "0 3 * * *"
    }
  ]
}
```

### Proteção da Rota Vercel Cron:
```typescript
// app/api/cron/release-expired-slots/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.SUPABASE_SERVICE_ROLE_KEY!);

export async function GET(req: NextRequest) {
  const authHeader = req.headers.get('authorization');
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return NextResponse.json({ error: 'Não autorizado' }, { status: 401 });
  }

  // Libera reservas de Pix pendentes há mais de 15 minutos
  const fifteenMinutesAgo = new Date(Date.now() - 15 * 60 * 1000).toISOString();

  const { data: expired } = await supabase
    .from('orders')
    .update({ status: 'expired' })
    .eq('status', 'pending')
    .lt('created_at', fifteenMinutesAgo)
    .select('id');

  return NextResponse.json({ releasedCount: expired?.length ?? 0 });
}
```

---

## 4. Supabase `pg_cron` (Manutenção Interna no PostgreSQL)

Se você utiliza o Supabase Pro, pode executar crons diretamente dentro da engine do PostgreSQL sem depender de requisições HTTP:

```sql
-- Ativar extensões
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Limpar tokens de sessão revogados todo domingo à meia-noite
SELECT cron.schedule(
    'limpar-tokens-expirados',
    '0 0 * * 0',
    $$DELETE FROM auth.refresh_tokens WHERE revoked = true OR updated_at < NOW() - INTERVAL '30 days'$$
);
```
