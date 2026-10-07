---
name: motion-design-system
description: "Comprehensive web animation and interaction design system based on Code Makers' 73 motion nomenclatures. Categorized into Essentials (15), Scroll (9), Text (9), Interactions (11), Advanced/Cinematic (17), and GSAP APIs (12). Includes production-ready code patterns for GSAP, CSS, React, and Canvas/WebGL, along with archetype combinations for landing pages, product pages, portfolios, and mobile apps. Enforces accessibility (prefers-reduced-motion) and 60fps GPU performance."
argument-hint: "[interaction-type or archetype]"
license: MIT
metadata:
  author: Code Makers & PromptVault
  version: "1.0.0"
---

# Web Motion & Interaction Design System (73 Nomenclatures)

#categoria-code #frontend #design #motion #gsap #animacoes

Este sistema consolida a **Biblioteca de Movimentos Completa (73 Nomenclaturas)** para websites, landing pages e aplicações ricas. Ele elimina a ambiguidade na comunicação de micro-interações, transições e efeitos cinematográficos, associando termos técnicos precisos a padrões de código robustos em GSAP, React, Tailwind CSS e Canvas.

---

## 1. Princípios de Ouro do Movimento

1. **Movimento com Intenção (Hierarquia e Foco):** Nunca adicione animação apenas para preencher a tela. Toda animação deve guiar o olhar do usuário, confirmar uma ação ou narrar a proposta de valor.
2. **Escala de Intensidade (Níveis 0 a 3):**
   - **Nível 0:** Sem animação (dados críticos, formulários densos, acessibilidade).
   - **Nível 1 (CSS):** Micro-interações, hover states, active states, fade/slide de fechamento (150ms a 300ms).
   - **Nível 2 (GSAP Pontual):** Hero reveal sincronizado, ScrollTrigger scrub, pin suave, contadores numéricos e seções de assinatura.
   - **Nível 3 (Cinematográfico):** Canvas frame sequence, WebGL distortion, transição de página contínua e 3D camera.
3. **Performance Absoluta (60 FPS):**
   - Anime exclusivamente propriedades compostas pela GPU: `transform` (`x`, `y`, `scale`, `rotation`) e `opacity`.
   - **NUNCA** anime `width`, `height`, `top`, `left`, `margin` ou `padding` em loops ou scroll triggers.
   - Use `will-change` pontualmente e limpe após a animação.
   - Em React/Next.js, sempre isole e limpe timelines usando `gsap.context()` ou o hook `@gsap/react` (`useGSAP`).
4. **Acessibilidade Obrigatória:** Sempre respeite `prefers-reduced-motion: reduce`. Desative ou simplifique movimentos quando detectado.

---

## 2. O Catálogo Completo das 73 Nomenclaturas

### Categoria 01: Animações Essenciais (15 Nomenclaturas)
Entradas, saídas e revelações fundamentais de interface.

1. **Fade In:** O elemento aparece progressivamente de opacidade 0 a 1. *(Bom para: textos, imagens, cards).*
2. **Fade Out:** O elemento desaparece progressivamente até opacidade 0. *(Bom para: fechamento de modais, troca de abas).*
3. **Slide In:** O elemento entra deslizando a partir de um dos eixos (`x` ou `y`). *(Bom para: menus laterais, títulos, notificações).*
4. **Slide Out:** O elemento sai deslizando para fora da visualização. *(Bom para: toasts, gavetas, alertas).*
5. **Scale Up:** O elemento cresce suavemente a partir de uma escala menor (ex: 0.95 -> 1.0). *(Bom para: modais, botões, destaques).*
6. **Scale Down:** O elemento reduz suavemente até o tamanho original ou menor. *(Bom para: feedback de clique, fechamento).*
7. **Zoom In:** A cena ou câmera se aproxima do conteúdo. *(Bom para: imagens principais, heróis imersivos).*
8. **Zoom Out:** A cena se afasta e revela um campo visual maior. *(Bom para: transições de seção, aberturas).*
9. **Rotate In:** O elemento surge com uma leve rotação angular (ex: -10° -> 0°). *(Bom para: badges, selos, ícones criativos).*
10. **Flip:** O elemento gira 180° no eixo 3D como uma carta com frente e verso. *(Bom para: cards de produtos, pricing tables).*
11. **Bounce:** O elemento atinge a posição final com um repique amortecido. *(Bom para: notificações lúdicas, pins em mapas).*
12. **Elastic:** O movimento ultrapassa o ponto de repouso e oscila suavemente como elástico. *(Bom para: botões de ação e toques).*
13. **Stagger:** Elementos de uma mesma coleção aparecem em sequência ritmada com atraso fixo entre si. *(Bom para: grids, listas, menus).*
14. **Reveal:** O conteúdo é descoberto suavemente através de corte ou transição limpa. *(Bom para: títulos editoriais, fotos).*
15. **Mask Reveal:** Uma camada ou container de máscara (`clip-path` ou `overflow: hidden`) se move, revelando a mídia interna. *(Bom para: marcas de luxo, portfolios premium).*

