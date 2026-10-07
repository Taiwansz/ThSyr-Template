# ThSyr Template — Copiloto Cognitivo Pessoal

> Blueprint e template público para instanciação de copilotos cognitivos pessoais de alto nível com memória cumulativa permanente, anti-sicofância e grafo neural 3D.

---

## O Que É Este Projeto?

Este repositório é uma arquitetura completa de **Copiloto Cognitivo Pessoal**, desenvolvida para atuar como conselheiro técnico, parceiro de arquitetura de software e copiloto contínuo.

Ao contrário de assistentes descartáveis e chatbots sem memória, esta arquitetura possui:
1. **Memória Persistente Permanente:** Quatro camadas de memória (episódica, semântica, analítica e procedural) organizadas sob a estrutura anatômica de um cérebro (`brain/`).
2. **Cérebro Neural 3D Interativo:** Visualização holográfica tridimensional em WebGL/Three.js de todos os nós semânticos, projetos e sinapses (`brain/neural_canvas_3d.html`).
3. **Córtex Pré-Frontal Anti-Sicofância:** Auditoria inibitória em tempo real que veta respostas subservientes, bajulações e premissas fracas.
4. **Skills Especializadas Embutidas:** Bibliotecas de excelência estética e arquitetural (`apple-design`, `taste-skill`, `logo-design`, `mobile-first-design-system`, `broadsheet-newspaper`, `brag`).
5. **CLI Operacional Unificada:** Ferramenta de linha de comando (`python thsyr.py`) para ingestão de projetos, compilação de grafo, publicação editorial e auditorias.

### Cerebro Neural 3D

<!-- THSYR_GRAPH_STATS:START -->
**Estado atual do cérebro:** `92` nós e `420` sinapses.

<!-- THSYR_GRAPH_STATS:END -->

O cérebro do copiloto possui renderização holográfica 3D interativa gerada a partir dos nós do `brain/` e projetos locais:
```bash
python thsyr.py graph3d
```

---

## Como Criar o Seu Próprio Copiloto (Quick Start)

### Passo 1: Use Este Template
1. Clique no botão verde **"Use this template"** no topo da página do GitHub (ou clone o repositório):
   ```bash
   git clone https://github.com/Taiwansz/ThSyr-Template.git meu-copiloto
   cd meu-copiloto
   ```

### Passo 2: Instale as Dependências
Recomenda-se Python 3.11 ou superior:
```bash
pip install -e ".[dev,desktop]"
```
Ou instale as dependências diretamente via `pip`:
```bash
pip install pytest fastapi uvicorn pydantic requests
```

### Passo 3: Inicie a Conversa com Qualquer IA
Abra esta pasta no seu ambiente de preferência (Cursor, Antigravity, VS Code com Claude Code, Gemini CLI, etc.) e envie uma mensagem simples:
> *"Olá! Vamos iniciar a configuração do meu copiloto."*

A IA lerá automaticamente o arquivo [BOOTSTRAP.md](BOOTSTRAP.md) e iniciará o **Questionário de Calibração**:
1. **Nome e Papel:** Como o seu copiloto se chamará (ex: *Jarvis*, *Athena*, *Syr*, *Turing*, etc.).
2. **Arquétipo de Tom:** Britânico sóbrio, Ultron crítico, Mentor acadêmico ou Engenheiro sênior.
3. **Objetivos:** Seus focos de estudo, pesquisa e desenvolvimento.
4. **Regras e Limites:** Tolerância zero a bajulação, política de emojis e densidade de resposta.
5. **Autorização de Varredura:** A IA perguntará se pode realizar uma análise autorizada nas suas pastas locais de projetos para indexar seu ecossistema no cérebro digital.

### Passo 4: O Cérebro é Moldado
Após o questionário, a IA:
- Gravará seus dados em `brain/core/personality.md`, `brain/core/directives.json` e `brain/profile/user.md`.
- Executará a ingestão neural das suas pastas (caso autorizada).
- Compilará o grafo neural 3D.
- Declarará a prontidão operacional do seu copiloto.

---

## Estrutura do Sistema

