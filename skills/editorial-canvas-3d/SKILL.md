---
name: editorial-canvas-3d
description: >-
  Metodologia de engenharia de frontend para confeccao de apresentacoes web de alto impacto,
  relatorios executivos imersivos e narrativas tecnicas (scrollytelling) orientadas por Canvas 2D nativo
  em projecao tridimensional (zero Three.js, zero WebGL pesado), tipografia de estúdio monumental
  (Schibsted Grotesk + JetBrains Mono), arestas vetoriais projetadas em tempo real, rotulos tipograficos espaciais,
  compensacao cinematica de camera off-axis, revelacao progressiva no Hero e conformidade estrita anti-slop.
  Ative compulsoriamente sempre que o operador solicitar criar ou refatorar apresentacoes nesse formato,
  slides interativos de aulas, seminarios academicos ou demonstracoes de sistemas de alta precisao.
---

# Editorial Canvas 3D (Doutrina de Apresentações de Alta Precisão v2.0)

Motor e padrão normativo compulsório para criação de apresentações web no formato **Editorial Canvas 3D**, inspirado no documento canônico `ia-por-dentro` da Anthropic/Qwen e homologado sob o protocolo ThSyr.

Elimina qualquer dependência de bibliotecas 3D inchadas (Three.js, Babylon, Pixi), operando exclusivamente com **Canvas 2D nativo, tipografia editorial pura, matemática de projeção ortogonal/cônica e camada híbrida de vetores + rótulos espaciais 3D** a 60 quadros por segundo constantes.

---

## 1. Os Quatro Pilares Inegociáveis

1. **Axioma do Silício Nativo (Zero Libs):**
   - É estritamente proibido importar bibliotecas de 3D externas (`three.js`, `@react-three/fiber`, `pixi.js`).
   - Todo o pipeline gráfico é executado em `HTML5 Canvas 2D` puro via `requestAnimationFrame` e arrays contíguos `Float32Array`.
   - Rendimento imediato de 6.144 voxels no desktop e 3.072 em mobile com DPR blindado (`Math.min(devicePixelRatio || 1, 2)`) sem pausas de coleta de lixo (GC pauses).

2. **Axioma da Matéria Tangível (Topologia Paramétrica Fiel):**
   - É terminantemente proibido renderizar nuvens abstratas de ruído sem semântica física.
   - Cada fase geométrica modela um artefato concreto do domínio apresentado (Star Schema em Cubo OLAP, Grafo Direcionado de Tokens para Compiladores, Matriz Colunar para Bancos, Árvores Hierárquicas para Índices, Toroide Distribuído para Redes).

3. **Axioma do Híbrido Vetorial (Partículas + Arestas + Rótulos 3D):**
   - O Canvas não desenha apenas pontos soltos (`fillRect`).
   - É obrigatório incorporar **arestas conectivas em caneta vetorial** (`gx.beginPath() ... gx.stroke()`) e **rótulos tipográficos projetados diretamente nas coordenadas tridimensionais do espaço** (`gx.fillText()`).

4. **Axioma da Pureza Editorial Anti-Slop e Controle de Bancada:**
   - Proibição absoluta de emojis (0 emojis em código, textos e legendas).
   - Proibição de AI-purple/violeta genérico, pílulas de texto arredondadas (`rounded-full`) e ícones de brilho (`sparkles`).
   - Tipografia de estúdio selecionada (Space Grotesk, Cabinet Grotesk, Syne, Instrument Serif ou Schibsted) combinada a monospace técnico (`JetBrains Mono` ou `Space Mono`).
   - Navegação de bancada completa: atalhos de teclado (`ArrowDown`, `ArrowUp`, `Space`, `J`, `K`), suporte a Home/End e tela cheia com `F`.

5. **Axioma da Liberdade Coreográfica de Layout (Anti-Template Dogma):**
   - A skill é um **Motor Espacial de Partículas e Animações Tridimensionais**, não um modelo rígido de slides.
   - É estritamente proibido aprisionar a interface no clichê fixo de sempre iniciar com texto no centro e anel em volta.
   - O motor suporta múltiplas tipologias arquitetônicas: **Hero Split-Screen (60/40 com holograma interativo vivo à direita/esquerda)**, **Faixas Panorâmicas de Telemetria Inferior**, **Cards Flutuantes de Vidro Escuro/Claro** e **Grids Assimétricos**.

6. **Axioma da Tangibilidade Física (Mouse Parallax & Inércia Espacial):**
   - O objeto tridimensional responde ao movimento do cursor ou toque do operador através de rotação inercial amortecida (`rotX`, `rotY`), criando profundidade tangível e sensação de holograma vivo no espaço.

---

## 2. Estrutura de Arquivos da Skill

