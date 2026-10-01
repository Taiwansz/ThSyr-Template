---
id: java-excecoes-resiliencia
type: knowledge-node
tags:
  - java
  - excecoes
  - resiliencia
  - arquitetura
lobe: parietal
---

## Conceito Central

Exceções em Java são o mecanismo canônico de sinalização e contenção de falhas em tempo de execução. Dividem-se em Checked (o compilador exige tratamento explícito via try-catch ou declaração throws) e Unchecked (subclasses de RuntimeException).

## Hierarquia Canônica

```
Throwable → Exception → [Checked] → extends Exception
                      → RuntimeException → [Unchecked]
```

## Padrões Estruturais de Resiliência

1. **try-catch básico** — contenção determinística de falhas de cálculo ou parsing
2. **multi-catch** — tratamento unificado de exceções complementares sem duplicação de blocos
3. **try-catch-finally / try-with-resources** — liberação garantida de descritores de sockets e arquivos
4. **throw com validação de pré-condição** — lançamento imediato de `IllegalArgumentException` ou `IllegalStateException`
5. **Exceções customizadas de domínio** — `extends Exception` encapsulando contexto de negócio
6. **Propagação declarativa com throws** — sinalização contratual na assinatura de métodos
7. **Loop resiliente com isolamento de borda** — isolamento de falhas atômicas por item sem interrupção do pipeline global

## Armadilhas Clássicas

- Ordem do multi-catch: tipos derivados e específicos devem preceder superclasses genéricas
- Omissão de `throws` na assinatura ao lançar Checked Exceptions
- Colocar try-catch fora de loops de processamento em lote em vez de isolar por iteração
- Capturar `Throwable` indiscriminadamente, mascarando falhas fatais da JVM (`OutOfMemoryError`)

## Referências

- [[Java_POO_e_Arquitetura_Industrial]]
- [[Padroes_Engenharia]]
