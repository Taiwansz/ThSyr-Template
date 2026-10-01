---
name: mobile-first-design-system
description: Diretrizes canônicas de design, ergonomia e auditoria visual Mobile First para aplicações web de alto padrão estético.
---

# Mobile First Design System & Ergonomia Visual

## 1. Princípios de Acessibilidade Tátil e Ergonomia (Fitts's Law)
- **Touch Target Mínimo:** Todo elemento interativo (botões, links, selects, switches, ícones clicáveis) DEVE possuir área mínima de toque de 44x44px.
- **Espaçamento e Prevenção de Toque Acidental:** Margem mínima de 8px entre alvos adjacentes.
- **Inputs em Dispositivos Móveis:** Campos de texto (`input`, `textarea`, `select`) DEVEM ter `font-size: 16px` no mínimo em telas mobile para impedir o zoom automático invasivo do iOS Safari.

## 2. Integridade de Viewport e Tolerância Zero a Overflow Horizontal
- **Corte Estrito:** `html, body` devem ter `max-width: 100%` e `overflow-x: clip` (ou `hidden`).
- **Elementos Absolutos e Transformações:** Decorações que usam `scale()` ou offsets negativos não podem expandir o scroll horizontal do documento.

## 3. Transparência de Decisão antes de Ações Irreversíveis
- **Acesso Antecipado a Dados:** Se um fluxo exige que o usuário reserve ou bloqueie um recurso compartilhado (ex: itens de inventário ou vagas compartilhadas), ele DEVE ter acesso prévio claro e desimpedido a links externos, preços e especificações técnicas ANTES de submeter seu nome ou confirmação.

## 4. Composição Editorial e Não-Colisão
- **Imagens e Florais:** Ilustrações decorativas nunca devem cobrir textos centrais, nomes próprios ou escrituras sagradas. Em viewports móveis, limitar dimensões a no máximo 55% da largura e ancorar estritamente aos cantos do cartão.

## 5. Orquestração de Animação e Intersecção Segura
- **Tolerância a Rolagem Rápida:** Sistemas de animação baseados em `IntersectionObserver` devem utilizar `threshold: 0` e margens de gatilho generosas (`rootMargin: "80px 0px 80px 0px"`). Elementos já ultrapassados pela rolagem (`rect.bottom < 0`) devem ser forçados para o estado visível imediatamente, prevenindo textos presos em `clip-path` ou `opacity: 0`.

## 6. Agrupamento de Ações Móveis (Foco Primário + Secundários)
- **Trios de Ação (ex: Maps / Waze / Uber):** Em viewports móveis, nunca quebrar um botão e dois links soltos de forma assimétrica. Utilizar grid ordenado com botão primário em largura total (100%) e botões secundários em colunas equilibradas (50%/50%) com 44px de altura mínima e cantos arredondados consistentes.

## 7. Prevenção de Microtipografia e Legibilidade no Rodapé
- **Piso Tipográfico de Leitura:** Nenhum texto legível ou link deve ter `font-size` inferior a 11px em viewports móveis. Metadados e datas devem manter contraste mínimo de 4.5:1 sobre o fundo.

## 8. Resiliência de APIs e Fallback Sem Banco de Dados
- **Disponibilidade Contínua:** Endpoints de catálogo e dados públicos nunca devem estourar 500 caso serviços de persistência secundários (PostgreSQL/Neon) estejam indisponíveis. Devem retornar listas vazias ou dados estáticos cacheados graciosamente.
