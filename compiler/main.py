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
    COLON = 11
    EQUALS = 12


with open(sys.argv[1], "r") as code_file:
    code_text = code_file.read()


NON_IDENT_CHARS = ["\n", " ", "\t", "(", ")", ";", ",", "+", "-", "/", "*", ":", "="]

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
    ":": TokenType.COLON,
    "=": TokenType.EQUALS,
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
OPCODE_PUSH = 2
OPCODE_ADD = 3
OPCODE_STORE = 4
OPCODE_LOAD = 5


VARS = {} #TODO: these are local vars, but I don't have functions yet, will need to be done differently in the future
NEXT_VAR_IDX = 0


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
        return [OPCODE_PUSH, int(self.number)]


class AstBinOp:

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def generate(self):
        left_code = self.left.generate()
        right_code = self.right.generate()

        if self.op == "+":
            binop_opcode = OPCODE_ADD
        else:
            raise Exception("operation not implemented")

        return left_code + right_code + [binop_opcode]


class AstVariable:

    def __init__(self, name):
        self.name = name

    def generate(self):
        return [OPCODE_LOAD, VARS[self.name]]


class AstAssign:

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def generate(self):
        right_code = self.right.generate()

        if type(self.left).__name__ == "AstVariable":
            address = VARS[self.left.name]
            return right_code + [OPCODE_STORE, address]

        if type(self.left).__name__ == "AstDeclaration":
            left_code = self.left.generate() #TODO: declarations can be halfway deep in statements (because assignment is an expression), so we'll need to hoist them to before the expression
            address = VARS[self.left.name]
            return left_code + right_code + [OPCODE_STORE, address]

        raise Exception("can't assign to something non variable yet")


class AstDeclaration:

    def __init__(self, name, var_type):
        self.name = name
        self.var_type = var_type

    def generate(self):
        #TODO: this is only correct if we hoist the declarations to before the current statement (make a tree operator for that)

        global NEXT_VAR_IDX
        #TODO: do something intelligent with the type
        #TODO: the id below is not always going to be correct, since it should go down when exitting a function
        VARS[self.name] = NEXT_VAR_IDX
        NEXT_VAR_IDX += 1
        int_default_value = 0
        return [OPCODE_PUSH, int_default_value]



def parse_expression(tokens):
    masked_token_types = [token[0] for token in mask_tokens(tokens, TokenType.OPEN_PARENTHESIS, TokenType.CLOSE_PARENTHESIS)] #TODO: eventually we also need to mask in braces and brackets, build that in one function, don't take the delimiters as arguments anymore

    if TokenType.EQUALS in masked_token_types:
        splits = split_tokens(tokens, masked_token_types, TokenType.EQUALS)
        left = parse_expression(splits[0])
        right = parse_expression(splits[1])

        return AstAssign(left, right)


    if len(tokens) == 1:
        if tokens[0][0] == TokenType.NUMBER:
            return AstNumber(tokens[0][1])
        if tokens[0][0] == TokenType.IDENTIFIER:
            return AstVariable(tokens[0][1])


    if TokenType.PLUS in masked_token_types:
        plus_split = split_tokens(tokens, masked_token_types, TokenType.PLUS)

        left = parse_expression(plus_split[0])
        right = parse_expression(plus_split[1])

        return AstBinOp("+", left, right)



    if len(tokens) > 2 and non_masked_types_equal(masked_token_types, [TokenType.IDENTIFIER, TokenType.OPEN_PARENTHESIS, TokenType.CLOSE_PARENTHESIS]) and tokens[0][1] in BUILTIN_FUNCTION_OPCODES.keys():
        builtin_name = tokens[0][1]

        argument_tokens = get_masked_tokens(tokens, masked_token_types)
        masked_argument_token_types = [token[0] for token in mask_tokens(argument_tokens, TokenType.OPEN_PARENTHESIS, TokenType.CLOSE_PARENTHESIS)]
        argument_tokens_list = split_all_tokens(argument_tokens, masked_argument_token_types, TokenType.COMMA)

        arguments_asts = []
        for argument_tokens in argument_tokens_list:
            argument_ast = parse_expression(argument_tokens)
            arguments_asts.append(argument_ast)

        return AstBuiltinFunction(builtin_name, arguments_asts)


    if TokenType.COLON in masked_token_types:

        splits = split_tokens(tokens, masked_token_types, TokenType.COLON)

        assert len(splits[0]) == 1  #TODO: proper error handling
        assert len(splits[1]) == 1  #TODO: proper error handling

        return AstDeclaration(splits[0][0][1], splits[1][0][1])



    raise Exception(f"ERROR: can't parse {tokens}")



def mask_tokens(tokens, start_delim_type, end_delim_type):
    nesting = 0
    masked_tokens = []

    for tok in tokens:
        if tok[0] == end_delim_type:
            nesting -= 1
        if nesting == 0:
            masked_tokens.append(tok)
        else:
            masked_tokens.append( (None, None) )
        if tok[0] == start_delim_type:
            nesting += 1

    return masked_tokens



def get_tokens_until_type(tokens, start_idx, token_type):
    idx = start_idx
    while idx < len(tokens):
        if tokens[idx][0] == token_type:
            break
        idx += 1
    return tokens[start_idx:idx], idx


def split_tokens(tokens, masked_token_types, token_type):
    idx = masked_token_types.index(token_type)
    return tokens[:idx], tokens[idx+1:]


def split_all_tokens(tokens, masked_token_types, token_type):
    splits = []
    cur_split = []
    for idx in range(0, len(tokens)):
        if masked_token_types[idx] == token_type:
            splits.append(cur_split)
            cur_split = []
        else:
            cur_split.append(tokens[idx])
    if cur_split:
        splits.append(cur_split)
    return splits


def non_masked_types_equal(masked_token_types, types_to_check):
    non_masked_token_types = [token_type for token_type in masked_token_types if token_type is not None]
    return non_masked_token_types == types_to_check


def get_masked_tokens(tokens, masked_token_types):
    return_tokens = []
    for idx in range(0, len(tokens)):
        if masked_token_types[idx] is None:
            return_tokens.append(tokens[idx])
    return return_tokens



idx = 0
ast_statements = []


masked_token_types = [token[0] for token in mask_tokens(tokens, TokenType.OPEN_PARENTHESIS, TokenType.CLOSE_PARENTHESIS)]
statement_tokens_list = split_all_tokens(tokens, masked_token_types, TokenType.SEMICOLON)


for statement_tokens in statement_tokens_list:
    expression_statement = parse_expression(statement_tokens)

    ast_statements.append(expression_statement)


bytes_to_write = []
for statement in ast_statements:
    bytes_to_write.extend(statement.generate())


print(bytes_to_write)


outfile_name = sys.argv[2]

bb2_file = open(outfile_name, "wb")
for byte in bytes_to_write:
    bb2_file.write(byte.to_bytes(1, byteorder='big'))

print("written " + outfile_name)

