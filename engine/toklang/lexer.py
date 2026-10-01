"""
TokLang Lexer & Tokenizer
Realiza analise lexica de scripts TokLang para geracao de sequencia de tokens tipados.
"""

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    DIRECTIVE = auto()     # @compress, @budget, @constraint
    IDENTIFIER = auto()    # context, instruction, name
    STRING = auto()        # "...", '...'
    NUMBER = auto()        # 1000, 250
    LBRACE = auto()        # {
    RBRACE = auto()        # }
    LPAREN = auto()        # (
    RPAREN = auto()        # )
    EQUALS = auto()        # =
    COMMA = auto()         # ,
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int


class TokLangLexer:
    def __init__(self, source: str):
        self.source = source
        self.length = len(source)
        self.pos = 0
        self.line = 1
        self.col = 1

    def _peek(self) -> str | None:
        return self.source[self.pos] if self.pos < self.length else None

    def _advance(self) -> str | None:
        if self.pos >= self.length:
            return None
        char = self.source[self.pos]
        self.pos += 1
        if char == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return char

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []

        while self.pos < self.length:
            char = self._peek()
            if char is None:
                break

            # Pular espacos em branco
            if char in (" ", "\t", "\r", "\n"):
                self._advance()
                continue

            # Comentarios (# ou //)
            if char == "#" or (char == "/" and self.pos + 1 < self.length and self.source[self.pos + 1] == "/"):
                while self.pos < self.length and self._peek() != "\n":
                    self._advance()
                continue

            cur_line = self.line
            cur_col = self.col

            # Diretivas (@compress, @budget, etc)
            if char == "@":
                self._advance()
                val = ""
                while self.pos < self.length:
                    pk = self._peek()
                    if pk and (pk.isalnum() or pk == "_"):
                        adv = self._advance()
                        if adv is not None:
                            val += adv
                    else:
                        break
                tokens.append(Token(TokenType.DIRECTIVE, f"@{val}", cur_line, cur_col))
                continue

            # Strings
            if char in ('"', "'"):
                quote = self._advance()
                val = ""
                while self.pos < self.length:
                    pk = self._peek()
                    if pk is None or pk == quote:
                        break
                    if pk == "\\":
                        self._advance()
                        if self.pos < self.length:
                            adv = self._advance()
                            if adv is not None:
                                val += adv
                    else:
                        adv = self._advance()
                        if adv is not None:
                            val += adv
                if self.pos < self.length:
                    self._advance()  # consome quote final
                tokens.append(Token(TokenType.STRING, val, cur_line, cur_col))
                continue

            # Numeros
            if char.isdigit():
                val = ""
                while self.pos < self.length:
                    pk = self._peek()
                    if pk and pk.isdigit():
                        adv = self._advance()
                        if adv is not None:
                            val += adv
                    else:
                        break
                tokens.append(Token(TokenType.NUMBER, val, cur_line, cur_col))
                continue

            # Identificadores e palavras-chave
            if char.isalpha() or char == "_":
                val = ""
                while self.pos < self.length:
                    pk = self._peek()
                    if pk and (pk.isalnum() or pk in ("_", "-")):
                        adv = self._advance()
                        if adv is not None:
                            val += adv
                    else:
                        break
                tokens.append(Token(TokenType.IDENTIFIER, val, cur_line, cur_col))
                continue

            # Simbolos especiais
            if char == "{":
                self._advance()
                tokens.append(Token(TokenType.LBRACE, "{", cur_line, cur_col))
            elif char == "}":
                self._advance()
                tokens.append(Token(TokenType.RBRACE, "}", cur_line, cur_col))
            elif char == "(":
                self._advance()
                tokens.append(Token(TokenType.LPAREN, "(", cur_line, cur_col))
            elif char == ")":
                self._advance()
                tokens.append(Token(TokenType.RPAREN, ")", cur_line, cur_col))
            elif char == "=":
                self._advance()
                tokens.append(Token(TokenType.EQUALS, "=", cur_line, cur_col))
            elif char == ",":
                self._advance()
                tokens.append(Token(TokenType.COMMA, ",", cur_line, cur_col))
            else:
                self._advance()

        tokens.append(Token(TokenType.EOF, "", self.line, self.col))
        return tokens
