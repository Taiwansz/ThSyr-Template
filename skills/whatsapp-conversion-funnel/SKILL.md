---
name: whatsapp-conversion-funnel
description: "High-converting WhatsApp sales and booking funnel skill for service businesses (barbershops, dental clinics, law firms, restaurants). Includes dynamic context-aware pre-filled WhatsApp link generators, UTM campaign tracking injection into chat text, anti-no-show automated appointment reminder copy, and Google Review reputation boosters."
argument-hint: "[service | niche | booking-type]"
license: MIT
metadata:
  author: Code Makers & PromptVault
  version: "1.0.0"
---

# WhatsApp Conversion Funnel — Máquina de Vendas & Agendamento

#categoria-cowork #whatsapp #vendas #conversao #negocios-locais #agendamento

No mercado brasileiro, **mais de 90% das conversões** de pequenos e médios negócios (barbearias, clínicas odontológicas, escritórios de advocacia e restaurantes) acontecem pelo WhatsApp. 

Esta skill governa a criação de links dinâmicos contextualizados, rastreamento de origem de campanhas, redução drástica de faltas (*anti-no-show*) e captação de avaliações 5 estrelas no Google.

---

## 1. A Regra do Link Contextualizado (Fim do "Olá, gostaria de informações")

> [ERRO] **O ERRO CLÁSSICO:** Colocar um botão flutuante com link `https://wa.me/5511999999999` sem mensagem ou com texto genérico. O atendente não sabe de onde o cliente veio, nem o que ele quer.

> [OK] **O PADRÃO DE ALTA CONVERSÃO:** A mensagem inicial deve ser pré-preenchida dinamicamente com base no **botão exato** ou na **seção de serviço** onde o usuário clicou.

### Fórmula do Link Dinâmico:
$$\text{URL} = \text{https://wa.me/}[DDI + DDD + \text{Numero}]?\text{text}=[\text{Mensagem Codificada em URI}]$$

### Exemplos de Mensagens por Especialidade:
- **Para Advocacia Tributária:**
  - *"Olá! Estava no site lendo sobre Recuperação de Impostos e gostaria de saber se a minha empresa se enquadra. [Ref: Site-Advocacia]"*
- **Para Odontologia (Implantes):**
  - *"Olá, Dra.! Vi no site a explicação sobre Implantes em 3 sessões e quero agendar uma avaliação para esta semana. [Ref: Site-Odonto]"*
- **Para Barbearia:**
  - *"Fala time! Vi no site os horários disponíveis e quero garantir meu corte degradê + barba para hoje/amanhã. [Ref: Site-Barbearia]"*

---

## 2. Componente React / Next.js de CTA Flutuante com UTMs

```tsx
'use client';

import { useSearchParams } from 'next/navigation';
import { MessageCircle } from 'lucide-react';

interface WhatsAppCTAProps {
  phone: string;              // Ex: "5511999998888"
  serviceName?: string;       // Ex: "Recuperação Tributária"
  className?: string;
}

export function WhatsAppCTA({ phone, serviceName = 'Atendimento Geral', className = '' }: WhatsAppCTAProps) {
  const searchParams = useSearchParams();
  const utmSource = searchParams.get('utm_source') || 'organico';
  const utmCampaign = searchParams.get('utm_campaign') || 'site-direto';

  const textMessage = `Olá! Vi o site na seção "${serviceName}" e gostaria de atendimento. [Origem: ${utmSource} | Campanha: ${utmCampaign}]`;
  const encodedUrl = `https://wa.me/${phone}?text=${encodeURIComponent(textMessage)}`;

  return (
    <a
      href={encodedUrl}
      target="_blank"
      rel="noopener noreferrer"
      className={`fixed bottom-6 right-6 z-50 flex items-center gap-3 bg-[#25D366] text-white font-semibold px-5 py-3 rounded-full shadow-2xl hover:scale-105 active:scale-95 transition-all duration-300 ${className}`}
      aria-label="Falar no WhatsApp"
    >
      <MessageCircle className="w-6 h-6" />
      <span className="text-sm font-medium hidden sm:inline">Agendar no WhatsApp</span>
    </a>
  );
}
```

---

## 3. Scripts de Comunicação Anti-No-Show (Redução de Faltas)

O maior prejuízo de serviços com agendamento é o cliente marcar e não aparecer. Utilize estes scripts automatizados:

### Script A: Confirmação Imediata (D-0, logo após o agendamento)
> *"Perfeito, [Nome]! Seu horário para [Serviço] foi confirmado com sucesso para amanhã, às [Horário]. Nosso endereço é [Endereço + Link do Google Maps]. Caso ocorra qualquer imprevisto, por favor nos avise por aqui com pelo menos 2h de antecedência para liberarmos o profissional. Até logo!"*

### Script B: Lembrete Matinal (Manhã do Dia)
> *"Bom dia, [Nome]! Passando para lembrar do seu horário hoje às [Horário] com [Profissional]. O café já está pronto te esperando! Tudo certo para hoje? Responda apenas 'SIM' para confirmarmos."*

### Script C: Pós-Atendimento para Google Meu Negócio (+ Reviews 5 Estrelas)
> *"Olá, [Nome]! Foi um prazer te atender hoje na [Nome da Empresa]. Esperamos que tenha gostado do resultado!  Se você puder dedicar 30 segundos para deixar uma avaliação sincera no Google, nos ajuda demais: [Link Direto de Review do Google]. Muito obrigado pela confiança!"*
