---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, or passing, before committing or creating PRs. Requires running verification commands and confirming output before making any success claims; evidence before assertions always.
---

# Verification Before Completion

## Visao Geral

Principio sagital: Evidencia antes de qualquer afirmacao.

Violar a letra deste processo e violar a integridade da execucao.

## A Lei de Ferro

```
PROIBIDO DECLARAR CONCLUSAO SEM EVIDENCIA RECEM-EXECUTADA
```

Se o comando de verificacao nao foi executado na mensagem atual ou imediatamente antes da afirmacao, e proibido alegar que a suite passa, o bug foi corrigido ou o sistema esta pronto.

## O Portao de Verificacao

Antes de emitir qualquer declaracao de conclusao ou status positivo:

1. IDENTIFICAR: Qual comando fisico no terminal prova esta afirmacao de forma inequivoca?
2. EXECUTAR: Rodar o comando completo e fresco no ambiente real (sem atalhos, sem suposicoes).
3. INSPECIONAR: Ler a saida completa, verificar o exit code (0), inspecionar stderr e contagem de falhas.
4. CONFIRMAR: A saida do comando confirma categoricamente a afirmacao?
   - Se NAO: Expor o status real com a evidencia da falha. Proibido atenuar o erro.
   - Se SIM: Expor a conclusao anexando os dados brutos da execucao.
5. APENAS ENTAO: Declarar o checkpoint ou tarefa como concluida.

Pular qualquer etapa e violacao do protocolo sagital.

## Tabela de Correspondencia de Evidencias

| Afirmacao | Requisito Obrigatorio | Evidencia Insuficiente |
|---|---|---|
| Testes passaram | Saida do comando de teste com 0 falhas (ex: pytest, npm test) | Execucao passada, "deve passar", log parcial |
| Linter limpo | Saida do linter com 0 erros/warnings | Inspecao visual, extrapolacao |
| Build bem-sucedido | Comando de build finalizado com exit code 0 | Apenas linter ter passado |
| Bug corrigido | Teste de regressao comprovando a falha antes e o sucesso apos | Codigo alterado sem execucao |
| Subagente concluiu | Inspecao do diff fisico no disco (`git diff`) | Relatorio de texto do subagente alegando sucesso |
| Requisitos atendidos | Checklist ponto a ponto validado contra arquivos | Afirmar generalidades |

## Bandeiras Vermelhas (Sinais de Alerta)

- Emprego de termos evasivos: "deve funcionar", "provavelmente", "parece correto", "supostamente".
- Expressar alivio ou comemoracao antes da execucao dos testes ("Pronto!", "Perfeito!", "Resolvido!").
- Tentar commitar, subir branch ou enviar push sem ter visto o comando verde na mesma sessao.
- Confiar cegamente em output textual de subagentes ou modelos auxiliares sem inspecionar os arquivos gerados.

## Padroes de Execucao

### Testes
- Correto: Executar comando de teste -> Inspecionar: 34 passed em X segundos -> Declarar: "Testes validados com 34/34 sucessos".
- Violacao: "O codigo foi corrigido e agora deve passar em todos os testes".

### Build e Tipagem
- Correto: Rodar `npm run build` ou `tsc --noEmit` -> Obter exit code 0 -> Declarar build integro.
- Violacao: "O linter passou, logo o build passara".
