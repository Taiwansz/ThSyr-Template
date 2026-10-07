---
name: core-web-vitals-guardian
description: "High-performance Core Web Vitals engineering skill for Next.js and web applications. Guarantees 95+ mobile PageSpeed scores even with rich animations: enforces zero layout shifts (CLS < 0.05), sub-2.5s LCP via next/font optimization and priority image loading, and sub-200ms INP via third-party script offloading."
argument-hint: "[audit | lcp | cls | inp | fonts]"
license: MIT
metadata:
  author: Code Makers & PromptVault
  version: "1.0.0"
---

# Core Web Vitals Guardian — Performance 95+ no Mobile

#categoria-code #performance #core-web-vitals #lighthouse #nextjs #seo #velocidade

Com o catálogo de 73 animações e bibliotecas visuais ricas, a tendência natural de uma IA sem supervisão é degradar a velocidade de carregamento. Um site lento destrói as conversões e anula o trabalho das suas 25 skills de SEO.

Esta skill atua como sentinela de performance, garantindo nota **95+ no Google PageSpeed Insights (Mobile)**.

---

## 1. As 3 Métricas Vitais e Suas Regras de Ouro

| Métrica | Meta Mobile | O que quebra | Como consertar |
| :--- | :--- | :--- | :--- |
| **LCP** *(Largest Contentful Paint)* | **< 2.5s** | Hero image pesada, fontes externas que bloqueiam renderização. | `priority` na imagem do hero, fontes locais com `next/font`, compressão WebP/AVIF. |
| **CLS** *(Cumulative Layout Shift)* | **< 0.05** | Imagens sem dimensões explícitas, banners que "empurram" o conteúdo após carregar. | Containers com `aspect-ratio` fixo, skeletons de loading com dimensões idênticas ao card real. |
| **INP** *(Interaction to Next Paint)* | **< 200ms** | Scripts de terceiros (Pixel, GTM) travando a thread principal do navegador. | Offloading com `@next/third-parties`, Web Workers (Partytown), debouncing em inputs. |

---

## 2. Otimização de Fontes com `next/font` (Zero FOIT / Zero Layout Shift)

> [ERRO] **BANIDO:** Usar `<link href="https://fonts.googleapis.com/css2?family=..." rel="stylesheet">` no `<head>`. Isso adiciona 2 roundtrips de rede antes de qualquer texto aparecer na tela.

> [OK] **OBRIGATÓRIO:** Usar `next/font/google` ou `next/font/local` com subsets reduzidos:

```tsx
// app/layout.tsx
import { Geist, Geist_Mono } from 'next/font/google';

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
  display: 'swap', // Garante que o texto renderiza imediatamente com fonte fallback
});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className={geistSans.variable}>
      <body className="antialiased font-sans">{children}</body>
    </html>
  );
}
```

---

## 3. A Imagem do Hero (A Regra do LCP)

A imagem principal da primeira dobra da página é quase sempre o elemento de LCP. Ela deve ser tratada como prioridade máxima de rede:

```tsx
import Image from 'next/image';

export function HeroSection() {
  return (
    <section className="relative w-full min-h-[80vh] flex items-center justify-center">
      {/* Imagem de Fundo com Prioridade */}
      <Image
        src="/assets/hero-bg.webp"
        alt="Ambiente da Barbearia JaoBarber"
        fill
        priority // Força pré-carregamento imediato no HTML inicial
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 1920px"
        className="object-cover object-center -z-10"
        quality={80} // 80% é indistinguível de 100% para o olho humano e pesa 60% menos
      />

      <div className="max-w-4xl mx-auto text-center px-4">
        <h1 className="text-5xl font-bold tracking-tight">Corte Impecável no Seu Tempo</h1>
      </div>
    </section>
  );
}
```

---

## 4. Scripts de Terceiros sem Travar o Navegador (Google Tag Manager & Meta Pixel)

Nunca insira scripts brutos com `<script src="...">` em Next.js. Utilize o pacote oficial `@next/third-parties`:

```bash
npm install @next/third-parties
```

```tsx
// app/layout.tsx
import { GoogleTagManager } from '@next/third-parties/google';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>
        {children}
        {/* Carregamento assíncrono após interatividade (não afeta LCP nem INP) */}
        {process.env.NEXT_PUBLIC_GTM_ID && (
          <GoogleTagManager gtmId={process.env.NEXT_PUBLIC_GTM_ID} />
        )}
      </body>
    </html>
  );
}
```
