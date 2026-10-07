---
name: transactional-email-resend
description: "High-deliverability transactional email engineering skill using Resend and React Email. Enforces TypeScript-native email components, dark/light mode client compatibility, DKIM/SPF/DMARC hygiene, anti-spam heuristics, calendar invites (.ics), and automated webhook tracking for bounces and deliveries."
argument-hint: "[resend | react-email | templates | bounce-tracking | deliverability]"
license: MIT
metadata:
  author: Code Makers & PromptVault
  version: "1.0.0"
---

# Transactional Email & Deliverability System (Resend + React Email)

#categoria-code #email #resend #react-email #deliverability #auth #notificacoes

Esta skill rege o envio de e-mails transacionais de alta entregabilidade (99%+) usando a stack moderna **Resend + React Email**. Ela elimina os problemas clássicos de IAs: geração de tabelas HTML quebradas dos anos 2000, e-mails caindo na caixa de SPAM ou na aba de Promoções do Gmail, e templates ilegíveis no Dark Mode do Apple Mail.

---

## 1. Princípios de Entregabilidade e Anti-SPAM

1. **Autenticação de Domínio Mandatória:**
   - **SPF:** `v=spf1 include:amazonses.com ~all` (ou o include oficial do Resend).
   - **DKIM:** Chaves CNAME configuradas no DNS do domínio (Cloudflare, GoDaddy, Vercel).
   - **DMARC:** `v=DMARC1; p=none; rua=mailto:dmarc-reports@seudominio.com` (mínimo para passar no crivo do Gmail e Yahoo 2024+).
2. **Proporção Texto vs. Imagem:** E-mails compostos unicamente de uma imagem gigante são imediatamente classificados como SPAM. O conteúdo crítico deve ser texto real renderizado em HTML acessível.
3. **Links com Texto Âncora Claro:** Nunca use URLs encurtadas (bit.ly) em e-mails transacionais. O domínio do link deve coincidir rigorosamente com o domínio do remetente.
4. **Respeito ao Dark Mode:** Use background com cores neutras seguras (`#ffffff` ou `#0f172a`), contraste WCAG AA para textos, e nunca presuma que o fundo será sempre branco.

---

## 2. Setup Base e Cliente Resend em TypeScript

Instalação recomendada:
```bash
npm install resend @react-email/components
```

```typescript
// lib/email/resend.ts
import { Resend } from 'resend';

if (!process.env.RESEND_API_KEY) {
  throw new Error('RESEND_API_KEY ausente nas variáveis de ambiente');
}

export const resend = new Resend(process.env.RESEND_API_KEY);

export const DEFAULT_FROM = process.env.NODE_ENV === 'production'
  ? 'App <notificacoes@seudominio.com.br>'
  : 'Acme <onboarding@resend.dev>';
```

---

## 3. Templates Profissionais em React Email

### 3.A Template 1: Confirmação de Agendamento (Com link para Google Calendar)

```tsx
// emails/appointment-confirmation.tsx
import {
  Body,
  Button,
  Container,
  Head,
  Heading,
  Hr,
  Html,
  Preview,
  Section,
  Text,
} from '@react-email/components';
import * as React from 'react';

interface AppointmentEmailProps {
  clientName: string;
  serviceName: string;
  professionalName: string;
  formattedDate: string; // Ex: "Sexta-feira, 20 de Março às 14:30"
  location: string;
  priceFormatted: string;
  calendarUrl: string;
}

export const AppointmentConfirmationEmail = ({
  clientName = 'Lucas',
  serviceName = 'Corte Degradê + Barba',
  professionalName = 'João',
  formattedDate = 'Sexta-feira, 20 de Março às 14:30',
  location = 'Rua das Flores, 123 - Centro',
  priceFormatted = 'R$ 75,00',
  calendarUrl = 'https://calendar.google.com',
}: AppointmentEmailProps) => {
  return (
    <Html>
      <Head />
      <Preview>Seu horário está confirmado: {serviceName} com {professionalName}</Preview>
      <Body style={main}>
        <Container style={container}>
          <Heading style={h1}>Horário Confirmado! ---️</Heading>
          <Text style={greeting}>Olá, {clientName}!</Text>
          <Text style={text}>
            Seu agendamento foi confirmado com sucesso. Veja abaixo os detalhes do seu horário:
          </Text>

          <Section style={card}>
            <Text style={cardItem}><strong>Serviço:</strong> {serviceName}</Text>
            <Text style={cardItem}><strong>Profissional:</strong> {professionalName}</Text>
            <Text style={cardItem}><strong>Data e Hora:</strong> {formattedDate}</Text>
            <Text style={cardItem}><strong>Local:</strong> {location}</Text>
            <Text style={cardItem}><strong>Valor:</strong> {priceFormatted}</Text>
          </Section>

          <Section style={btnContainer}>
            <Button style={button} href={calendarUrl}>
              Adicionar à Minha Agenda
            </Button>
          </Section>

          <Text style={subtext}>
            Precisa reagendar ou cancelar? Faça-o com pelo menos 2 horas de antecedência através do link no nosso app ou WhatsApp.
          </Text>

          <Hr style={hr} />
          <Text style={footer}>
            © {new Date().getFullYear()} Barbearia JaoBarber. Todos os direitos reservados.
          </Text>
        </Container>
      </Body>
    </Html>
  );
};

export default AppointmentConfirmationEmail;

const main = {
  backgroundColor: '#f6f9fc',
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  padding: '40px 0',
};

const container = {
  backgroundColor: '#ffffff',
  margin: '0 auto',
  padding: '32px 40px',
  borderRadius: '12px',
  maxWidth: '520px',
  boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
};

const h1 = {
  color: '#0f172a',
  fontSize: '24px',
  fontWeight: '700',
  marginBottom: '16px',
};

const greeting = {
  fontSize: '16px',
  color: '#334155',
  fontWeight: '600',
};

const text = {
  fontSize: '15px',
  lineHeight: '24px',
  color: '#475569',
};

const card = {
  backgroundColor: '#f8fafc',
  border: '1px solid #e2e8f0',
  borderRadius: '8px',
  padding: '16px 20px',
  margin: '20px 0',
};

const cardItem = {
  fontSize: '14px',
  color: '#1e293b',
  margin: '6px 0',
};

const btnContainer = {
  textAlign: 'center' as const,
  margin: '28px 0',
};

const button = {
  backgroundColor: '#0f172a',
  borderRadius: '8px',
  color: '#ffffff',
  fontSize: '14px',
  fontWeight: '600',
  textDecoration: 'none',
  padding: '12px 24px',
  display: 'inline-block',
};

const subtext = {
  fontSize: '13px',
  color: '#64748b',
  lineHeight: '20px',
};

const hr = {
  borderColor: '#e2e8f0',
  margin: '24px 0',
};

const footer = {
  color: '#94a3b8',
  fontSize: '12px',
  textAlign: 'center' as const,
};
```

