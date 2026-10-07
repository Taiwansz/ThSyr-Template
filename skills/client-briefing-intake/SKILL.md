---
name: client-briefing-intake
description: "Intake and synthesis skill that converts messy, unstructured client materials (WhatsApp audios, disorganized notes, PDF menus, meeting transcripts) into a clean, structured Step 1 Diagnostic. Extracts business rules, pricing, differentials, target audience, and isolates 3-5 critical blocking questions before architecture begins."
argument-hint: "[client-materials or raw-notes]"
license: MIT
metadata:
  author: Code Makers & PromptVault
  version: "1.0.0"
---

# Client Briefing Intake — O Decodificador de Clientes do Mundo Real

#categoria-cowork #briefing #diagnostico #clientes #negocios #etapa-1

Esta skill é a ponte entre o cliente da vida real e o desenvolvimento profissional com IA. Clientes nunca enviam um PRD arrumado; eles enviam áudios desconexos de WhatsApp, rascunhos em guardanapo, prints de cardápios antigos e listas confusas de desejos.

Esta skill processa essa enxurrada de dados desorganizados e entrega exatamente a documentação da **Etapa 1 (Diagnóstico)** do Framework Universal.

---

## 1. Protocolo de Ingestão e Limpeza

Ao receber áudios transcritos, anotações de reunião ou materiais brutos do cliente:

1. **Separação Rigorosa de Fatos vs. Desejos:**
   - **Fatos (Regras de Negócio):** Preços atuais, catálogo de serviços prestados, horários de atendimento, equipe, endereço, formas de pagamento aceitas.
   - **Desejos/Ideias Vagas:** *"Quero que pareça a Apple"*, *"Quero algo moderno e inovador"*, *"Talvez no futuro a gente tenha um blog"*. (Isole em backlog futuro).
2. **Caça a Contradições Internas:**
   - Identifique pontos onde o cliente se contradiz (ex: fala que quer focar em público de alto padrão, mas quer colocar banners piscando de promoção popular).
3. **Mapeamento de Restrições Críticas:**
   - O que o cliente **NÃO** faz de jeito nenhum.
   - Limites de prazo, orçamento ou ferramentas que ele já utiliza e se recusa a trocar.

---

## 2. Estrutura de Saída Obrigatória (Template de Diagnóstico)

A skill deve formatar a saída exatamente neste formato para aprovação:

```markdown
# Diagnóstico e Definição de Projeto — [Nome do Cliente/Negócio]

## 1. Resumo Executivo & Proposta de Valor Real
- **O que a empresa realmente vende:** (Em 1 frase direta, sem termos corporativos vagos).
- **Para quem vende (Persona Principal):** (Quem é o comprador ideal, sua urgência e sua principal dor).
- **O Grande Diferencial Competitivo:** (Por que alguém compra deles e não do concorrente ao lado).

## 2. Catálogo Estruturado de Ofertas & Preços
| Serviço / Produto | Descrição Objetiva | Faixa de Preço | Condições / Prazos |
| :--- | :--- | :--- | :--- |
| [Ex: Corte Degradê] | [Serviço com lavagem] | [R$ 60,00] | [30 min] |

## 3. Delimitação Estrita de Escopo
- [OK] **O que ESTÁ incluído na entrega:** (Ex: Agendamento via WhatsApp, catálogo de fotos reais, mapa de localização).
- [ERRO] **O que NÃO ESTÁ incluído (Backlog):** (Ex: Sistema de fidelidade com pontos, app nativo iOS, gateway de pagamento complexo).

## 4. Identidade, Ativos & Tom de Voz
- **Ativos Existentes:** (Logo em PNG/SVG, fotos do espaço físico, cores predominantes).
- **Tom de Comunicação:** (Ex: Direto, acolhedor e profissional; sem formalidades excessivas).

## 5. Dúvidas Críticas Bloqueantes (Máximo 3 a 5 Perguntas)
*(Faça apenas perguntas que mudam decisões de arquitetura de software ou banco de dados)*
1. [Pergunta 1...]
2. [Pergunta 2...]
3. [Pergunta 3...]
```

---

## 3. Regra de Ouro da Etapa 1
>  **NÃO desenhe telas. NÃO gere código. NÃO crie paleta de cores CSS.**
> O único objetivo desta skill é extrair a verdade sobre o negócio do cliente e deixar a mesa 100% limpa para a Etapa 2 (Arquitetura).
