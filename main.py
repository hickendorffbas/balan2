import sys

from enum import Enum


class TokenType(Enum):
    IDENTIFIER = 1
    NUMBER = 2
    OPEN_PARENTHESIS = 3
    CLOSE_PARENTHESIS = 4
    SEMICOLON = 5




with open(sys.argv[1], "r") as code_file:
    code_text = code_file.read()


NON_IDENT_CHARS = ["/n", " ", "/t", "(", ")", ";"]


tokens = []

idx = 0
while idx < len(code_text):
    cur_char = code_text[idx]

    if cur_char == "(":
        tokens.append( (TokenType.OPEN_PARENTHESIS, None) )
    elif cur_char == ")":
        tokens.append( (TokenType.CLOSE_PARENTHESIS, None) )
    elif cur_char == ";":
        tokens.append( (TokenType.SEMICOLON, None) )
    elif cur_char in (" ", "\n", "\t"):
        pass

    elif cur_char.isnumeric():
        number = ""
        while idx < len(code_text) and code_text[idx].isnumeric():
            number += code_text[idx]
            idx += 1
        tokens.append( (TokenType.NUMBER, number) )
        continue

    elif cur_char not in NON_IDENT_CHARS:
        identifier = ""
        while idx < len(code_text) and code_text[idx] not in NON_IDENT_CHARS:
            identifier += code_text[idx]
            idx += 1;
        tokens.append( (TokenType.IDENTIFIER, identifier) )
        continue

    else:
        print("ERROR: unknown token: {}", cur_char)

    idx += 1

print(tokens)

