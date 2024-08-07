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




BUILTIN_FUNCTION_OPCODES = {
    "print": 1,
}
BUILTIN_FUNCTIONS_NUMBER_OF_ARGS = {
    1: 1,
}


class AstBuiltinFunction:

    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def generate(self):

        if self.name in BUILTIN_FUNCTION_OPCODES:
            opcode = BUILTIN_FUNCTION_OPCODES[self.name]
        else:
            raise Exception("Unknown builtin")

        expected_number_of_args = BUILTIN_FUNCTIONS_NUMBER_OF_ARGS[opcode]

        if len(self.arguments) != expected_number_of_args:
            raise Exception("Invalid number of args supplied to builtin function")

        code = []
        for arg in self.arguments:
            code = code + arg.generate()

        return code + [opcode]


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
        left_code = self.left.generate()
        right_code = self.right.generate()

        if self.op == "+":
            binop_opcode = 3
        else:
            raise Exception("operation not implemented")

        return left_code + right_code + [binop_opcode]


def parse_expression(tokens):
    blocked_tokens = block_tokens(tokens, TokenType.OPEN_PARENTHESIS, TokenType.CLOSE_PARENTHESIS)

    if len(tokens) == 1:
        if tokens[0][0] == TokenType.NUMBER:
            return AstNumber(tokens[0][1])

        raise Exception(f"ERROR: unparsable tokens: {tokens}", )


    if tokens[0][0] == TokenType.IDENTIFIER and tokens[0][1] in BUILTIN_FUNCTION_OPCODES.keys() and tokens[1][0] == TokenType.OPEN_PARENTHESIS:
        function_name = tokens[0][1]

        #TODO: enormous hack below (removing close parenthesis):
        tokens = tokens[2:-1]

        argument_tokens_list = split_tokens(tokens, blocked_tokens, TokenType.COMMA)

        arguments_asts = []
        for argument_tokens in argument_tokens_list:
            argument_ast = parse_expression(argument_tokens)
            arguments_asts.append(argument_ast)

        return AstBuiltinFunction(function_name, arguments_asts)


    token_types = [token[0] for token in blocked_tokens]
    if TokenType.PLUS in token_types:
        plus_split = split_tokens(tokens, blocked_tokens, TokenType.PLUS)

        left = parse_expression(plus_split[0])
        right = parse_expression(plus_split[1])

        return AstBinOp("+", left, right)


    raise Exception(f"ERROR: can't parse {tokens}")



def block_tokens(tokens, start_delim_type, end_delim_type):
    nesting = 0
    blocked_tokens = []

    for tok in tokens:
        if tok[0] == end_delim_type:
            nesting =- 1
        if nesting == 0:
            blocked_tokens.append(tok)
        else:
            blocked_tokens.append( (None, None) )
        if tok[0] == start_delim_type:
            nesting += 1

    return blocked_tokens



def get_tokens_until_type(tokens, start_idx, token_type):
    idx = start_idx
    while idx < len(tokens):
        if tokens[idx][0] == token_type:
            break
        idx += 1
    return tokens[start_idx:idx], idx


def split_tokens(tokens, blocked_tokens, token_type):
    splits = []

    cur_split = []
    for idx in range(0, len(tokens)):
        if blocked_tokens[idx][0] == token_type:
            if cur_split:
                splits.append(cur_split)
                cur_split = []
        else:
            cur_split.append(tokens[idx])
    if cur_split:
        splits.append(cur_split)
    return splits




idx = 0
ast_statements = []


statement_tokens_list = split_tokens(tokens, tokens, TokenType.SEMICOLON)


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

