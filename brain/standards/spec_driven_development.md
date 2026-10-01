# Padrao de Desenvolvimento Orientado por Especificacao (Spec-Driven Development) & Engenharia Agentica

Este documento formaliza o padrao operacional do ThSyr para conducao de projetos full-stack de grande escala, engenharia de software agêntica e selecao rigorosa de estruturas de dados.

---

## 1. Fundamentos Metodologicos

A abordagem funde tres pilares da engenharia contemporanea:

1. **Spec-Driven Development (SDD)**:
   A especificacao formal antecede o codigo. Contratos, esquemas relacionais, entidades de dominio e politicas de seguranca sao definidos em documentos Markdown canônicos que servem como fonte unica da verdade.

2. **Workflow Research-Plan-Implement (RPI)**:
   - **Research**: Investigacao contextual e extracao topologica via [[Graphify_Code_Architecture]].
   - **Plan**: Mapeamento granular de arquivos, contratos impactados, analise Big-O e checklist de seguranca.
   - **Implement**: Execucao atomica em pequenos blocos com verificacao estatica e testes continuos.
   - **Task Report**: Formalizacao do fechamento da tarefa em `docs/tasks/`.

3. **GraphRAG Determinístico como Memoria Arquitetural**:
   A utilizacao do motor Graphify (`thsyr graphify`) reduz a sobrecarga de tokens em 5x a 70x em bases de codigo medias e grandes, evitando leituras lineares cegas e permitindo navegacao por vizinhanca e analise de impacto reverso.

---

## 2. Scaffolding Documental Obrigatorio (`docs/specs/`)

Ao instanciar ou assumir um projeto de grande porte, a seguinte topologia e compulsoria:

| Arquivo | Finalidade Arquitetural |
|---|---|
| `docs/specs/main.md` | Visao holistica do produto, dor real do usuario, escopo, nao-escopo, restricoes legais e metricas de sucesso (SLA, p95, taxa de erro). |
| `docs/specs/architecture.md` | Topologia de containers (`apps/api`, `apps/web`, `packages/*`), padroes arquiteturais (Clean Architecture, Ports & Adapters), servicos externos e lista de ADRs. |
| `docs/specs/domain.md` | Linguagem ubiqua (Domain-Driven Design), entidades nucleares, agregados, invariantes de negocio e politicas de ciclo de vida e privacidade de dados. |
| `docs/specs/security.md` | Modelo de ameacas (STRIDE / OWASP Top 10), requisitos de autenticacao, matriz de autorizacao (RBAC/ABAC), mitigacao de IDOR e governanca de secrets. |
| `docs/specs/quality.md` | Piramide de testes, metas de cobertura, politicas de linter, tipagem estrita e verificacao de regressao. |
| `docs/specs/api-contracts.md` | Especificacao detalhada de endpoints, DTOs tipados de entrada/saida, formatos padronizados de erro (`RFC 7807`) e headers obrigatorios. |
| `docs/adr/ADR-NNN-[titulo].md` | Registros formais de decisoes arquiteturais irreversiveis ou de alto custo. |
| `docs/tasks/YYYY-MM-DD-[feature].md` | Relatorios executivos de conclusao de tarefas com analise de impacto e assertividade. |

---

## 3. Matriz de Decisao de Estruturas de Dados e Complexidade Big-O

A escolha de colecoes e governada estritamente pela operacao dominante no ciclo de vida do dado:

| Operacao Dominante | Estrutura Recomendada | Complexidade Temporal | Anti-Padrao Proibido |
|---|---|---|---|
| Busca frequente por chave ou identificador | Tabela Hash / Dicionario (`dict`, `Map`, `HashMap`) | $O(1)$ amortizado | Array linear com `find()`, `indexOf()` ou loop scan $O(n)$ |
| Verificacao de unicidade e pertencimento | Conjunto Hash (`set`, `HashSet`) | $O(1)$ amortizado | Array com `includes()` dentro de loop |
| Insercoes e remocoes prioritarias | Fila de Prioridade / Heap (`heapq`, `PriorityQueue`) | $O(\log n)$ | Array reordenado via `sort()` a cada insercao $O(n \log n)$ |
| Operacoes estritas LIFO (Desfazer / Pilha de execucao) | Pilha (`list.append/pop`, `Deque`) | $O(1)$ | Array com insercoes/remocoes no inicio (`shift`/`unshift`) $O(n)$ |
| Operacoes estritas FIFO (Fila de tarefas / Buffers) | Fila de extremidade dupla (`collections.deque`, `ArrayDeque`) | $O(1)$ | Array linear com remocao no indice zero $O(n)$ |
| Consultas frequentes por intervalo em dados estaveis | Array Ordenado + Busca Binaria (`bisect`) | $O(\log n)$ busca | Reordenacao completa em tempo de consulta |
| Navegacao em grafos de dependencia e hierarquias | Grafo por Lista de Adjacencia (`dict[ID, list[ID]]`) | $O(V + E)$ | Matriz densa de adjacencia para grafos esparsos |

### Regra Anti-$O(n^2)$: Eliminacao de Joins Lineares em Memoria
Ao combinar duas colecoes em memoria (ex: associar uma lista de $N$ pedidos a uma lista de $M$ clientes), e terminantemente proibido o aninhamento:

```python
# PROIBIDO: Complexidade O(N * M)
resultado = [
    {**pedido, "cliente": next(c for c in clientes if c["id"] == pedido["cliente_id"])}
    for pedido in pedidos
]
```

O padrao compulsorio exige indexacao previa por Hash Map com complexidade $O(N + M)$:

```python
# OBRIGATORIO: Complexidade O(N + M)
clientes_por_id = {c["id"]: c for c in clientes}
resultado = [
    {**pedido, "cliente": clientes_por_id.get(pedido["cliente_id"])}
    for pedido in pedidos
]
```

---

## 4. Guardrails e Prevencao de Vulnerabilidades por Camada

1. **Camada de Transporte e Borda**:
   - Rate limiting mandatorio em endpoints de autenticacao, recuperacao de credenciais e buscas textuais.
   - Headers de seguranca padrao: HSTS, Content-Security-Policy (CSP), X-Content-Type-Options, X-Frame-Options.

2. **Camada de Aplicacao e Logica de Negocio**:
   - **Prevencao a IDOR (Insecure Direct Object Reference)**: Nenhuma entidade e buscada exclusivamente pelo ID da URL sem filtro obrigatorio pelo contexto do usuario ou `tenant_id` da sessao.
   - **Validacao de Fronteira**: Uso obrigatorio de bibliotecas de parsing e validacao estrita (Pydantic em Python, Zod em TypeScript, Bean Validation em Java).

3. **Camada de Persistencia**:
   - Proibicao absoluta de concatenacao de strings em comandos SQL.
   - Uso de prepared statements, parametros nomeados ou query builders protegidos.
   - Migrations de esquema versionadas e rastreaveis (Flyway, Alembic, Liquibase, Drizzle).

4. **Camada de Seguranca de Secrets**:
   - Proibido expor credenciais, tokens JWT ou senhas em logs ou commits.
   - `.env` e mantido estritamente local e listado no `.gitignore`.

---

## 5. Sinapses
- Conectado a [[Padroes_Engenharia]].
- Conectado a [[Graphify_Code_Architecture]].
- Conectado a [[Cortex_Central]].
- Conectado a [[Lobo_Parietal]].
