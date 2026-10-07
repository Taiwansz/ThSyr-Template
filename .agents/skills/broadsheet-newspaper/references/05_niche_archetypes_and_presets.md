# GUIA DE ARQUETIPOS DE NICHO E ADAPTACAO UNIVERSAL

Este manual instrui como calibrar e adaptar a skill **`broadsheet-newspaper`** para qualquer matéria acadêmica, seminário, disciplina universitária ou encomenda solicitada por professores e orientadores, transcendendo a esfera de tecnologia pura.

---

## 1. Mapeamento por Disciplinas e Áreas do Saber

### A. História, Ciência Política e Relações Internacionais
* **Caso de Uso:** Recriação de um jornal da época para simular um evento histórico (ex: A Proclamação da República de 1889, O Tratado de Versalhes de 1919, A Crise dos Mísseis de 1962, ou A Queda da Bastilha de 1789).
* **Arquétipo Recomendado:** `classic`.
* **Título Sugerido:** *A Gazeta Constitucional*, *The Daily Tribune*, *O Diário das Nações*.
* **Lema Latino:** *“Salus Populi Suprema Lex Esto”* (O bem do povo seja a lei suprema).
* **Estrutura:**
  - Manchete com a deliberação dos parlamentos ou declaração diplomática.
  - Coluna do Telégrafo com despachos das capitais estrangeiras sobre a crise.
  - Tabela com inventário de tropas, tratados ratificados ou finanças do tesouro público.
  - Rodapé com a portaria do ministério da justiça ou decreto supremo.

### B. Economia, Contabilidade e Administração de Negócios
* **Caso de Uso:** Relatório macroeconômico, balanço anual de crises cambiais, análise do sistema financeiro, fusões de conglomerados ou história do padrão-ouro.
* **Arquétipo Recomendado:** `financial` (paleta salmão mineral).
* **Título Sugerido:** *The Financial Gazette*, *O Mercantil & Financeiro*, *O Mensageiro da Bolsa*.
* **Lema Latino:** *“Pacta Sunt Servanda”* (Os acordos devem ser cumpridos).
* **Estrutura:**
  - Manchete sobre a taxa básica de juros, quebra de safras de café ou balança comercial.
  - Coluna do Telégrafo com cotações de Londres, Nova York, Paris e Hamburgo.
  - Tabela comparativa de títulos do tesouro, câmbio do franco/libra/dólar e fretes marítimos.
  - Análise em duas colunas sobre liquidez bancária e risco de inadimplência.

### C. Ciências Biológicas, Medicina e Saúde Pública
* **Caso de Uso:** Divulgação de teses científicas, anúncio de descobertas de vacinas, reformas sanitárias (ex: Oswaldo Cruz em 1904), descoberta da penicilina ou sequenciamento genômico.
* **Arquétipo Recomendado:** `scientific` (paleta pergaminho com realce verde botânico).
* **Título Sugerido:** *The Scientific Register*, *Os Anais da Academia de Medicina*, *O Arauto Científico*.
* **Lema Latino:** *“Scientia Potentia Est”* (Conhecimento é poder).
* **Estrutura:**
  - Manchete sobre os ensaios clínicos laboratoriais e erradicação de patógenos.
  - Sublide com metodologia experimental e amostragem de pacientes.
  - Tabela com dados estatísticos de incidência, grupos de controle e desvio padrão.
  - Despachos telegráficos com notas das sociedades de química e biologia europeias.

### D. Letras, Filosofia, Literatura e Comunicação Social
* **Caso de Uso:** Suplemento literário sobre uma escola artística (ex: Modernismo na Semana de 22, Romantismo, Iluminismo), ensaio sobre a obra de Machado de Assis ou Kant, crônicas urbanas.
* **Arquétipo Recomendado:** `cultural` (paleta algodão cru com siena queimado).
* **Título Sugerido:** *The Literary Review*, *A Tribuna das Belas-Artes*, *O Folhetim Crítico*.
* **Lema Latino:** *“Ars Longa, Vita Brevis”* (A arte é longa, a vida é breve).
* **Estrutura:**
  - Ensaio central em 3 colunas dissecando a nova publicação poética ou o manifesto filosófico.
  - Coluna lateral com crônica lírica do cotidiano da cidade.
  - Crítica dos novos espetáculos do Teatro Municipal e salões de pintura.
  - Poema ou extrato em tipografia itálica com capitular esculpida.

### E. Engenharia, Física, Matemática e Computação
* **Caso de Uso:** Publicação de patentes, relatório de arquitetura de compiladores, análise de supercondutores, modelagem de Data Warehouse, inteligência artificial ou cálculo estrutural.
* **Arquétipo Recomendado:** `tech` (paleta cinza-ardósia com bronze mineral).
* **Título Sugerido:** *The Mechanical Herald*, *A Gazeta dos Engenheiros*, *O Monitor da Técnica*.
* **Lema Latino:** *“Mens Agitat Molem”* (A mente move a matéria).
* **Estrutura:**
  - Manchete sobre especificação de novo motor de turbina, compilador ou infraestrutura.
  - Sub-lede detalhando throughput, latência de barramento ou resistência de materiais.
  - Diagrama em gravura ASCII ou tabela técnica com microarquitetura, registradores e Big-O.
  - Despachos com registros do escritório de patentes.

---

## 2. Parâmetros Configuráveis no Gerador (`scaffold_newspaper.py`)

Ao executar o script de geração, passe as propriedades temáticas do seu trabalho:

```bash
python scripts/scaffold_newspaper.py \
  --archetype <classic | financial | scientific | cultural | tech> \
  --title "Nome do Jornal" \
  --motto "Lema do Sub-Masthead" \
  --location "Cidade e Estado" \
  --volume "Número do Volume" \
  --edition "Número da Edição" \
  --price "Preço da Edição" \
  --lead-title "Manchete Principal" \
  --lead-sub "Sub-manchete ou Deck da Matéria Principal" \
  --output "arquivo_final.html"
```

A flexibilidade é absoluta. Qualquer tema acadêmico ganha instantaneamente a dignidade de um documento histórico centenário.