---

### Categoria 02: Animações de Rolagem (09 Nomenclaturas)
Movimentos sincronizados com a rolagem da página.

16. **Scroll Trigger:** A animação é disparada quando o elemento entra no viewport em determinado gatilho.
17. **Scrub:** O progresso exato da timeline de animação é atrelado diretamente à velocidade e posição do scroll do usuário.
18. **Pin:** O elemento ou seção fica fixo na tela por uma distância pré-determinada enquanto outros elementos transitam.
19. **Parallax:** Camadas de fundo e primeiro plano se movem em velocidades distintas, criando ilusão de profundidade física.
20. **Horizontal Scroll:** O movimento vertical da roda do mouse conduz um contêiner horizontalmente ao longo da tela.
21. **Scroll Snap:** A rolagem trava suavemente na posição ideal de cada seção da página.
22. **Scroll Progress:** Uma barra, círculo ou indicador numérico mostra a porcentagem consumida da página.
23. **Section Transition:** Uma seção sobrepõe, corta ou deforma visualmente a seção anterior durante a passagem.
24. **Sticky Story:** Um elemento visual (mockup, imagem, modelo 3D) fica fixo enquanto múltiplos blocos de texto passam ao lado.

---

### Categoria 03: Animações de Texto (09 Nomenclaturas)
Manipulação tipográfica expressiva de caracteres, palavras e linhas.

25. **Split Text:** Separação do texto no DOM em `chars`, `words` ou `lines` para animação individual.
26. **Character Stagger:** As letras de uma palavra entram individualmente em rápida sequência sequencial.
27. **Word Stagger:** Palavras inteiras surgem uma após a outra em um fluxo cadenciado.
28. **Line Reveal:** Cada linha de texto é mascarada e sobe revelando-se de forma alinhada.
29. **Typewriter:** Efeito clássico simulando a digitação caractere por caractere com cursor piscante.
30. **Text Scramble:** Letras embaralhadas em caracteres aleatórios (código binário ou ascii) decodificando até formar a frase correta.
31. **Text Morph:** Interpolação suave onde uma palavra se desfaz ou se transforma organicamente em outra.
32. **Gradient Text:** Um degradê de cores animado desliza continuamente ao longo da tipografia.
33. **Marquee:** Faixa contínua e infinita de texto que corre na horizontal em velocidade constante.

---

### Categoria 04: Interações com o Usuário (11 Nomenclaturas)
Respostas diretas a eventos de mouse, toque e foco.

34. **Hover Animation:** Resposta visual imediata quando o cursor entra na área do elemento.
35. **Magnetic Button:** O botão sofre atração magnética em direção ao ponteiro do mouse quando este se aproxima.
36. **Cursor Follower:** Um círculo ou elemento gráfico customizado segue o ponteiro com física de interpolação e lag suave.
37. **3D Tilt:** O card ou elemento inclina sua perspectiva nos eixos X e Y acompanhando as coordenadas relativas do mouse.
38. **Ripple:** Onda circular expansiva que surge exatamente no ponto de contato do clique/toque.
39. **Microinteraction:** Pequeno feedback comemorativo ou informativo (ex: check que se desenha, coração pulsando).
40. **Accordion Motion:** Expansão e retração fluida de altura com interpolação de conteúdo sem saltos bruscos.
41. **Animated Counter:** Números que incrementam de zero até o valor alvo final com curva de desaceleração suave.
42. **Drag:** Capacidade do usuário arrastar o elemento livremente ou dentro de limites pré-estabelecidos.
43. **Swipe:** Detecção de gesto rápido de deslize lateral para avançar carrosséis ou descartar itens.
44. **Menu Morph:** O ícone tradicional de hambúrguer deforma seus traços até se tornar um 'X' enquanto o painel expande.

---

### Categoria 05: Efeitos Avançados e Cinematográficos (17 Nomenclaturas)
Técnicas de alto impacto visual para experiências imersivas.

