---
name: brazilian-payments-pix
description: "Comprehensive Brazilian payments and Pix engineering skill for SaaS, local services, and digital products. Implements dynamic Pix QR Codes, Copia e Cola (EMV payload), multi-gateway integration (Asaas, Mercado Pago, Stripe Brasil), real-time webhook liquidation, 15-minute expiration timers with slot release, payment splits, and live status polling/SSE."
argument-hint: "[pix | asaas | mercadopago | stripe-br | checkout | webhooks]"
license: MIT
metadata:
  author: Code Makers & PromptVault
  version: "1.0.0"
---

# Brazilian Payments & Pix Architecture (Asaas, Mercado Pago, Stripe BR)

#categoria-code #pagamentos #pix #asaas #mercadopago #stripe #fintech #checkout

Esta skill rege a implementação completa de pagamentos para o mercado brasileiro, com foco em **Pix Instantâneo (QR Code dinâmico + Copia e Cola)**, gateways nacionais e conciliação em tempo real. Ela elimina falhas críticas como bloqueio perpétuo de agendamentos por falta de expiração, tela travada aguardando confirmação manual e duplicidade de liquidação.

---

## 1. Princípios de Ouro do Pix em Produção

1. **Expiração Rigorosa com Liberação de Slot:** Todo Pix dinâmico deve possuir validade estrita (padrão: 15 minutos). Ao expirar sem confirmação de pagamento, o lock de agendamento (ou reserva de estoque) **deve ser liberado automaticamente**.
2. **Confirmação via Webhook + Polling/SSE Ativo:**
   - **Backend:** A única fonte de verdade da liquidação é o webhook criptografado do gateway.
   - **Frontend:** O checkout deve escutar confirmações via Server-Sent Events (SSE), Supabase Realtime ou Polling exponencial (a cada 3s nos primeiros 2 min, depois a cada 10s) para redirecionar o cliente instantaneamente assim que o app bancário liquidar.
3. **Idempotência no Banco de Dados:** O `external_id` (ID da transação no gateway) deve ter índice `UNIQUE`. Reprocessamentos de webhook jamais podem duplicar créditos, agendamentos ou notificações.
4. **Resiliência do Payload "Copia e Cola":** O código alfanumérico EMV (Pix Copia e Cola) deve ser exibido com botão nativo `navigator.clipboard.writeText` e feedback visual de sucesso ("Copiado!").

---

## 2. Modelagem Relacional no PostgreSQL (Supabase)

```sql
-- Status do ciclo de vida do pagamento
CREATE TYPE payment_status AS ENUM ('pending', 'paid', 'expired', 'failed', 'refunded');
CREATE TYPE payment_gateway AS ENUM ('asaas', 'mercadopago', 'stripe');

CREATE TABLE IF NOT EXISTS public.orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    customer_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    customer_name TEXT NOT NULL,
    customer_email TEXT NOT NULL,
    customer_cpf_cnpj TEXT NOT NULL,
    amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
    status payment_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.pix_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES public.orders(id) ON DELETE CASCADE,
    gateway payment_gateway NOT NULL,
    gateway_charge_id TEXT NOT NULL UNIQUE,
    qr_code_base64 TEXT NOT NULL,
    copy_paste_payload TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    paid_at TIMESTAMPTZ,
    status payment_status NOT NULL DEFAULT 'pending',
    raw_response JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices de alta performance
CREATE INDEX idx_pix_order ON public.pix_transactions(order_id);
CREATE INDEX idx_pix_charge_id ON public.pix_transactions(gateway_charge_id);
CREATE INDEX idx_pix_expiration ON public.pix_transactions(status, expires_at) WHERE status = 'pending';
```

---

## 3. Implementação dos Gateways Brasileiros (Next.js Server Actions)

### 3.A Padrão Asaas (API v3 — Altamente Recomendado para Negócios Locais & SaaS BR)

