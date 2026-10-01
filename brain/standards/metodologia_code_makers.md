# Metodologia Canônica Code Makers: Governança de Projetos com IA & Motion Design

Manual canônico de governança executiva, arquitetura de software, ciclo de vida de projetos e biblioteca de animações avançadas da Code Makers.

---

## 1. Princípio Fundamental e Regra de Ouro

> **"PRIMEIRO ENTENDER. DEPOIS PLANEJAR. SÓ ENTÃO EXECUTAR."**

A improvisação é proibida. Nenhum arquivo de código, schema de banco ou componente de interface deve ser criado antes do encerramento e aprovação formal do estágio anterior.

---

## 2. O Processo Obrigatório em 3 Etapas (Hard Gates)

Qualquer iniciativa técnica desenvolvida pelo ThSyr ou em conjunto com o operador deve respeitar 3 portões de validação estritos:

### Etapa 1 — Diagnóstico e Definição do Projeto
- **Objetivo:** Entender profundamente o negócio, nicho, dores, público-alvo, diferencial competitivo e regras críticas antes de qualquer proposta técnica.
- **Entradas Obrigatórias:**
  - Identidade e marca: Logos em todas as variações, manuais, paletas, tipografia e diretrizes de design.
  - Contexto de negócio: Oferta central, objetivos de conversão, integrações prévias e restrições técnicas/financeiras.
  - Materiais brutos: Textos, planilhas, notas desestruturadas e requisitos funcionais.
- **O que a IA deve gerar:**
  1. Visão executiva sintetizada do produto.
  2. Público-alvo, dores centrais e diferenciais inegociáveis.
  3. Mapeamento de regras de negócio preliminares.
  4. Delimitação estrita do escopo (o que faz vs. o que NÃO faz na versão 1).
  5. **Portão de Saída (Hard Gate):** Identificação e isolamento obrigatório de **3 a 5 perguntas bloqueantes críticas** que impedem o avanço seguro para a arquitetura.

### Etapa 2 — Arquitetura, Planejamento e Solução
- **Objetivo:** Transformar o diagnóstico aprovado em um blueprint técnico detalhado, eliminando qualquer decisão aberta durante a implementação.
- **Entregáveis Obrigatórios:**
  1. **Arquitetura de Navegação:** Mapa completo de páginas, telas, rotas (`app/`), layouts e estados vazios/erro.
  2. **Modelagem de Dados Relacional:** Tabelas do PostgreSQL/Supabase, chaves primárias/estrangeiras, tipos de dados estritos, enums e índices.
  3. **Segurança e RLS:** Políticas de Row Level Security explícitas para cada operação (SELECT, INSERT, UPDATE, DELETE), separação multi-tenant e triggers com `SECURITY DEFINER`.
  4. **Fluxos de Integração e APIs:** Contratos de Server Actions, endpoints de webhooks com verificação de assinatura/HMAC e tratamento de idempotência.
  5. **Component Tree & Design System:** Hierarquia de componentes (Server vs. Client Components), tokens de cor, tipografia e biblioteca de componentes reutilizáveis.
  6. **Checklist Pré-Voo de 8 Pontos:** Validação cruzada de regras, permissões, escalabilidade e conformidade legal (LGPD).

### Etapa 3 — Execução Controlada em Ciclos Cirúrgicos
- **Objetivo:** Construção em blocos atômicos e progressivos. Proibido tentar gerar sistemas inteiros em um único passo.
- **Ordem de Construção Mandatória:**
  1. *Fundação:* Estrutura de diretórios, configurações de ambiente (`.env.example`), providers globais e layout base.
  2. *Dados, Autenticação e Segurança:* Migrations idempotentes, autenticação, policies RLS e funções de banco.
  3. *Módulos Centrais:* Telas e componentes principais alimentados por dados reais.
  4. *Integrações e Webhooks:* Gateways de pagamento, disparos transacionais e APIs de terceiros.
  5. *Acabamento Visual, Motion e Micro-interações:* Aplicação do design system, biblioteca de animações GSAP e polimento tipográfico.
  6. *Responsividade Multi-Viewport:* Validação explícita em Desktop (1440px) e Mobile (390px).
- **Ciclo Operacional Contínuo:**
  $$\text{Implementar} \longrightarrow \text{Testar} \longrightarrow \text{Validar} \longrightarrow \text{Corrigir} \longrightarrow \text{Commitar}$$

---

## 3. Protocolos de Sustentação, QA e Emergência

### Prompt 4 — Auditoria / QA Final Pré-Produção
Auditoria sistemática obrigatória antes de qualquer deploy em produção. Classificação de apontamentos por severidade:
- **Crítico (P0):** Falhas de segurança, bypass de RLS, vazamento de dados de outros usuários/tenants, quebra de login ou falhas em cobrança/pagamentos. Bloqueia o deploy.
- **Alto (P1):** Quebra de regra de negócio central, perda de dados não crítica ou erros bloqueantes de navegação em rotas secundárias.
- **Médio (P2):** Erros visuais visíveis, layout quebrado em viewports móveis, inconsistência de tipografia ou ausência de loading states.
- **Baixo (P3):** Micro-ajustes de espaçamento, otimizações de animação ou refinamentos de microcopy.