45. **Page Transition:** Transição orquestrada entre rotas diferentes sem tela branca (curtain reveal, wipe, morph).
46. **Shared Element:** Um mesmo elemento (como um card ou foto) viaja e expande da tela de listagem até a tela de detalhes.
47. **FLIP Animation (First, Last, Invert, Play):** Técnica de reordenação fluida de layout quando itens são filtrados ou organizados.
48. **SVG Morph:** O caminho vetorial (`d` de um SVG path) se transforma suavemente no formato de outro SVG com mesma contagem de pontos.
49. **Motion Path:** Um elemento percorre uma curva vetorial arbitrária desenhada no espaço 2D.
50. **Draw SVG:** Efeito de traçado onde o contorno de um SVG parece ser desenhado à mão viva (`stroke-dashoffset`).
51. **Image Sequence:** Sequência de centenas de imagens renderizadas em um `<canvas>` controladas frame a frame pelo scroll do usuário.
52. **Lottie Control:** Animação rica em JSON controlada via código para avançar, retroceder ou disparar por scroll.
53. **WebGL Distortion:** Shaders que criam refração, ondulação de líquido ou distorção cromática em imagens.
54. **Liquid Transition:** Efeito de troca de imagem simulando tinta se espalhando ou gosma fluida.
55. **Particle Animation:** Simulação de dezenas ou centenas de partículas físicas que reagem a forças de atração/repulsão do mouse.
56. **Depth Layers:** Múltiplas camadas de arte recortadas que se afastam ou aproximam no eixo Z criando volume 3D.
57. **3D Camera Movement:** A câmera virtual passeia por um espaço tridimensional (Three.js ou Spline) orientada pelo scroll.
58. **Physics Motion:** Elementos obedecem a leis de colisão, fricção, peso e gravidade realistas.
59. **Inertia:** O elemento mantém momento cinético após o usuário soltar o arraste, desacelerando organicamente.
60. **Smooth Scroll:** Normalização e amortecimento da rolagem da página inteira (Lenis ou GSAP ScrollSmoother).
61. **Loop:** Animação infinita e contínua de fundo (órbita lenta, respiração, luz ambiente pulsante).

---

### Categoria 06: Nomes Importantes da Ferramenta GSAP (12 Nomenclaturas)
A terminologia e plugins oficiais da principal biblioteca de animação da web.

62. **Tween:** Animação única e atômica que interpola propriedades de um estado A para um estado B.
63. **Timeline:** Contêiner sequencial que orquestra múltiplos tweens no tempo com controle total de playhead (`seek`, `reverse`).
64. **ScrollTrigger:** Plugin do GSAP que sincroniza animações com a posição do scroll na janela.
65. **ScrollTo:** Plugin especializado para rolar a janela ou contêiner até um elemento ou posição com curva de aceleração customizada.
66. **ScrollSmoother:** Plugin oficial para rolagem amortecida com efeitos nativos de parallax e velocidade diferenciada.
67. **SplitText:** Plugin para particionar textos em caracteres, palavras e linhas mantendo semântica e acessibilidade.
68. **Flip (GSAP Plugin):** Implementação de alto desempenho do padrão FLIP para reorganização instantânea de grids e listas.
69. **Draggable:** Plugin para adicionar suporte a arrasto com suporte a touch, mouse, snap a grid e limites físicos.
70. **MotionPath:** Plugin para fazer qualquer elemento seguir trajetórias SVG complexas e curvas Bezier.
71. **MorphSVG:** Plugin que interpola qualquer formato vetorial para outro, mesmo com contagens diferentes de pontos de controle.
72. **DrawSVG:** Plugin que interpola o comprimento do traço vetorial de forma intuitiva de 0% a 100%.
73. **Observer:** Plugin que unifica a detecção de intenção do usuário (scroll wheel, touch swipe, drag) antes que o navegador role a página.

---

## 3. Combinações Recomendadas por Objetivo de Projeto

| Estilo de Projeto | Combinação Principal Recomendada | Atmosfera Visual & Ritmo |
| :--- | :--- | :--- |
| **01. Visual Limpo (SaaS Corporativo)** | `Fade In` + `Slide In Leve` + `Stagger` | Discreto, institucional, rápido (200-300ms), sem chamar atenção para o efeito. |
| **02. Landing Page de Conversão** | `Scroll Trigger` + `Mask Reveal` + `Parallax Suave` + `Animated Counter` | Conduz a narrativa, destaca métricas e provas sociais conforme o usuário desce. |
| **03. Portfólio de Luxo / Agência** | `Smooth Scroll` + `Page Transition` + `Magnetic Button` + `3D Tilt` | Movimento fluido contínuo (Lenis/ScrollSmoother), cursor follower e cards com física. |
| **04. Página de Produto (Hardware/App)** | `Pin` + `Image Sequence (Canvas)` + `Depth Layers` | O produto fica travado no centro da tela girando 360° enquanto suas peças explodem. |
| **05. Tech / Cyber / Futurista** | `Text Scramble` + `WebGL Distortion` + `Particle Animation` | Atmosfera de terminal, decodificação de dados, malhas de partículas e glow. |
| **06. Aplicação Web Mobile-First** | `Swipe` + `Microinteractions` + `Menu Morph` + `Accordion Motion` | Gestos táteis rápidos, feedback háptico/visual imediato, transições sem atraso. |

