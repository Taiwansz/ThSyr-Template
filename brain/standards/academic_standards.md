# Padroes Academicos e Arquitetura Vault (Obsidian OS)

Manual canonico de arquitetura de informacao para integracao com cofre Obsidian de conhecimento e estudos acadêmicos (~/academic-vault).
Define as convencoes de metadados, taxonomia e integracao de ferramentas interativas no cofre Obsidian do Operador.

---

## 1. Arquitetura de Pastas e Nomenclatura

O cofre obedece a uma numeracao hierarquica para garantir ordenacao visual consistente e navegabilidade:

- `00 - Dashboard.md`: Homepage com Bento Grid e consultas Dataview dinamicas.
- `00 - Guia do Cofre (Vault Guide).md`: Matriz de diretrizes, metadados e atalhos.
- `01 - Disciplinas/`: Diretorios individuais por disciplina contendo subpastas `Aulas/`, `Materiais/`, `Notas/`, `Provas/`.
- `02 - Avaliacoes/`: Paineis globais e cronogramas de provas e entregas.
- `03 - Calendario/`: Quadro de horarios, faltometro e marcos do semestre.
- `04 - Materiais Gerais/`: Acervo de PDFs institucionais, apostilas e anexos.
- `99 - Templates/`: Modelos padronizados para aulas, atas de orientacao, GDD e laboratorios.
- `Excalidraw/`: Diagramas conceituais e topologias de rede visuais.

---

## 2. Padrao Frontmatter YAML Rigoroso

Todas as notas de aula, atividades e orientacoes devem conter cabeçalho estruturado para ingestao por Dataview:

```yaml
---
tipo: aula # aula | atividade | trabalho | avaliacao | tcc | gdd
disciplina: Compiladores # Nome exato da pasta
data: 2026-08-03
professor: [NOME_DO_PROFESSOR]
status: assistida # assistida | concluido | pendente | em_andamento
---
```

---

## 3. Componentes de UI e Interatividade Nativa

O operador rejeita notas passivas em texto plano. Padroes mandatorios:
1. Bento Grid: Cards de navegacao rapida em CSS (`<div class="bento-grid">...</div>`).
2. Consultas Dataview Dinamicas: Tabelas e listas automaticas para consolidar aulas, presencas e prazos sem manutencao manual redundante.
3. Simuladores Interativos e Terminais Nativos: Implementacao de emuladores (ex: Cisco IOS Catalyst 3560, calculadoras de sub-redes VLSM, simuladores de encapsulamento OSI) codificados nativamente em DataviewJS ou renderizados via `srcdoc` em HTML para compatibilidade total offline dentro do Obsidian.
4. Diagramas Visuais: Integracao de topologias e arquiteturas via Excalidraw e Canvas nativo.

---

## 4. Politica de Frequencia e Faltometro
 
- Carga horaria regulamentar: Minimo obrigatorio de **75% de presenca**.
- Monitoramento semanal via `03 - Calendario/Controle de Frequencia.md`.
- Disciplinas de 80h: Limite maximo de 20h de faltas.
- Disciplinas de 40h: Limite maximo de 10h de faltas.
- Registro continuo de presenca para prevencao de risco por absenteismo.

---

## 5. Protocolo de Fechamento de Aula (SOP-005)

Gatilhos textuais de ativacao: "finalizando aqui a aula", "fim de aula", "encerrei a aula", "acabou a aula".

### Matriz de Varredura e Extracao:
1. **Ambiente Java / IDEs**:
   - `~/workspace/`
2. **Ambiente SQL / SGBD (MySQL Workbench)**:
   - Workspaces e rascunhos ativos: `~/workspace/`
   - Historico de execucoes do dia: `~/workspace/`
   - Logs de acoes SQL: `~/workspace/`
3. **Destino e Higienizacao no Cofre Academico (`academic-vault`)**:
   - Criar ou consolidar na pasta `01 - Disciplinas/<NomeDisciplina>/Materiais/Aula_<Data>_<Tema>/` todos os scripts `.sql` ou arquivos `.java`.
   - Atualizar a nota de aula em `01 - Disciplinas/<NomeDisciplina>/Aulas/` com resumo conceitual, analise critica de arquitetura, diagramas de relacoes e diagnostico de erros superados.
4. **Ciclo de Persistencia Git**:
   - Executar `git add`, `git commit` com mensagem formal e `git push` no repositorio do cofre.
   - Sincronizar o estado da sessao e hipocampo no copiloto com `git push origin main`.

---

## Sinapses
- Conectado a [[Cortex_Central]].
- Conectado a [[Padroes_Engenharia]].
