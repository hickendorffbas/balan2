import sys

from dataclasses import dataclass
from enum import Enum

import balan_ast
from lexer import lex, TokenType


#TODO: make AST produce the existing bytecode


class Parser:

    INFIX_BP = {
        TokenType.PLUS: (10, 11),
        TokenType.MINUS: (10, 11),
        TokenType.STAR: (20, 21),
        TokenType.FORWARD_SLASH: (20, 21),
    }

    PREFIX_BP = 30

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # --------------------------------------------------------
    # Basic helpers
    # --------------------------------------------------------

    @property
    def current(self):
        return self.tokens[self.pos]

    def peek(self, offset=1):
        return self.tokens[self.pos + offset]

    def advance(self):
        token = self.current
        self.pos += 1
        return token

    def match(self, token_type):
        if self.current.token_type == token_type:
            return self.advance()
        return None

    def expect(self, token_type):
        token = self.advance()
        if token.token_type != token_type:
            raise SyntaxError(f"Expected {token_type}, got {token.token_type}")
        return token

    def parse(self):
        statements = []

        while self.current.token_type != TokenType.EOF:
            statements.append(self.parse_statement())
            self.match(TokenType.SEMICOLON)

        return balan_ast.AstProgram(statements)

    def parse_statement(self):
        if self.current.token_type == TokenType.IDENT and self.peek().token_type == TokenType.EQUALS:
            return self.parse_assignment()
        if self.current.token_type == TokenType.IDENT and self.peek().token_type == TokenType.COLON:
            return self.parse_declaration()

        expr = self.parse_expression()
        return balan_ast.AstExprStmt(expr)

    def parse_assignment(self):
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.EQUALS)
        value = self.parse_expression()
        return balan_ast.AstAssign(name, value)

    def parse_declaration(self):
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.COLON)
        type = self.expect(TokenType.TYPE).value
        if self.current.token_type == TokenType.EQUALS:
            self.expect(TokenType.EQUALS)
            initializer = self.parse_expression()
        else:
            initializer = None
        return balan_ast.AstDeclaration(name, type, initializer)

    def parse_expression(self, min_bp=0):
        left = self.parse_prefix()

        while True:
            token = self.current

            if token.token_type == TokenType.PARENTHESIS_OPEN:
                left = self.parse_function_call(left)
                continue

            if token.token_type not in self.INFIX_BP:
                break

            left_bp, right_bp = self.INFIX_BP[token.token_type]

            if left_bp < min_bp:
                break

            op = self.advance().value
            right = self.parse_expression(right_bp)
            left = balan_ast.AstBinaryOp(left, op, right)

        return left

    def parse_prefix(self):
        token = self.advance()

        if token.token_type == TokenType.NUMBER:
            return balan_ast.AstNumber(int(token.value))

        if token.token_type == TokenType.IDENT:
            return balan_ast.AstVariable(token.value)

        if token.token_type == TokenType.MINUS:
            operand = self.parse_expression(self.PREFIX_BP)
            return balan_ast.AstUnaryOp("-", operand)

        if token.token_type == TokenType.PARENTHESIS_OPEN:
            expr = self.parse_expression()
            self.expect(TokenType.PARENTHESIS_CLOSE)
            return expr

        raise SyntaxError(f"Unexpected token: {token.token_type}")

    def parse_function_call(self, callee):
        self.expect(TokenType.PARENTHESIS_OPEN)

        arguments = []
        if self.current.token_type != TokenType.PARENTHESIS_CLOSE:
            while True:
                arguments.append(self.parse_expression())

                if self.current.token_type != TokenType.COMMA:
                    break
                self.expect(TokenType.COMMA)

        self.expect(TokenType.PARENTHESIS_CLOSE)

        if isinstance(callee, balan_ast.AstVariable):
            if callee.name in balan_ast.BUILTIN_FUNCTION_OPCODES:
                return balan_ast.AstBuiltinCall(callee.name, arguments)

        return balan_ast.AstFunctionCall(callee, arguments)


with open(sys.argv[1], "r") as code_file:
    source = code_file.read()

tokens = lex(source)

print(tokens)

parser = Parser(tokens)
ast = parser.parse()

print(ast)

bytes_to_write = ast.generate()

print(bytes_to_write)

outfile_name = sys.argv[2]

#TODO: it seems we don't handle variable indexes good enough. We point to them on the same stack, but we can't know
#      the address beforehand. Will need to be assigned by the vm (which can be confusing, since we translate to an index during compliation,
#      but that index still needs to be mapped to stack position)

bb2_file = open(outfile_name, "wb")
for byte in bytes_to_write:
    bb2_file.write(byte.to_bytes(1, byteorder='big'))

print("written " + outfile_name)