### Prompt 5 — Protocolo de Hotfix Cirúrgico
Aplicado quando ocorre um incidente em ambiente de homologação ou produção:
1. **Isolamento de Causa-Raiz:** Reproduzir o erro e identificar com precisão a camada afetada (Frontend, Server Action, Banco/RLS, Integração ou Deploy).
2. **Princípio do Menor Escopo:** Corrigir estritamente o ponto de ruptura.
3. **Proibição de Refatoração Lateral:** É terminantemente proibido refatorar componentes adjacentes, reescrever arquitetura funcional estável ou introduzir novas bibliotecas durante um hotfix.
4. **Verificação de Regressão:** Validar que a correção não introduziu efeitos colaterais nas rotas vizinhas antes do commit.

### Auditoria de Segurança & LGPD
- **Políticas RLS:** Nenhuma tabela do PostgreSQL pode ficar sem Row Level Security habilitado. Utilização mandatória de queries eficientes indexadas via `EXISTS` para evitar varreduras sequenciais completas.
- **Funções de Banco:** Triggers e functions executadas com privilégios elevados devem conter explicitamente `SECURITY DEFINER` e `SET search_path = ''` para blindagem contra injeção de schema.
- **Higiene de Segredos:** Tokens de `service_role` ou chaves privadas jamais trafegam no bundle de cliente. Uso exclusivo em Server Actions ou Edge Functions.
- **LGPD:** Dados de identificação pessoal (PII) sensíveis protegidos, ausência de senhas em texto puro e sanitização estrita de payloads em logs.

---

## 4. Biblioteca de Movimentos (73 Nomenclaturas de Motion)

Estrutura formal de animação e interação para produtos digitais premium, fundamentada em GPU hardware-acceleration (60fps) e respeito à acessibilidade (`prefers-reduced-motion`).

### Categoria 01: Animações Essenciais (15 termos)
Entradas, saídas e transições estruturais de interface:
1. `Fade In`: Revelação suave de opacidade ($0 \to 1$).
2. `Fade Out`: Ocultação gradual de elemento ($1 \to 0$).
3. `Slide In`: Entrada com translação linear lateral ou vertical.
4. `Slide Out`: Saída com translação para fora do viewport.
5. `Scale Up`: Crescimento suave de escala ($0.8 \to 1.0$).
6. `Scale Down`: Redução dimensional controlada.
7. `Rotate`: Rotação angular em graus (2D ou 3D).
8. `Stagger`: Intervalo cascateado entre elementos de uma lista ou grid.
9. `Reveal`: Revelação progressiva de conteúdo por máscara ou clippath.
10. `Flip`: Rotação de 180° simulando elemento com frente e verso.
11. `Bounce`: Efeito de repique com curva elástica ao final do percurso.
12. `Pulse`: Variação cíclica sutil de escala para atrair atenção (CTAs).
13. `Shake`: Oscilação rápida horizontal para feedback de erro.
14. `Blur In`: Transição combinada de desfoque gaussiano para nitidez.
15. `Accordion`: Expansão e retração vertical de altura em listas retráteis.

### Categoria 02: Animações de Rolagem / Scroll (9 termos)
Movimentos orquestrados pela progressão de scroll do usuário:
1. `Scroll Trigger`: Ativação de timeline vinculada a marcadores de scroll.
2. `Scrub`: Sincronização direta de scrubbing entre a rolagem e o progresso da animação.
3. `Pinning`: Fixação de seção ou elemento enquanto o conteúdo interno transita.
4. `Parallax`: Deslocamento diferencial de camadas em velocidades assimétricas.
5. `Horizontal Scroll`: Conversão de rolagem vertical em deslocamento lateral.
6. `Progress Bar`: Barra indicadora do progresso total de leitura ou navegação.
7. `Batch`: Agrupamento de gatilhos para otimizar renderização de listas densas.
8. `Toggle Class`: Aplicação e remoção dinâmica de classes CSS conforme visibilidade.
9. `Velocity`: Ajuste dinâmico de intensidade e inércia baseado na velocidade de rolagem.

### Categoria 03: Animações de Tipografia e Texto (9 termos)
Expressão visual de títulos editoriais e frases de alto impacto:
1. `Split Text`: Fatiamento de strings em letras, palavras ou linhas independentes.
2. `Character Stagger`: Entrada sequenciada caractere por caractere.
3. `Word Reveal`: Aparição palavra por palavra com máscara inferior.
4. `Line Mask`: Revelação suave linha por linha ocultando overflow.
5. `Scramble Text`: Efeito de decodificação criptográfica de caracteres aleatórios.
6. `Typewriter`: Simulação realista de digitação mecânica.
7. `Counter`: Incremento numérico animado para estatísticas e métricas.
8. `Text Highlight`: Animação de marcação de texto simulando marca-texto sutil.
9. `Kinetic Typography`: Tipografia cinética expressiva com distorção elástica.

