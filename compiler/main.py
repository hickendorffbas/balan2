import sys

from enum import Enum


class TokenType(Enum):
    IDENTIFIER = 1
    NUMBER = 2
    OPEN_PARENTHESIS = 3
    CLOSE_PARENTHESIS = 4
    SEMICOLON = 5
    COMMA = 6
    PLUS = 7
    MINUS = 8
    TIMES = 9
    FORWARD_SLASH = 10



with open(sys.argv[1], "r") as code_file:
    code_text = code_file.read()


NON_IDENT_CHARS = ["\n", " ", "\t", "(", ")", ";", ",", "+", "-", "/", "*"]
BUILTIN_FUNCTION_NAMES = ["print"]

tokens = []

DIRECT_TOKEN_MAPPING = {
    "(": TokenType.OPEN_PARENTHESIS,
    ")": TokenType.CLOSE_PARENTHESIS,
    ";": TokenType.SEMICOLON,
    ",": TokenType.COMMA,
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.TIMES,
    "/": TokenType.FORWARD_SLASH,
}

idx = 0
while idx < len(code_text):
    cur_char = code_text[idx]

    if cur_char in DIRECT_TOKEN_MAPPING:
        tokens.append( (DIRECT_TOKEN_MAPPING[cur_char], None) )

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


BUILTIN_OPCODES = {
    "print": 1,
}

class AstBuiltinFunction:

    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def generate(self):
        code = self.arguments[0].generate() #TODO: handle unexpected number of args

        print("len ", len(self.arguments))

        if self.name in BUILTIN_OPCODES:
            return code + [BUILTIN_OPCODES[self.name]]
        else:
            raise Exception("Unknown builtin")


class AstNumber:

    def __init__(self, number):
        self.number = number

    def generate(self):
        return [2, int(self.number)]


class AstBinOp:

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def generate(self):
        print("L", self.left.number)
        print("R", self.right.number)


        left_code = self.left.generate()
        right_code = self.right.generate()

        print("CC", left_code, right_code)

        if self.op == "+":
            binop_opcode = 3
        else:
            raise Exception("operation not implemented")

        print(left_code + right_code + [binop_opcode])
        return left_code + right_code + [binop_opcode]


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


    #TODO: we need the blackout stuff
    token_types = [token[0] for token in tokens]
    if TokenType.PLUS in token_types:
        plus_split = split_tokens(tokens, TokenType.PLUS)

        left = parse_expression(plus_split[0])
        right = parse_expression(plus_split[1])

        return AstBinOp("+", left, right)


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
    expression_statement = parse_expression(statement_tokens)

    ast_statements.append(expression_statement)


bytes_to_write = []
for statement in ast_statements:
    bytes_to_write.extend(statement.generate())


print(bytes_to_write)


bb2_file = open("test.bb2", "wb")
for byte in bytes_to_write:
    bb2_file.write(byte.to_bytes(1, byteorder='big'))