---

## 4. Snippets de Produção (Recipes Prontos)

### Snippet A: Magnetic Button (React + GSAP)
```tsx
import React, { useRef } from 'react';
import gsap from 'gsap';

export const MagneticButton = ({ children, className = '' }: { children: React.ReactNode; className?: string }) => {
  const btnRef = useRef<HTMLButtonElement>(null);

  const handleMouseMove = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (!btnRef.current) return;
    const { clientX, clientY } = e;
    const { left, top, width, height } = btnRef.current.getBoundingClientRect();
    const x = (clientX - (left + width / 2)) * 0.35;
    const y = (clientY - (top + height / 2)) * 0.35;

    gsap.to(btnRef.current, { x, y, duration: 0.3, ease: 'power2.out' });
  };

  const handleMouseLeave = () => {
    if (!btnRef.current) return;
    gsap.to(btnRef.current, { x: 0, y: 0, duration: 0.7, ease: 'elastic.out(1, 0.3)' });
  };

  return (
    <button
      ref={btnRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className={`relative inline-flex items-center justify-center transition-colors ${className}`}
    >
      {children}
    </button>
  );
};
```

### Snippet B: 3D Tilt Card (CSS Perspective + Mouse Coordinates)
```tsx
import React, { useRef, useState } from 'react';

export const TiltCard = ({ children, className = '' }: { children: React.ReactNode; className?: string }) => {
  const cardRef = useRef<HTMLDivElement>(null);
  const [transform, setTransform] = useState('perspective(1000px) rotateX(0deg) rotateY(0deg)');

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    const rotateX = -(y / (rect.height / 2)) * 8;
    const rotateY = (x / (rect.width / 2)) * 8;

    setTransform(`perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`);
  };

  const handleMouseLeave = () => {
    setTransform('perspective(1000px) rotateX(0deg) rotateY(0deg)');
  };

  return (
    <div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{ transform, transition: 'transform 0.15s ease-out' }}
      className={`will-change-transform ${className}`}
    >
      {children}
    </div>
  );
};
```

### Snippet C: Mask Reveal de Imagem com GSAP ScrollTrigger
```tsx
import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export const MaskRevealImage = ({ src, alt }: { src: string; alt: string }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(
        containerRef.current,
        { clipPath: 'polygon(0% 100%, 100% 100%, 100% 100%, 0% 100%)' },
        {
          clipPath: 'polygon(0% 0%, 100% 0%, 100% 100%, 0% 100%)',
          duration: 1.2,
          ease: 'power3.inOut',
          scrollTrigger: {
            trigger: containerRef.current,
            start: 'top 80%',
            toggleActions: 'play none none none',
          },
        }
      );

      gsap.fromTo(
        imgRef.current,
        { scale: 1.2 },
        {
          scale: 1.0,
          duration: 1.4,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: containerRef.current,
            start: 'top 80%',
            toggleActions: 'play none none none',
          },
        }
      );
    });

    return () => ctx.revert();
  }, []);

  return (
    <div ref={containerRef} className="relative overflow-hidden w-full h-full rounded-2xl">
      <img ref={imgRef} src={src} alt={alt} className="w-full h-full object-cover" />
    </div>
  );
};
```

---

## 5. Checklist de Verificação de Qualidade de Motion

Antes de considerar qualquer animação pronta:
- [ ] O movimento roda a 60fps estáveis em dispositivos de média performance?
- [ ] O código respeita `prefers-reduced-motion` e desativa transições vertiginosas?
- [ ] Não há vazamento de memória em SPAs (todas as timelines estão associadas a `gsap.context()` ou `ctx.revert()` no unmount)?
- [ ] Não há animações competindo por atenção na mesma dobra da tela (regra do ponto focal único)?
- [ ] Os elementos possuem fallback de visualização em caso de falha de carregamento do JS (evitar elementos com `opacity: 0` travados)?
