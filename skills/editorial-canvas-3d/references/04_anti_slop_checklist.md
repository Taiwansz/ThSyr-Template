# Checklist de Verificação Pré-Voo Anti-Slop (DoD)

Antes de homologar qualquer apresentação gerada no padrão **Editorial Canvas 3D**, todos os critérios abaixo devem receber status binário **PASS**. Qualquer falha impede a entrega ao operador.

---

## 1. Integridade Semântica e Anti-Mediocridade

- [ ] **Zero Emojis (0 Emojis):** Varredura completa no arquivo HTML (títulos, parágrafos, código inline, comentários JS e metadados). Nenhum caractere Unicode de emoji pode existir.
- [ ] **Ausência de Pílulas de Texto de IA (`rounded-full`):** Nenhuma tag, categoria ou subtítulo está encapsulado em badges ovais flutuantes. As tags devem ser retângulos técnicos com `.tag i`.
- [ ] **Ausência de AI-Purple / Sparkles:** Sem gradientes roxo/magenta clichê, sem ícones de estrelinha ou varinha mágica.
- [ ] **Fidelidade ao Domínio (Zero Tech Contamination):** Se o tema for negócios, varejo, artesanal ou acadêmico, o design reflete as metáforas do próprio domínio (não usa switches de rack ou barras de carregamento de videogame onde não cabem).

---

## 2. Motor Gráfico e Performance (Canvas 2D)

- [ ] **Zero Dependências 3D Externas:** O arquivo HTML não contém `<script src="...three.js">` ou imports externos de renderizadores pesados.
- [ ] **Alocação Prévia Contígua:** As coordenadas estão em `Float32Array` pré-alocados. O loop `requestAnimationFrame` não instancia objetos pesados por frame.
- [ ] **Revelação Progressiva no Hero ($S_0$):** O estado inicial possui centro desobstruído (`seedA[i] > rpow`), permitindo leitura limpa da tipografia monumental.
- [ ] **Híbrido Vetorial Ativo:** O Canvas desenha ativamente arestas vetoriais com `gx.stroke()` e rótulos tipográficos projetados em `gx.fillText()` em pelo menos três estados chave.
- [ ] **Compensação Off-Axis:** O centro de projeção da câmera move-se horizontalmente (`OFFS`) para compensar a posição do bloco de texto em telas desktop.

---

## 3. Tipografia e Microinterações Apple Design

- [ ] **Combinação Tipográfica Homologada:** `Schibsted Grotesk` (Google Fonts) em 900/800 nos títulos e `JetBrains Mono` em 700/800 nos dados tabulares e tags.
- [ ] **Números Tabulares:** Números métricos dominantes (`.n`) e valores da tabela (`.v`) possuem `font-variant-numeric: tabular-nums`.
- [ ] **Feedback Tátil `:active`:** Tags, itens de fatos (`.facts div`) e dicas de rolagem comprimem suavemente em `:active` (`scale(0.96)` a `scale(0.985)`).
- [ ] **Acessibilidade a Movimento:** Suporte mandatório a `@media (prefers-reduced-motion: reduce)`, parando a rotação autônoma do Canvas e zerando transições CSS.
- [ ] **Responsividade Mobile:** Suporte a telas `< 760px` com redução automática para 3.072 partículas e ajuste do offset da câmera.

---

## 4. Evidências Obrigatórias

- [ ] **Auditoria Algorítmica:** Execução de `python -m engine.visual.cli audit <arquivo.html>` com nota 100/100.
- [ ] **Captura Visual com Playwright:** Screenshots em resolução real 1440x900 capturados em múltiplos estados e inspecionados antes da entrega.
- [ ] **Auditoria por Subagente:** Parecer de homologação emitido pelo subagente especialista `frontend_craft_auditor`.
