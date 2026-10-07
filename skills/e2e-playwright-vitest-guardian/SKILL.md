---
name: e2e-playwright-vitest-guardian
description: "End-to-end and integration testing guardian using Playwright and Vitest for Next.js applications. Automates pre-production QA checklists, enforces multi-viewport validation (Desktop 1440px vs Mobile 390px), zero-console-error policies, authentication state testing, network mocking, and automated accessibility scans with Axe."
argument-hint: "[playwright | vitest | e2e | smoke-test | accessibility | ci]"
license: MIT
metadata:
  author: Code Makers & PromptVault
  version: "1.0.0"
---

# E2E & Integration QA Guardian (Playwright + Vitest)

#categoria-code #testes #e2e #playwright #vitest #qa #smoke-test #qualidade

Esta skill rege a criação, execução e automação de testes End-to-End (E2E) com **Playwright** e testes unitários/integração com **Vitest**. Ela transforma o **Checklist Pré-Produção dos 19 Itens** em uma bateria automatizada que impede que telas quebradas em mobile, erros silenciosos no console ou falhas de autenticação cheguem aos usuários finais.

---

## 1. Princípios de Ouro dos Testes em Aplicações com IA

1. **Dual-Viewport Obrigatório:** Todo teste E2E crítico deve rodar em pelo menos duas resoluções:
   - **Desktop:** Viewport padrão `1440x900`.
   - **Mobile:** Emulação de dispositivo móvel moderno (iPhone 14 / Viewport `390x844`).
2. **Zero Console Errors:** Durante a execução de qualquer teste de página, o Playwright deve escutar eventos de console. Qualquer `console.error` ou erro não capturado de hidratação deve reprovar o teste imediatamente.
3. **Resiliência a Seletores (Testing Library Mindset):** Proibido usar classes de CSS voláteis (`.css-123xyz` ou `.flex-col`) para encontrar elementos. Use exclusivamente:
   - `page.getByRole('button', { name: /entrar/i })`
   - `page.getByLabel('E-mail')`
   - `page.getByTestId('checkout-modal')`
4. **Isolamento de Estado:** Testes devem rodar com dados isolados ou fixtures limpas, nunca dependendo da execução prévia de outro teste.

---

## 2. Configuração Padrão do Playwright (`playwright.config.ts`)

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['html'], ['list']],
  use: {
    baseURL: process.env.PLAYWRIGHT_TEST_BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'Desktop Chrome (1440px)',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1440, height: 900 },
      },
    },
    {
      name: 'Mobile Safari (390px)',
      use: {
        ...devices['iPhone 14'],
        viewport: { width: 390, height: 844 },
      },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
```

---

## 3. Bateria E2E de Auditoria Pré-Produção (`e2e/smoke.spec.ts`)

Este teste executa o crivo de conformidade da página inicial e fluxos críticos:

```typescript
// e2e/smoke.spec.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Bateria de Smoke Test e Quality Gate', () => {
  test('A página inicial não pode emitir erros no console', async ({ page }) => {
    const consoleErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    page.on('pageerror', (exception) => {
      consoleErrors.push(exception.message);
    });

    await page.goto('/');

    // Aguardar hidratação completa
    await expect(page.locator('main')).toBeVisible();

    // Validar ausência de erros de console/hidratação
    expect(consoleErrors, `Erros encontrados no console:\n${consoleErrors.join('\n')}`).toHaveLength(0);
  });

  test('Responsividade: Não deve haver overflow horizontal no mobile', async ({ page }) => {
    await page.goto('/');

    const hasHorizontalScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > window.innerWidth;
    });

    expect(hasHorizontalScroll, 'A página vazou horizontalmente (overflow horizontal no viewport)').toBeFalsy();
  });

  test('Acessibilidade básica (WCAG AA via Axe)', async ({ page }) => {
    await page.goto('/');

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .disableRules(['color-contrast']) // Ajuste conforme a identidade visual
      .analyze();

    expect(accessibilityScanResults.violations).toEqual([]);
  });
});
```

---

## 4. Teste de Fluxo Crítico: Autenticação e Proteção de Rotas

```typescript
// e2e/auth-flow.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Fluxo de Autenticação e Rotas Protegidas', () => {
  test('Deve redirecionar usuário não autenticado para /login ao acessar /dashboard', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/.*login/);
    await expect(page.getByRole('heading', { name: /entrar/i })).toBeVisible();
  });

  test('Deve exibir erro amigável ao tentar login com credenciais inválidas', async ({ page }) => {
    await page.goto('/login');

    await page.getByLabel(/e-mail/i).fill('usuario_inexistente@teste.com');
    await page.getByLabel(/senha/i).fill('senha_errada_123');
    await page.getByRole('button', { name: /entrar/i }).click();

    // Aguardar feedback visual de erro
    const alert = page.getByRole('alert');
    await expect(alert).toBeVisible();
    await expect(alert).toContainText(/credenciais inválidas|e-mail ou senha incorretos/i);
  });
});
```

---

## 5. Vitest para Testes Unitários de Server Actions & Regras de Negócio

Instalação:
```bash
npm install -D vitest @vitejs/plugin-react jsdom
```

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

### Teste de Validação de Input e Schemas Zod:
```typescript
// tests/validation.test.ts
import { describe, it, expect } from 'vitest';
import { z } from 'zod';

const createAppointmentSchema = z.object({
  customerId: z.string().uuid(),
  serviceId: z.string().uuid(),
  startsAt: z.string().datetime(),
  customerCpf: z.string().regex(/^\d{11}$/, 'CPF deve conter 11 dígitos numéricos'),
});

describe('Validação de Dados de Agendamento', () => {
  it('deve aprovar payload válido', () => {
    const validData = {
      customerId: 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
      serviceId: 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22',
      startsAt: '2026-03-20T14:30:00Z',
      customerCpf: '12345678901',
    };

    const result = createAppointmentSchema.safeParse(validData);
    expect(result.success).toBe(true);
  });

  it('deve rejeitar CPF com formatação inválida', () => {
    const invalidData = {
      customerId: 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
      serviceId: 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22',
      startsAt: '2026-03-20T14:30:00Z',
      customerCpf: '123.456.789-01', // Com pontuação quando esperado somente dígitos
    };

    const result = createAppointmentSchema.safeParse(invalidData);
    expect(result.success).toBe(false);
  });
});
```

---

## 6. Pipeline de CI no GitHub Actions (`.github/workflows/qa.yml`)

Para travar commits que quebram a aplicação:

```yaml
name: QA & Smoke Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'

      - name: Instalar dependências
        run: npm ci

      - name: Executar Vitest (Unitários)
        run: npm run test:unit

      - name: Instalar browsers Playwright
        run: npx playwright install --with-deps

      - name: Executar Playwright (E2E)
        run: npm run test:e2e
```