```
meu-copiloto/
├── BOOTSTRAP.md                   # Protocolo mandatório de onboarding da IA
├── INSTRUCOES_INICIAIS.md         # Guia rápido em português
├── thsyr.py                       # CLI unificada de controle cognitivo
├── brain/                         # Hipocampo e Córtex Cognitivo
│   ├── Cortex_Central.md          # Ponto focal de convergência neural
│   ├── core/                      # Personalidade, tom e diretrizes inegociáveis
│   │   ├── personality.md         # Regras de voz, estilo e postura dialética
│   │   └── directives.json        # Parâmetros estruturados do agente e operador
│   ├── profile/                   # Perfil do Operador e Dossiê Comportamental
│   │   ├── user.md                # Metas, stack, preferências e projetos
│   │   └── psychological_dossier.md # Dossiê de deduções analíticas contínuas
│   ├── standards/                 # Padrões de engenharia, arquitetura e design
│   ├── memories/                  # Sistema de Memória Permanente
│   │   ├── episodic/              # Diários de sessões organizados cronologicamente
│   │   ├── semantic/              # Conhecimento consolidado de projetos e conceitos
│   │   ├── analytical/            # Deduções analíticas de segunda ordem
│   │   └── procedural/            # Procedimentos operacionais padrão (SOPs)
│   ├── nodes/                     # Nós conceituais e base de conhecimento
│   └── sleep_cycle/               # Rotina de consolidação de memórias (O Sono)
├── engine/                        # Motor Cognitivo Python
│   ├── cognitive_router.py        # Orquestrador de contexto e roteamento
│   ├── prefrontal_cortex.py       # Auditoria inibitória e anti-sicofância
│   ├── memory_manager.py          # Gestão unificada das 4 camadas de memória
│   ├── retriever.py               # Motor de busca híbrida (léxica + semântica + grafo)
│   ├── visual/                    # Visual Studio e protocolo contra mediocridade
│   ├── code_graph/                # Análise AST e visualização de código
│   ├── news/                      # Motor editorial da Gazeta Tecnológica
│   └── runtime/                   # Supervisor de processos e continuous event loop
├── skills/                        # Arsenal unificado de habilidades de engenharia, arquitetura e design
│   ├── apple-design/              # Padrões de interfaces de altíssima fidelidade e física Apple
│   ├── atlas-deep-reporting/      # Doutrina de relatórios técnicos e auditoria analítica quantitativa
│   ├── editorial-canvas-3d/       # Motor espacial 3D em Canvas 2D nativo com mouse parallax
│   ├── broadsheet-newspaper/      # Periódicos impressos históricos broadsheet em HTML puro (Universal)
│   ├── taste-skill/               # Calibração estética contra designs genéricos (Anti-Slop)
│   ├── stitch-design-taste/       # Design systems semânticos para Google Stitch
│   ├── logo-design/               # Criação de identidades visuais e marcas em SVG
│   ├── mobile-first-design-system/ # Design responsivo e ergonomia móvel rigorosa
│   ├── brandkit/                  # Geração de brand-kits visuais e guidelines de marca
│   ├── industrial-brutalist-ui/   # Interfaces industriais mecânicas e terminais de alta precisão
│   ├── gpt-taste/                 # Engenharia avançada de animação GSAP e layout dinâmico
│   ├── minimalist-ui/             # Interfaces minimalistas editoriais e bento grids
│   ├── image-to-code/             # Conversão de referências visuais em código limpo
│   ├── systematic-debugging/      # Investigação metodológica de causa raiz em 4 fases
│   ├── test-driven-development/   # Ciclo disciplinar Red-Green-Refactor estrito
│   ├── using-git-worktrees/       # Isolamento de branches paralelas no sistema de arquivos
│   ├── verification-before-completion/ # Verificação empírica compulsória antes de conclusões
│   ├── packet-tracer/             # Automação e simulação de topologias de redes via MCP
│   └── ...                        # Utilitários de geração de imagem, code review e anti-truncamento
├── tests/                         # Suíte de testes automatizados herméticos
└── state/                         # Estado operacional de sessões e checkpoints
```

---

## Comandos Operacionais da CLI

O comando `thsyr.py` é o ponto de contato do operador e do agente com o cérebro:

### Diagnóstico do Cérebro
```bash
python thsyr.py status
```
Exibe o estado de ativação dos nós, sinapses, lobos cerebrais e o Córtex Pré-Frontal.

### Ingestão de Projetos e Pastas
```bash
python thsyr.py ingest --path "/caminho/do/seu/projeto"
```
Varre o projeto de forma segura, catalogando linguagens, arquivos e dependências no cérebro sem gravar segredos ou código sensível.

### Renderizar o Cérebro Neural 3D
```bash
python thsyr.py graph3d
```
Gera o canvas holográfico interativo em `brain/neural_canvas_3d.html`. Abra diretamente no navegador para inspecionar nós e sinapses com rotação e busca.

### Validar Integridade e Testes
```bash
pytest
```
Executa a suíte de testes de todos os subsistemas cognitivos.

---

## Leis Inegociáveis da Arquitetura

1. **Anti-Sicofância (Zero Bajulação):** O copiloto não existe para bajular. Se uma proposta técnica for frágil, ele tem o dever ético de apontar a falha com lógica implacável e propor a alternativa robusta.
2. **Zero Emojis:** Caracteres gráficos adicionam ruído visual e reduzem a densidade de sinal técnico.
3. **Continuidade Cumulativa:** Amnésia técnica é tratada como falha grave de sistema. Decisões tomadas são persistidas em Markdown e registradas nas sinapses.

---

## Licença

Distribuído sob licença aberta para uso pessoal, acadêmico e profissional. Sinta-se livre para clonar, adaptar e forjar o seu próprio parceiro intelectual de inteligência sintética.
