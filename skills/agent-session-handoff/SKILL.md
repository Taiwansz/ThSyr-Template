---
name: agent-session-handoff
description: "Context preservation and session handoff skill for AI coding agents. Enforces automated generation of structured SESSION_STATE.md files when wrapping up work or hitting context window limits. Captures completed tasks, active uncommitted changes, architectural decisions made, and the exact next command to run in the following session."
argument-hint: "[save | resume]"
license: MIT
metadata:
  author: Code Makers & PromptVault
  version: "1.0.0"
---

# Agent Session Handoff — Persistência de Memória Entre Sessões

#categoria-ambas #memoria #handoff #produtividade #contexto #governanca

Esta skill elimina o problema crônico de **amnésia entre sessões** de agentes de IA (Antigravity, Claude Code, Cursor). Quando o desenvolvedor encerra o dia de trabalho ou a janela de contexto atinge o limite, esta skill compacta o estado mental do agente em um arquivo padronizado `SESSION_STATE.md`, permitindo retomar o trabalho no dia seguinte instantaneamente.

---

## 1. Protocolo de Fechamento de Sessão (`[session-handoff]`)

Ao final do expediente ou antes de resetar a conversa, o agente deve executar este protocolo:

1. **Auditar o Estado do Git:**
   - Verificar arquivos alterados, novos e não commitados (`git status`).
2. **Sintetizar Decisões Técnicas:**
   - Registrar qualquer decisão de banco, pacote instalado ou regra de negócio acordada durante a sessão.
3. **Gerar ou Sobrescrever `SESSION_STATE.md` na raiz do projeto:**

```markdown
# SESSION_STATE — [Data e Hora]

## 1. Objetivo da Sessão
- [Ex: Implementação do fluxo de agendamento online com Supabase]

## 2. O Que Foi Concluído Nesta Sessão
- [x] Criação da tabela `appointments` com RLS ativado.
- [x] Server Action `createAppointmentAction` validada com Zod.
- [x] Componente visual de calendário interativo com Tailwind.

## 3. Trabalho em Andamento (Em Aberto)
- [ALERTA]️ **Arquivo em edição:** `app/api/webhooks/stripe/route.ts`
- [ALERTA]️ **Onde paramos:** Falta validar a assinatura do webhook e testar o evento de estorno.

## 4. Decisões de Arquitetura Críticas
- Optamos por salvar horários em UTC no banco e converter para o fuso local (`America/Sao_Paulo`) no frontend.
- O campo `client_phone` agora usa sanitização regex para remover caracteres especiais antes do insert.

## 5. Próximo Passo Exato para a Próxima Sessão (Comando de Retomada)
> *"Continue a partir do arquivo `app/api/webhooks/stripe/route.ts`. O objetivo imediato é rodar o teste com Stripe CLI (`stripe trigger payment_intent.succeeded`) e validar a inserção na tabela `processed_webhooks`."*
```

---

## 2. Protocolo de Retomada de Sessão (`[session-resume]`)

Ao iniciar uma nova sessão ou novo chat no projeto:

1. O agente deve verificar silenciosamente se o arquivo `SESSION_STATE.md` existe na raiz do projeto.
2. Se existir, ler o arquivo antes de sugerir qualquer código ou fazer perguntas repetitivas.
3. Iniciar a primeira resposta confirmando o ponto onde parou:
   > *"Li o `SESSION_STATE.md`. Na última sessão concluímos o agendamento no Supabase e paramos na validação do webhook do Stripe. Vamos continuar a partir do teste com o Stripe CLI?"*
