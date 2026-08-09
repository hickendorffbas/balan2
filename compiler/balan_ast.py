from dataclasses import dataclass
from enum import Enum


class ASTBalanDataType(Enum):
    INT = 1
    STRING = 2


TYPE_KEYWORDS_MAPPING = {
    "int": ASTBalanDataType.INT,
    "string": ASTBalanDataType.STRING,
}


OPCODE_PUSH = 2
OPCODE_ADD = 3
OPCODE_STORE = 4
OPCODE_LOAD = 5


BUILTIN_FUNCTION_OPCODES = {
    "print": 1,
}
BUILTIN_FUNCTIONS_NUMBER_OF_ARGS = {
    "print": 1,
}


VARS = {} #TODO: these are local vars, but I don't have functions yet, will need to be done differently in the future
NEXT_VAR_IDX = 0


@dataclass
class AstProgram:
    statements: list

    def generate(self):
        bytecode = []
        for statement in self.statements:
            bytecode.extend(statement.generate())
        return bytecode


@dataclass
class AstAssign:
    name: str
    value: object


@dataclass
class AstExprStmt:
    expr: object

    def generate(self):
        return self.expr.generate()


@dataclass
class AstNumber:
    value: int

    def generate(self):
        return [OPCODE_PUSH, self.value]


@dataclass
class AstVariable:
    name: str

    def generate(self):
        return [OPCODE_LOAD, VARS[self.name]]


@dataclass
class AstDeclaration:
    name: str
    type: ASTBalanDataType
    initializer: AstExprStmt

    def generate(self):
        if self.initializer is None:
            return []  #TODO: I think we don't need to generate in this case. We do need this node for type information
                       #      but that should probably be a different pass

        global NEXT_VAR_IDX
        new_var_idx = NEXT_VAR_IDX
        NEXT_VAR_IDX += 1
        VARS[self.name] = new_var_idx #TODO: We need a check (and error) that this var does not yet exist
        return self.initializer.generate() + [OPCODE_STORE, new_var_idx]


@dataclass
class AstUnaryOp:
    op: str
    operand: object


@dataclass
class AstBinaryOp:
    left: object
    op: str
    right: object

    def generate(self):
        left_code = self.left.generate()
        right_code = self.right.generate()

        if self.op == "+":
            binop_opcode = OPCODE_ADD
        else:
            raise Exception(f"operation not implemented for {self.op}")

        return left_code + right_code + [binop_opcode]


@dataclass
class AstFunctionCall:
    callee: object
    arguments: list


@dataclass
class AstBuiltinCall:
    function_name: str
    arguments: list

    def generate(self):
        expected_number_of_args = BUILTIN_FUNCTIONS_NUMBER_OF_ARGS[self.function_name]
        if len(self.arguments) != expected_number_of_args:
            raise Exception("Invalid number of args supplied to builtin function")

        code = []
        for arg in self.arguments:
            code = code + arg.generate()

        return code + [BUILTIN_FUNCTION_OPCODES[self.function_name]]