```typescript
// lib/payments/asaas.ts
const ASAAS_API_URL = process.env.ASAAS_ENVIRONMENT === 'production' 
  ? 'https://api.asaas.com/v3' 
  : 'https://sandbox.asaas.com/v3';

interface CreateAsaasPixParams {
  customer: {
    name: string;
    cpfCnpj: string;
    email?: string;
  };
  value: number; // Ex: 45.00
  description: string;
  dueDate: string; // YYYY-MM-DD
}

export async function createAsaasPixCharge(params: CreateAsaasPixParams) {
  // 1. Criar ou buscar cliente
  const customerRes = await fetch(`${ASAAS_API_URL}/customers`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      access_token: process.env.ASAAS_API_KEY!,
    },
    body: JSON.stringify({
      name: params.customer.name,
      cpfCnpj: params.customer.cpfCnpj.replace(/\D/g, ''),
      email: params.customer.email,
    }),
  });
  const customer = await customerRes.json();

  // 2. Criar cobrança Pix
  const chargeRes = await fetch(`${ASAAS_API_URL}/payments`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      access_token: process.env.ASAAS_API_KEY!,
    },
    body: JSON.stringify({
      customer: customer.id,
      billingType: 'PIX',
      value: params.value,
      dueDate: params.dueDate,
      description: params.description,
    }),
  });
  const charge = await chargeRes.json();

  // 3. Obter QR Code e Chave Copia e Cola
  const qrRes = await fetch(`${ASAAS_API_URL}/payments/${charge.id}/pixQrCode`, {
    headers: { access_token: process.env.ASAAS_API_KEY! },
  });
  const qrData = await qrRes.json();

  return {
    chargeId: charge.id,
    encodedImage: qrData.encodedImage, // base64
    payload: qrData.payload, // copia e cola
    expirationDate: qrData.expirationDate,
  };
}
```

---

### 3.B Padrão Mercado Pago (SDK Oficial v2)

```typescript
// lib/payments/mercadopago.ts
import { MercadoPagoConfig, Payment } from 'mercadopago';

const client = new MercadoPagoConfig({ accessToken: process.env.MERCADO_PAGO_ACCESS_TOKEN! });
const payment = new Payment(client);

export async function createMercadoPagoPix({
  amount,
  email,
  cpf,
  description,
}: {
  amount: number;
  email: string;
  cpf: string;
  description: string;
}) {
  const result = await payment.create({
    body: {
      transaction_amount: amount,
      description,
      payment_method_id: 'pix',
      payer: {
        email,
        identification: {
          type: 'CPF',
          number: cpf.replace(/\D/g, ''),
        },
      },
    },
  });

  const pixData = result.point_of_interaction?.transaction_data;

  return {
    chargeId: result.id?.toString(),
    qrCodeBase64: pixData?.qr_code_base64,
    copyPaste: pixData?.qr_code,
    ticketUrl: pixData?.ticket_url,
  };
}
```

---

## 4. Webhook de Liquidação e Confirmação Instantânea