---

### 3.B Template 2: Magic Link de Autenticação

```tsx
// emails/magic-link.tsx
import {
  Body,
  Button,
  Container,
  Head,
  Heading,
  Html,
  Preview,
  Section,
  Text,
} from '@react-email/components';
import * as React from 'react';

export const MagicLinkEmail = ({ magicLink = 'https://app.lacora.com.br/auth/confirm' }: { magicLink: string }) => (
  <Html>
    <Head />
    <Preview>Seu link seguro para entrar na plataforma</Preview>
    <Body style={{ backgroundColor: '#f8fafc', fontFamily: 'sans-serif', padding: '40px 0' }}>
      <Container style={{ backgroundColor: '#fff', padding: '36px', borderRadius: '12px', maxWidth: '480px' }}>
        <Heading style={{ fontSize: '22px', fontWeight: 'bold', color: '#0f172a' }}>Entrar na sua conta</Heading>
        <Text style={{ color: '#475569', fontSize: '15px', lineHeight: '24px' }}>
          Clique no botão abaixo para fazer login instantaneamente na sua conta. Este link é válido por 15 minutos.
        </Text>
        <Section style={{ textAlign: 'center', margin: '28px 0' }}>
          <Button
            href={magicLink}
            style={{ backgroundColor: '#2563eb', color: '#fff', padding: '12px 28px', borderRadius: '8px', fontWeight: '600', textDecoration: 'none' }}
          >
            Fazer Login com 1 Clique
          </Button>
        </Section>
        <Text style={{ fontSize: '12px', color: '#94a3b8' }}>
          Se você não solicitou este link, pode ignorar este e-mail com segurança.
        </Text>
      </Container>
    </Body>
  </Html>
);
```

---

## 4. Disparo Assíncrono com Fallback e Log no Supabase

```typescript
// lib/email/sender.ts
import { resend, DEFAULT_FROM } from './resend';
import { AppointmentConfirmationEmail } from '@/emails/appointment-confirmation';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export async function sendAppointmentEmail(recipientEmail: string, details: any) {
  try {
    const { data, error } = await resend.emails.send({
      from: DEFAULT_FROM,
      to: recipientEmail,
      subject: `Horário Confirmado: ${details.serviceName}`,
      react: AppointmentConfirmationEmail(details),
    });

    if (error) {
      console.error('Erro Resend:', error);
      throw error;
    }

    // Registrar log no Supabase
    await supabase.from('email_logs').insert({
      resend_id: data?.id,
      recipient: recipientEmail,
      type: 'appointment_confirmation',
      status: 'sent',
    });

    return { success: true, emailId: data?.id };
  } catch (err: any) {
    console.error('Falha ao enviar e-mail transacional:', err.message);
    return { success: false, error: err.message };
  }
}
```

---

## 5. Webhook Resend para Bounce e Rejeição de E-mail

Para proteger a reputação do domínio, quando o Resend notifica um `email.bounced` ou `email.complained`, o endereço deve ser marcado no banco para nunca mais receber disparos:

```typescript
// app/api/webhooks/resend/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.SUPABASE_SERVICE_ROLE_KEY!);

export async function POST(req: NextRequest) {
  const event = await req.json();

  if (event.type === 'email.bounced' || event.type === 'email.complained') {
    const email = event.data.to[0];

    // Bloqueia envios futuros para este e-mail
    await supabase
      .from('email_suppressions')
      .upsert({ email, reason: event.type, created_at: new Date().toISOString() });
  }

  return NextResponse.json({ ok: true });
}
```
