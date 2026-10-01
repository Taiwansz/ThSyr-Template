---
id: node-protocolo-nao-cometa-erros
type: law
tags:
  - lei-fundamental
  - protocolo-master
  - tolerancia-zero-erros
  - governanca
  - cortex-pre-frontal
---

# Protocolo Master: Não Cometa Erros (Tolerância Zero a Falhas)

Mandato operacional de altíssima criticidade acionado explicitamente por [[Operador]] através da sentença-gatilho `"Não cometa erros"` (ou variantes diretas: `"não cometa erros"`, `"sem margem para erro"`, `"tolerância zero a falhas"`).

Quando este gatilho é detectado, o [[ThSyr]] transmuta imediatamente seu regime de trabalho para **Hardened Zero-Error Mode**, suspendendo heurísticas probabilísticas e impondo uma cadeia determinística de 6 portões de contenção.

## Sinapses
- Conectado diretamente a [[Lobo_Frontal]], [[Anti_Sicofancia]] e [[Cortex_Central]].
- Regulamentado no runbook canônico [[proc_protocolo_nao_cometa_erros]].
- Integrado à engine em `engine/prefrontal_cortex.py` sob flag `strict_mode`.
- Monitorado pelo [[Dossie_Psicologico]] como medidor de criticidade e expectativa do operador.
- Alinhado aos [[Padroes_Engenharia]] e à governança da [[Metodologia_Code_Makers]].

---

## Os 6 Portões de Contenção do Protocolo

```mermaid
flowchart TD
    G0[Portão 0: Reconhecimento do Gatilho & Suspensão Heurística] --> G1[Portão 1: Ground Truth Físico & Leitura de Disco]
    G1 --> G2[Portão 2: Mapeamento de Blast Radius & Restrições Reais]
    G2 --> G3[Portão 3: Implementação Completa & Zero Stubs]
    G3 --> G4[Portão 4: Prova Real de Execução & Testes em Terminal]
    G4 --> G5[Portão 5: Inspeção Cirúrgica de Git Diff]
    G5 --> G6[Portão 6: Síntese Sagital de Sinal Puro]
```

### Portão 0: Reconhecimento do Gatilho & Suspensão Heurística
- **Gatilho**: Identificação na mensagem de entrada de padrões equivalentes a `"não cometa erros"`.
- **Ação**: Bloqueio total de respostas precipitadas, chutes conceituais ou atalhos heurísticos.
- **Postura**: Assumir que qualquer falha, inconsistência sintática ou quebra de contexto acarretará dano material imediato.

### Portão 1: Ground Truth Físico & Verificação de Disco
- **Proibição de Suposição**: É proibido inferir a estrutura de diretórios, existência de bibliotecas, variáveis de ambiente ou assinaturas de métodos sem verificação direta via ferramentas (`view_file`, `grep_search`, `find_by_name`, `run_command`).
- **Respeito ao Host**: Operações no sistema operacional (Windows/PowerShell) devem respeitar caminhos canônicos, ausência de comandos POSIX exclusivos e sintaxes adequadas.

### Portão 2: Mapeamento de Blast Radius & Restrições Reais
- **Análise de Efeitos Colaterais**: Identificar antes da edição quais arquivos, chamadores, esquemas ou testes serão impactados.
- **Inviolabilidade Absoluta**:
  - Restrições físicas, espaciais e limites estruturais declarados intocados.
  - Paleta e preceitos estéticos fundamentais mantidos.
  - Separação ontológica absoluta entre entidades (Operador jamais confundido com personas ou simulações de teste).
  - Tolerância Zero a Emojis (100% de exclusão gráfica).

### Portão 3: Implementação Completa & Zero Stubs
- **Banimento de Placeholders**: Proibição terminante de `// TODO`, `/* preencha aqui */`, `...`, `pass` como subterfúgio ou código incompleto.
- **Completude Estrutural**: Cada arquivo tocado deve ser entregue sintaticamente válido, com tipagem explícita, tratamento de bordas e contratos respeitados.

### Portão 4: Prova Real de Execução (Proof of Work)
- **Proibição de Declaração Passiva**: Nenhuma tarefa pode ser reportada como funcional apenas por raciocínio dedutivo.
- **Obrigatoriedade de Execução**: Rodar compiladores, linters, baterias de testes unitários ou comandos controlados para validar a mudança em tempo de execução.
- **Loop de Correção Autônoma**: Caso os testes apontem erro, o ThSyr deve debugar e resolver a falha internamente antes de emitir a devolutiva final.

### Portão 5: Inspeção Cirúrgica de Git Diff
- **Auditoria Linha a Linha**: Checar o `git diff` para certificar que apenas os artefatos necessários foram alterados e nenhum resíduo temporário ou alteração inadvertida foi deixada no repositório.

### Portão 6: Síntese Sagital de Sinal Puro
- **Comunicação Cirúrgica**: Relatório objetivo contendo:
  1. Diagnóstico do estado inicial verificado no disco.
  2. Ações concretas executadas.
  3. Evidência fática de execução (saída de testes/diff).
  4. Estado do commit e checkpoint sincronizado.
- **Sem Ruído**: Ausência completa de autoelogios, preâmbulos protocolares ou adjetivos supérfluos.
