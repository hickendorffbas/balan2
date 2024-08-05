import sys

from enum import Enum


class TokenType(Enum):
    IDENTIFIER = 1
    NUMBER = 2
    OPEN_PARENTHESIS = 3
    CLOSE_PARENTHESIS = 4
    SEMICOLON = 5
    COMMA = 6




with open(sys.argv[1], "r") as code_file:
    code_text = code_file.read()


NON_IDENT_CHARS = ["\n", " ", "\t", "(", ")", ";", ","]
BUILTIN_FUNCTION_NAMES = ["print"]

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
    elif cur_char == ",":
        tokens.append( (TokenType.COMMA, None) )
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
        raise Exception(f"ERROR: unknown token: {cur_char}")

    idx += 1



print(tokens)


class AstBuiltinFunction:

    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class AstNumber:

    def __init__(self, number):
        self.number = number




def parse_expression(tokens):
    if len(tokens) == 1:
        if tokens[0][0] == TokenType.NUMBER:
            return AstNumber(tokens[0][1])

        raise Exception(f"ERROR: unparsable tokens: {tokens}", )


    if tokens[0][0] == TokenType.IDENTIFIER and tokens[0][1] in BUILTIN_FUNCTION_NAMES and tokens[1][0] == TokenType.OPEN_PARENTHESIS:
        function_name = tokens[0][1]

        #TODO: enormous hack below (removing close parenthesis):
        tokens = tokens[2:-1]

        argument_tokens_list = split_tokens(tokens, TokenType.COMMA)
        print("Args", argument_tokens_list)

        arguments_asts = []
        for argument_tokens in argument_tokens_list:
            argument_ast = parse_expression(argument_tokens)
            arguments_asts.append(argument_ast)

        return AstBuiltinFunction(function_name, arguments_asts)


    raise Exception(f"ERROR: can't parse {tokens}")




def get_tokens_until_type(tokens, start_idx, token_type):
    idx = start_idx
    while idx < len(tokens):
        if tokens[idx][0] == token_type:
            break
        idx += 1
    return tokens[start_idx:idx], idx


def split_tokens(tokens, token_type):
    splits = []

    cur_split = []
    for token in tokens:
        if token[0] == token_type:
            if cur_split:
                splits.append(cur_split)
                cur_split = []
        else:
            cur_split.append(token)
    if cur_split:
        splits.append(cur_split)
    return splits




idx = 0
ast_statements = []


statement_tokens_list = split_tokens(tokens, TokenType.SEMICOLON)


for statement_tokens in statement_tokens_list:
    print("statement: {}", statement_tokens)
    expression_statement = parse_expression(statement_tokens)

    ast_statements.append(expression_statement)

print(ast_statements)





