---
id: node-java-poo
type: technology
tags:
  - tech
  - backend
  - java
  - poo
  - arquitetura
---

# Java POO e Padrões de Arquitetura de Software

Conhecimento consolidado sobre Programação Orientada a Objetos em Java e práticas de modelagem corporativa aplicadas nos projetos industriais e arquiteturais do [[Operador]].

## 1. Padrões Estruturais e Polimorfismo
- **Abstração Contratual:** Uso de interfaces (`Processador`, `Monitoravel`) para desacoplar comportamento de estado e viabilizar interoperabilidade entre módulos heterogêneos.
- **Herança Especializada:** Superclasses abstratas (`ServicoBase`, `EstacaoOperacional`) fornecendo esqueletos reutilizáveis com métodos concretos de controle e métodos abstratos (`executarCiclo()`) para execução polimórfica via Template Method.
- **Encapsulamento Estrito:** Proteção de estado contra mutações ilegais, assegurando invariantes de negócio e validação determinística de limites.

## 2. Persistência e E/S em Disco (Java I/O)
- **Streams com Buffer Encadeado:** Utilização de `BufferedWriter` envolvendo `FileWriter` para escrita em lote eficiente em disco físico, mitigando degradação de E/S.
- **Padrão de Serialização Estruturada:** Encapsulamento da representação textual na própria entidade (`salvarDados()` gerando linha delimitada e static factory `fromCsv()` para desserialização).
- **Tratamento de Recursos com `try-with-resources`:** Fechamento determinístico de descritores de arquivo sem vazamento de memória ou locks residuais.

## Sinapses
- Conectado a [[Cortex_Central]], [[Operador]] e [[Padroes_Engenharia]].
- Relacionado a padrões de arquitetura de software corporativo e sistemas resilientes.
- Alinhado aos padrões de execução de pipelines em [[Continuous_Runtime]].
