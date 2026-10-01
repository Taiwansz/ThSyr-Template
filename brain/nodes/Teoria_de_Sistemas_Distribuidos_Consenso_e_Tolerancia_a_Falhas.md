---
id: node-sistemas-distribuidos-consenso
title: Teoria de Sistemas Distribuidos, Consenso e Tolerancia a Falhas
type: systems-architecture
lobe: parietal
importance: 0.98
tags:
  - sistemas-distribuidos
  - consenso
  - raft
  - paxos
  - lsm-trees
  - crdts
  - cap-theorem
  - parietal
---

# Teoria de Sistemas Distribuidos, Consenso e Tolerancia a Falhas

Fundamentacao sobre como projetar, raciocinar e provar a corretude de sistemas que operam sobre multiplos nos computacionais interconectados por redes assincronas e sujeitas a particao, latencia imprevisivel e falhas de parada (crash-stop / crash-recovery).

---

## 1. Tempo, Relogios e Causalidade

Em um sistema distribuido, nao existe um relogio fisico global compartilhado. O desvio de quartzo (clock drift) e a latencia variavel de rede tornam impossivel determinar a ordem temporal estrita de dois eventos ocorridos em maquinas distintas utilizando timestamps de relogio de parede (NTP).

1. **Relogios Logicos de Lamport**:
   - Definem a relacao de ordem parcial "aconteceu-antes" ($a \to b$).
   - Cada processo incrementa um contador monotonicamente a cada evento interno. Ao enviar uma mensagem, anexa seu relogio $L_i$; o receptor atualiza seu relogio para $L_j = \max(L_j, L_i) + 1$.
   - Se $a \to b$, entao $L(a) < L(b)$. Porem, a recíproca nao e verdadeira (dois eventos com $L(a) < L(b)$ podem ser concorrentes).
2. **Relogios Vetoriais (Vector Clocks)**:
   - Cada no mantem um vetor de contadores de tamanho $N$ (onde $N$ e o numero de nos).
   - Permitem identificar de forma exata e matematica se dois eventos possuem dependencia causal direta ou se sao **concorrentes** ($a \parallel b$), base fundamental para deteccao de conflitos em bancos distribuidos (ex: Amazon Dynamo, Riak).

---

## 2. O Teorema CAP e o Modelo PACELC

Formulado por Eric Brewer e provado formalmente por Gilbert e Lynch:

1. **Teorema CAP**:
   Em um sistema distribuido assincrono, sob ocorrencia de uma **Particao de Rede (P)**, e matematicamente impossivel garantir simultaneamente:
   - **Consistencia Estrita (C - Linearizabilidade)**: Toda leitura retorna a gravacao mais recente ou um erro.
   - **Disponibilidade (A - Availability)**: Todo no nao-defeituoso retorna uma resposta de sucesso sem erro ou recusa.
   - **Decisao Inegociavel**: Redes fisicas inevitavelmente falham ($P$ e uma certeza do mundo fisico). Portanto, o sistema deve optar entre **CP** (rejeitar escritas para preservar a verdade dos dados) ou **AP** (aceitar escritas em nos isolados, gerando divergencias temporarias).

2. **Extensao PACELC (Daniel Abadi)**:
   - Se ha **Particao (P)**: Como o sistema escolhe entre **Disponibilidade (A)** e **Consistencia (C)**?
   - **Senao (E - Else)**, quando o sistema opera normalmente em regime de paz: Como escolhe entre **Latencia (L)** e **Consistencia (C)**?
   - Exemplo: Sistemas como MongoDB ou Cassandra no modo padrao priorizam Latencia baixa (PA/EL), enquanto Spanner ou PostgreSQL com replicacao sincrona priorizam Consistencia (PC/EC).

---

## 3. Algoritmos de Consenso: Replicacao de Maquina de Estado

O problema do consenso reside em fazer com que um conjunto de computadores concorde com uma sequencia ordenada de comandos de transicao de estado na presenca de falhas de rede e quedas de nós (modelo Paxos/Raft assume falhas nao-bizantinas).

### A Arquitetura do Protocolo Raft (Ongaro & Ousterhout):
Concebido para decompor o consenso em subproblemas compreensiveis:
1. **Eleicao de Lider**:
   - Nos operam em tres estados: *Follower*, *Candidate*, *Leader*.
   - Se um Follower nao recebe heartbeat antes do timeout de eleicao (randomizado entre 150ms e 300ms para evitar votos divididos), autodeclara-se Candidate e solicita votos via RPC `RequestVote`.
   - Requer maioria absoluta (Quorum de $\lfloor N/2 \rfloor + 1$) para consagrar um lider.
2. **Replicacao de Log (AppendEntries)**:
   - Todo comando de cliente e recebido exclusivamente pelo Lider, que anexa a entrada ao seu proprio log local e dispara RPCs `AppendEntries` em paralelo para os seguidores.
   - O comando e considerado *committed* (irreversivel) assim que for gravado no disco da maioria dos nos.
3. **Invariante de Correspondencia de Log (Log Matching Invariant)**:
   - Se duas entradas em logs de nos distintos possuem o mesmo indice e termo, elas armazenam o mesmo comando e todos os seus logs predecessores sao compulsoriamente identicos.

---

## 4. Motores de Armazenamento: LSM-Trees vs B-Trees

1. **B-Trees / B+Trees (Motores In-Place como Postgres/InnoDB)**:
   - Otimizadas para leitura aleatoria rapida ($O(\log N)$).
   - Gravam diretamente no local fisico da pagina em disco (random I/O). Sob taxas extremas de escrita, causam severa fragmentacao e amplificacao de gravacao (write amplification).
2. **LSM-Trees (Log-Structured Merge-Trees - RocksDB, Cassandra, SQLite WAL)**:
   - Transformam todas as escritas em **Append Sequencial Puro**:
     1. **MemTable**: Gravacao imediata em memoria RAM estruturada em SkipList ou Red-Black Tree ordenada por chave.
     2. **Write-Ahead Log (WAL)**: Gravacao sequencial e sincrona no disco para garantia de durabilidade (ACID) contra crashes.
     3. **SSTables (Sorted String Tables)**: Quando a MemTable atinge capacidade limite, e descarregada (*flush*) como um arquivo imutavel ordenado no disco.
     4. **Compaction**: Processo de fundo que funde multiplas SSTables obsoletas em novos niveis hierarquicos (Leveled Compaction), expurgando dados deletados (tombstones).
     5. **Bloom Filters**: Estruturas probabilisticas baseadas em funcoes de hash que testam se uma chave nao reside em determinada SSTable com probabilidade de falso positivo parametrizada, evitando leituras estereis no disco.

---

## 5. CRDTs (Conflict-free Replicated Data Types)
Estruturas matematicas com propriedades algebricas de Semirreticulados Semilattice (Comutativa, Associativa e Idempotente):

$$A \vee B = B \vee A, \quad (A \vee B) \vee C = A \vee (B \vee C), \quad A \vee A = A$$

Permitem que replicas recebam atualizacoes em qualquer ordem, com perda temporaria de conexao, e convirjam deterministicamente para o mesmo estado final sem necessidade de coordenacao central ou locks distribuidos.

---

## Sinapses
- Conectado a [[Lobo_Parietal]].
- Conectado a [[Microarquitetura_de_Computadores_e_Fisica_do_Silicio]].
- Conectado a [[Padroes_Engenharia]].
- Conectado a [[Enxame_Ultron_Distribuido]].
- Conectado a [[Supabase_Stack]].
