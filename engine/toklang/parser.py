"""
TokLang Recursive Descent Parser
Converte sequencias de tokens em uma Arvore Sintatica Abstrata (PromptDocument AST).
"""

from typing import Any

from .ast_nodes import (
    AttentionConstraint,
    CompressionDirective,
    ContextBlock,
    InstructionBlock,
    PromptDocument,
    TokenBudgetDirective,
)
from .lexer import Token, TokenType


class TokLangParser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def _peek(self) -> Token:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else Token(TokenType.EOF, "", -1, -1)

    def _advance(self) -> Token:
        t = self._peek()
        if self.pos < len(self.tokens):
            self.pos += 1
        return t

    def _match(self, t_type: TokenType, value: str | None = None) -> bool:
        t = self._peek()
        if t.type == t_type:
            if value is None or t.value == value:
                self._advance()
                return True
        return False

    def _expect(self, t_type: TokenType, error_msg: str) -> Token:
        t = self._peek()
        if t.type != t_type:
            raise SyntaxError(f"Erro sintatico [linha {t.line}, col {t.column}]: {error_msg}. Encontrado: {t.value}")
        return self._advance()

    def _parse_kwargs(self) -> dict[str, Any]:
        """Analisa argumentos no formato (key="val", key=123, ...)."""
        kwargs: dict[str, Any] = {}
        if not self._match(TokenType.LPAREN):
            return kwargs

        while not self._match(TokenType.RPAREN):
            key_token = self._expect(TokenType.IDENTIFIER, "Esperado nome de parametro")
            self._expect(TokenType.EQUALS, "Esperado '=' apos parametro")
            val_token = self._peek()

            if val_token.type == TokenType.STRING:
                kwargs[key_token.value] = self._advance().value
            elif val_token.type == TokenType.NUMBER:
                kwargs[key_token.value] = int(self._advance().value)
            elif val_token.type == TokenType.IDENTIFIER:
                val = self._advance().value
                if val.lower() == "true":
                    kwargs[key_token.value] = True
                elif val.lower() == "false":
                    kwargs[key_token.value] = False
                else:
                    kwargs[key_token.value] = val
            else:
                self._advance()

            self._match(TokenType.COMMA)

        return kwargs

    def parse(self) -> PromptDocument:
        doc = PromptDocument()

        while self._peek().type != TokenType.EOF:
            t = self._peek()

            # Diretivas
            if t.type == TokenType.DIRECTIVE:
                dir_name = self._advance().value.lower()
                kwargs = self._parse_kwargs()

                if dir_name == "@compress":
                    doc.compression = CompressionDirective(
                        level=kwargs.get("level", "balanced"),
                        target=kwargs.get("target", "semantic"),
                        drop_stopwords=kwargs.get("drop_stopwords", True)
                    )
                elif dir_name == "@budget":
                    doc.budget = TokenBudgetDirective(
                        max_tokens=kwargs.get("max_tokens", 1000),
                        reserve_completion=kwargs.get("reserve_completion", 250)
                    )
                elif dir_name == "@constraint":
                    focus = kwargs.get("focus", "")
                    focus_list = [f.strip() for f in focus.split(",")] if isinstance(focus, str) and focus else []
                    doc.constraints.append(AttentionConstraint(
                        name=kwargs.get("name", "unnamed"),
                        focus_terms=focus_list,
                        strictly_inviolable=kwargs.get("strictly_inviolable", True)
                    ))
                continue

            # Blocos context / instruction
            if t.type == TokenType.IDENTIFIER:
                block_type = self._advance().value.lower()

                # Bloco de contexto
                if block_type == "context":
                    name = "default"
                    if self._peek().type in (TokenType.STRING, TokenType.IDENTIFIER):
                        name = self._advance().value
                    self._expect(TokenType.LBRACE, "Esperado '{' para iniciar bloco context")
                    content_parts = []
                    while not self._match(TokenType.RBRACE):
                        if self._peek().type == TokenType.EOF:
                            raise SyntaxError("Fim de arquivo inesperado dentro do bloco context.")
                        content_parts.append(self._advance().value)
                    doc.contexts.append(ContextBlock(name=name, content=" ".join(content_parts)))
                    continue

                # Bloco de instrucoes
                if block_type == "instruction":
                    self._expect(TokenType.LBRACE, "Esperado '{' para iniciar bloco instruction")
                    inst_parts = []
                    while not self._match(TokenType.RBRACE):
                        if self._peek().type == TokenType.EOF:
                            raise SyntaxError("Fim de arquivo inesperado dentro do bloco instruction.")
                        tok = self._advance()
                        if tok.type in (TokenType.STRING, TokenType.IDENTIFIER):
                            inst_parts.append(tok.value)
                    doc.instruction = InstructionBlock(instructions=inst_parts)
                    continue

            self._advance()

        return doc