Exemplo de rota App Router para o Asaas (`app/api/webhooks/asaas/route.ts`):

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export async function POST(req: NextRequest) {
  try {
    const authHeader = req.headers.get('asaas-access-token');
    if (authHeader !== process.env.ASAAS_WEBHOOK_SECRET) {
      return NextResponse.json({ error: 'Não autorizado' }, { status: 401 });
    }

    const event = await req.json();

    // Eventos de liquidação confirmada
    if (event.event === 'PAYMENT_RECEIVED' || event.event === 'PAYMENT_CONFIRMED') {
      const chargeId = event.payment.id;

      // Atualização atômica idempotente
      const { data: pixTx, error } = await supabase
        .from('pix_transactions')
        .update({
          status: 'paid',
          paid_at: new Date().toISOString(),
        })
        .eq('gateway_charge_id', chargeId)
        .neq('status', 'paid') // Evita disparos duplicados se já estiver pago
        .select('order_id')
        .single();

      if (pixTx?.order_id) {
        // Marca o pedido ou agendamento como confirmado
        await supabase
          .from('orders')
          .update({ status: 'paid' })
          .eq('id', pixTx.order_id);

        // Desencadeia notificação WhatsApp / Email aqui
      }
    }

    return NextResponse.json({ received: true });
  } catch (err: any) {
    console.error('Erro no webhook Pix:', err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
```

---

## 5. Componente de UI: Modal de Checkout Pix com Timer e Auto-Copy

```tsx
// components/checkout/pix-modal.tsx
'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import { Check, Copy, Clock, Loader2 } from 'lucide-react';

interface PixModalProps {
  qrCodeBase64: string;
  copyPasteCode: string;
  expiresInSeconds?: number;
  onPaid: () => void;
  orderId: string;
}

export function PixModal({ qrCodeBase64, copyPasteCode, expiresInSeconds = 900, onPaid, orderId }: PixModalProps) {
  const [copied, setCopied] = useState(false);
  const [secondsLeft, setSecondsLeft] = useState(expiresInSeconds);

  // Timer regressivo
  useEffect(() => {
    if (secondsLeft <= 0) return;
    const interval = setInterval(() => setSecondsLeft((prev) => prev - 1), 1000);
    return () => clearInterval(interval);
  }, [secondsLeft]);

  // Polling de verificação de pagamento a cada 4s
  useEffect(() => {
    if (secondsLeft <= 0) return;
    const pollInterval = setInterval(async () => {
      const res = await fetch(`/api/orders/${orderId}/status`);
      const data = await res.json();
      if (data.status === 'paid') {
        clearInterval(pollInterval);
        onPaid();
      }
    }, 4000);
    return () => clearInterval(pollInterval);
  }, [orderId, secondsLeft, onPaid]);

  const handleCopy = () => {
    navigator.clipboard.writeText(copyPasteCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 3000);
  };

  const minutes = Math.floor(secondsLeft / 60);
  const seconds = secondsLeft % 60;

  return (
    <div className="bg-card text-card-foreground p-6 rounded-2xl border shadow-xl max-w-md w-full mx-auto space-y-5">
      <div className="text-center space-y-1">
        <h3 className="text-xl font-bold">Pague com Pix</h3>
        <p className="text-sm text-muted-foreground">Abra o app do seu banco e escaneie o QR Code abaixo</p>
      </div>

      <div className="flex justify-center p-4 bg-white rounded-xl border w-fit mx-auto">
        <img
          src={`data:image/png;base64,${qrCodeBase64}`}
          alt="QR Code Pix"
          className="w-56 h-56 object-contain"
        />
      </div>

      <div className="flex items-center justify-center gap-2 text-sm font-medium text-amber-600 bg-amber-500/10 py-2 rounded-lg">
        <Clock className="w-4 h-4" />
        <span>Válido por: {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}</span>
      </div>

      <div className="space-y-2">
        <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Pix Copia e Cola</label>
        <div className="flex gap-2">
          <input
            readOnly
            value={copyPasteCode}
            className="flex-1 bg-muted px-3 py-2 text-xs rounded-lg border font-mono truncate select-all"
          />
          <button
            onClick={handleCopy}
            className="px-4 py-2 bg-primary text-primary-foreground font-medium rounded-lg text-sm flex items-center gap-2 hover:opacity-90 transition-all"
          >
            {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            {copied ? 'Copiado!' : 'Copiar'}
          </button>
        </div>
      </div>

      <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
        <Loader2 className="w-3.5 h-3.5 animate-spin" />
        <span>Identificando pagamento em tempo real...</span>
      </div>
    </div>
  );
}
```

---

## 6. Split de Pagamento (Parceiros & Barbeiros/Prestadores)

Em modelos onde o prestador recebe percentual direto (ex: 70% barbeiro, 30% plataforma):
- No Asaas ou Mercado Pago, utilize o recurso de **Split**.
- Configure o `walletId` da conta do prestador e a taxa percentual ou fixa.
- Garanta que se o estorno for solicitado, a plataforma debite proporcionalmente de cada carteira.
