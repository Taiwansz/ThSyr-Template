---
id: motor-vetorial-local
title: Motor Vetorial Local e Indice Denso Embutido
type: technical_standard
lobe: parietal
importance: 0.95
tags:
  - vetores
  - embeddings
  - sqlite
  - recuperacao
  - semantica
---

# Motor Vetorial Local e Indice Denso Embutido

Camada de indexacao e busca semantica densa de altissima velocidade integrada nativamente ao ThSyr, sem necessidade de servidores externos de banco vetorial ou dependencias de nuvem.

---

## 1. Principios Arquiteturais
- **Embeddings Densos Offline:** Hashing de n-gramas e projecao semantica deterministica com normalizacao L2, permitindo consultas semanticas em microssegundos.
- **Persistencia ACID embutida:** Armazenamento relacional e vetorial via SQLite em `state/vector_index.db`.
- **Similaridade de Cosseno Pura:** Produto escalar normalizado em Python nativo, eliminando complexidade de compiladores C ou pacotes pesados.
- **Flexibilidade Hibrida:** Compativel com injecao de vetores gerados por modelos neurais locais (Ollama) ou externos.

---

## 2. Implementacao
- Modulo: `engine/vector_store.py`
- Classe Central: `LocalVectorStore`
- Testes: `tests/test_vector_store.py`

---

## Sinapses
- Conectado a [[Cortex_Central]].
- Conectado a [[Padroes_Engenharia]].
- Conectado a [[Python_Engine]].
