from dataclasses import dataclass
from enum import Enum

import balan_ast


class TokenType(Enum):
    NUMBER = 1
    IDENT = 2
    EOF = 3
    PLUS = 4
    MINUS = 5
    MULTIPLY = 6
    FORWARD_SLASH = 7
    STAR = 8
    EQUALS = 9
    PARENTHESIS_OPEN = 10
    PARENTHESIS_CLOSE = 11
    SEMICOLON = 12
    COLON = 13
    TYPE = 14
    COMMA = 15


CHAR_TOKEN_MAPPING = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.FORWARD_SLASH,
    "=": TokenType.EQUALS,
    "(": TokenType.PARENTHESIS_OPEN,
    ")": TokenType.PARENTHESIS_CLOSE,
    ";": TokenType.SEMICOLON,
    ":": TokenType.COLON,
    ",": TokenType.COMMA,
}


@dataclass
class Token:
    token_type: TokenType
    value: str


def lex(source: str):
    tokens = []
    i = 0

    while i < len(source):
        c = source[i]

        if c.isspace():
            i += 1

        elif c.isdigit():
            start = i
            while i < len(source) and source[i].isdigit():
                i += 1
            tokens.append(Token(TokenType.NUMBER, source[start:i]))

        elif c.isalpha() or c == "_":
            start = i
            while i < len(source) and (source[i].isalnum() or source[i] == "_"):
                i += 1

            word = source[start:i]

            if word in balan_ast.TYPE_KEYWORDS_MAPPING:
                tokens.append(Token(TokenType.TYPE, word))
            else:
                tokens.append(Token(TokenType.IDENT, word))

        elif c in CHAR_TOKEN_MAPPING.keys():
            tokens.append(Token(CHAR_TOKEN_MAPPING[c], c))
            i += 1

        else:
            raise SyntaxError(f"Unexpected character: {c}")

    tokens.append(Token(TokenType.EOF, ""))
    return tokens