### Categoria 04: Interações com o Usuário (11 termos)
Feedback físico e responsividade a gestos e ponteiros:
1. `Hover Animation`: Resposta estética ao passar do cursor.
2. `Magnetic Button`: Botão com atração magnética em direção ao cursor do mouse.
3. `Cursor Follower`: Elemento visual customizado que rastreia suavemente o ponteiro.
4. `3D Tilt`: Inclinação tridimensional de cards baseada na posição do ponteiro.
5. `Ripple Effect`: Onda de choque circular expansiva ao clique.
6. `Drag & Drop`: Arraste físico de elementos com física de mola e encaixe.
7. `Toggle Switch`: Transição orgânica entre estados binários (on/off, dark/light).
8. `Micro-Interaction`: Micro-respostas táteis em ícones e botões.
9. `Card Stack`: Empilhamento interativo de cartões com descarte ou transição.
10. `Swipe`: Mudança fluida de itens via gesto de deslizamento lateral.
11. `Tooltip Reveal`: Aparição contextual e posicionada de dicas flutuantes.

### Categoria 05: Efeitos Avançados e Cinematográficos (17 termos)
Técnicas de alto nível para interfaces imersivas e cinematográficas:
1. `Page Transition`: Transição contínua e sem flash entre rotas.
2. `Horizontal Section`: Seção horizontal imersiva inserida em layout vertical.
3. `Mask Reveal`: Revelação complexa usando formas geométricas SVG como máscara.
4. `Sticky Header`: Cabeçalho inteligente que minimiza e fixa na rolagem.
5. `Zoom on Scroll`: Zoom-in cinematográfico sobre imagem de destaque.
6. `Parallax Layering`: Sobreposição profunda de 3 ou mais camadas em profundidades distintas.
7. `Infinite Marquee`: Faixa contínua e infinita de logos, textos ou selos.
8. `SVG Path Animation`: Desenho progressivo do contorno de vetores e ilustrações.
9. `Canvas Particle`: Partículas dinâmicas e interativas renderizadas em Canvas/WebGL.
10. `Liquid Transition`: Transição fluida com estética viscosa ou hidrodinâmica.
11. `Distortion Effect`: Distorções de textura e filtros aplicados via shaders.
12. `Glassmorphism Movement`: Camadas translúcidas com desfoque de fundo em movimento.
13. `Dark/Light Transition`: Transição global de paleta cromática sem flicker.
14. `Sound-Reactive Motion`: Animação calibrada por frequências ou eventos sonoros.
15. `Shimmer / Skeleton`: Efeito metálico pulsante de carregamento sobre placeholders.
16. `Glow Effect`: Brilho difuso ativado por proximidade ou foco.
17. `Noise & Grain`: Camada sutil de textura granulada analógica animada.

### Categoria 06: Termos e APIs Centrais do GSAP (12 termos)
Primitivas técnicas da biblioteca GreenSock Animation Platform:
1. `Tween`: Unidade básica atômica de animação entre estados.
2. `Timeline`: Orquestrador temporal sequencial e aninhado de múltiplos Tweens.
3. `Easing`: Curva de aceleração e desaceleração matemática (ex: `power3.out`, `expo.inOut`).
4. `Duration`: Duração temporal explícita em segundos.
5. `Delay`: Intervalo de espera antes do início do movimento.
6. `Stagger (API)`: Propriedade nativa para controle de atraso distributivo.
7. `ScrollTrigger (Plugin)`: Motor central de integração de timelines com o scroll.
8. `Observer`: Normalizador de eventos de rolagem, toque e ponteiro.
9. `Flip (Plugin)`: Técnica First-Last-Invert-Play para transições de layout sem recalculação pesada de DOM.
10. `MorphSVG`: Transformação matemática contínua entre dois caminhos vetoriais distintos.
11. `DrawSVG`: Revelação progressiva do preenchimento de traços em vetores SVG.
12. `SplitText (Plugin)`: Quebra nativa de strings para animações tipográficas atômicas.

---

## 5. Combinações Canônicas por Arquétipo de Projeto

- **Visual Limpo (SaaS / B2B):** `Fade In` + `Slide In suave` + `Stagger` moderado + `Micro-interactions`.
- **Landing Page de Alta Conversão:** `Scroll Trigger` + `Word Reveal` no Hero + `Parallax sutil` + `Magnetic Button` no CTA principal.
- **Portfólio / Identidade de Alto Padrão:** `Page Transition` contínua + `3D Tilt` em cards + `Infinite Marquee` de selos + `Split Text`.
- **Dashboard Operacional:** `Shimmer/Skeleton` em estados de carregamento + `Counter` em KPIs + `Accordion` em painéis laterais.

## Sinapses
- Conectado a [[Cortex_Central]].
- Conectado a [[Padroes_Engenharia]].