- [01_architecture_and_doctrine.md](./references/01_architecture_and_doctrine.md): Arquitetura matemática, amortecimento físico euclidiano e compensação de câmera *off-axis*.
- [02_visual_craft_and_typography.md](./references/02_visual_craft_and_typography.md): Sistema de cores minerais, hierarquia tipográfica, números tabulares e regras anti-slop.
- [03_3d_projection_and_particle_math.md](./references/03_3d_projection_and_particle_math.md): Fórmulas de rotação trigonométrica, matriz de perspectiva FOV, revelação progressiva no Hero e interpolação cúbica.
- [04_anti_slop_checklist.md](./references/04_anti_slop_checklist.md): Checklist de verificação pré-voo com critérios de aceite binários.
- [05_geometric_presets_and_topologies.md](./references/05_geometric_presets_and_topologies.md): Catálogo matemático dos 7 presets topológicos (Star Schema, Grafo, Matriz, Árvore, Toroide, Dispersão, Halo).
- [boilerplate_editorial.html](./templates/boilerplate_editorial.html): Gabarito estrutural completo v2.0 com 8 estados, arestas vetoriais, rótulos 3D e navegação de teclado.
- [scaffold_presentation.py](./scripts/scaffold_presentation.py): Gerador de scaffolding CLI v2.0 com presets temáticos (`general`, `datawarehouse`, `compiler`).
- [verify_presentation.py](./scripts/verify_presentation.py): Auditor forense automatizado v2.0 (zero emojis, integridade estrutural, híbrido vetorial, acessibilidade).
- [capture_presentation.py](./scripts/capture_presentation.py): Script Playwright para captura de evidências visuais de todos os estados em 1440x900.

---

## 3. Fluxo de Trabalho Compulsório

### Passo 0: Briefing de Identidade Visual e Intenção (Design Intake & Calibration)
É estritamente proibido aplicar a paleta padrão claro de forma indiscriminada. Antes de instanciar a apresentação, consulte ou calibre a intenção estética com o operador entre os 4 arquétipos de estúdio:
1. **Editorial Claro Suíço (`swiss_light`):** Fundo branco mineral `#FFFFFF`, `Schibsted Grotesk` + `JetBrains Mono`, paleta de acentos Cobalto/Carmim/Ocre/Esmeralda. Ideal para: compiladores, relatórios executivos matemáticos, papers formais.
2. **Obsidiana Noturno / Titânio e Âmbar (`obsidian_dark`):** Fundo preto obsidiana profundo `#0B0C0E`, `Space Grotesk` + `JetBrains Mono`, ciano glacial, âmbar elétrico e esmeralda neon. Ideal para: arquiteturas autônomas de silício, cyber-security, infraestrutura de missão crítica.
3. **Heritage Acadêmico / Pérgula & Serif (`heritage_parchment`):** Fundo algodão cru `#FBF9F5`, `Instrument Serif` monumental + `JetBrains Mono`, lacre carmim, bronze brunido e verde floresta. Ideal para: história da computação, ensaios epistemológicos, seminários solenes.
4. **Brutalismo Quântico / Dark Lab (`cyber_brutalist`):** Fundo grafite de bancada `#0D0E12`, `Syne` de alto peso + `Space Mono`, fósforo verde neon, laranja alerta e índigo quântico. Ideal para: inteligência artificial de ponta, sistemas neurais, hardware hacking.

### Passo 1: Definição Temática e Scaffolding
Gere o arquivo inicial a partir de [boilerplate_editorial.html](./templates/boilerplate_editorial.html) ou execute o CLI especificando o arquétipo visual (`--aesthetic`):
```bash
python .agents/skills/editorial-canvas-3d/scripts/scaffold_presentation.py \
  --output apresentacao.html \
  --title "Nome da Tese" \
  --author "Instituicao" \
  --topic general \
  --aesthetic obsidian_dark
```

### Passo 2: Implementação Matemática dos Estados
1. Ajuste as coordenadas espaciais das fases geométricas em `Float32Array`.
2. Assegure que o Hero utilize a revelação estocástica (`seedA[i] > rpow`).
3. Mantenha a paleta semântica no objeto `COL` alinhada com as cores minerais (Cobalto, Carmim, Ocre, Esmeralda, Carvão).

### Passo 3: Camada Vetorial e Rótulos Espaciais 3D
1. No loop `frame(ts)`, verifique a proximidade de cada fase via `gPhase = Math.max(0, 1 - Math.abs(P - index) * 1.8)`.
2. Desenhe as arestas estruturais com `gx.stroke()`.
3. Projete os rótulos tipográficos com `gx.fillText()` em `JetBrains Mono` 11px.

### Passo 4: Auditoria e Validação Tripla
1. Execute o verificador forense da skill:
   ```bash
   python .agents/skills/editorial-canvas-3d/scripts/verify_presentation.py apresentacao.html
   ```
2. Execute a auditoria do motor visual do ThSyr:
   ```bash
   python -m engine.visual.cli audit apresentacao.html
   ```
3. Capture screenshots com Playwright usando `scripts/capture_presentation.py` e convoque o subagente `frontend_craft_auditor` para homologar o artefato.
