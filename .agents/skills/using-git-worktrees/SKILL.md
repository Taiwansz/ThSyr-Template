---
name: using-git-worktrees
description: Use when starting parallel feature branches, spike explorations, or subagent tasks requiring physical filesystem isolation from the main workspace.
---

# Using Git Worktrees (Isolamento Topologico de Workspace)

## Visao Geral

Garantir que exploracoes experimentais, refatoracoes pesadas ou execucoes paralelas ocorram em arvores de trabalho fisicamente isoladas, impedindo a contaminacao da branch e do diretorio principal.

## Principio Sagital

Detectar isolamento preexistente primeiro. Utilizar comandos nativos de git worktree. Nunca poluir a branch ativa do operador.

## Procedimento de 4 Etapas

### Etapa 0: Inspecionar Isolamento Atual

Antes de criar qualquer estrutura, verificar se o ambiente ja opera dentro de uma linked worktree:

```bash
git rev-parse --git-dir
git rev-parse --git-common-dir
```

- Se `git-dir` for diferente de `git-common-dir`, o processo ja reside dentro de uma worktree isolada. Nao criar outra worktree.
- Se forem identicos, o processo esta na raiz principal do repositorio.

### Etapa 1: Garantir Ignorancia no .gitignore

Se o diretorio de worktrees for local ao projeto (ex: `.worktrees/`), verificar compulsoriamente se ele esta no `.gitignore`:

```bash
git check-ignore -q .worktrees || echo ".worktrees/" >> .gitignore
```

Isso impede que arquivos de outra branch sejam comitados acidentalmente na arvore principal.

### Etapa 2: Instanciacao da Worktree

Criar a arvore isolada apontando para a nova branch:

```bash
git worktree add .worktrees/<nome-da-branch> -b <nome-da-branch>
```

Em seguida, executar comandos ou orquestrar agentes dentro de `.worktrees/<nome-da-branch>`.

### Etapa 3: Baseline e Limpeza

1. Apos entrar na worktree, rodar a instalacao de dependencias se necessario.
2. Executar a suite de testes basica para confirmar um baseline verde antes de qualquer modificacao de codigo.
3. Ao finalizar a tarefa, fazer o merge/push correspondente e remover a worktree para liberar espaco em disco:

```bash
git worktree remove .worktrees/<nome-da-branch>
```
