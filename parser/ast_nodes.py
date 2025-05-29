"""
Abstract Syntax Tree Node Definitions for PArL Language
REFACTORED with __str__ methods for perfect printing
"""

from typing import List, Optional, Any, Union
from abc import ABC, abstractmethod


class ASTNode(ABC):
    """Base class for all AST nodes with visitor pattern support and elegant printing"""
    def __init__(self, line: int = 0, col: int = 0):
        self.line = line
        self.col = col
    
    def accept(self, visitor):
        """Visitor pattern implementation for semantic analysis/code generation"""
        method_name = f"visit_{self.__class__.__name__.lower()}"
        if hasattr(visitor, method_name):
            return getattr(visitor, method_name)(self)
        return visitor.generic_visit(self)
    
    @abstractmethod
    def __str__(self):
        """Clean string representation for Task 2 printing"""
        pass
    
    def _indent_children(self, children, level=1):
        """Helper for beautiful indented child printing"""
        result = ""
        indent = "  " * level
        for child in children:
            if child is not None:
                child_str = str(child)
                for line in child_str.split('\n'):
                    if line.strip():
                        result += f"\n{indent}{line}"
        return result
    
    def _format_single_child(self, child, level=1):
        """Helper for single child formatting"""
        if child is None:
            return ""
        indent = "  " * level
        child_str = str(child)
        return f"\n{indent}{child_str}"


# ===== PROGRAM STRUCTURE =====
class Program(ASTNode):
    """Root AST node representing entire program"""
    def __init__(self, statements: List[ASTNode], line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.statements = statements
    
    def __str__(self):
        result = "Program"
        result += self._indent_children(self.statements)
        return result


class Block(ASTNode):
    """Block of statements enclosed in braces"""
    def __init__(self, statements: List[ASTNode], line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.statements = statements
    
    def __str__(self):
        result = "Block"
        result += self._indent_children(self.statements)
        return result


# ===== DECLARATIONS =====
class VariableDeclaration(ASTNode):
    """Variable declaration: let name:type = expr"""
    def __init__(self, name: str, var_type: str, initializer: Optional[ASTNode] = None,
                 line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.name = name
        self.var_type = var_type
        self.initializer = initializer
    
    def __str__(self):
        result = f"VarDecl: {self.name}:{self.var_type}"
        if self.initializer:
            result += f" = {self.initializer}"
        return result


class FunctionDeclaration(ASTNode):
    """Function declaration with parameters and body"""
    def __init__(self, name: str, params: List['FormalParameter'], 
                 return_type: str, body: Block, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body
    
    def __str__(self):
        params_str = ", ".join(str(p) for p in self.params)
        result = f"FunctionDecl: {self.name}({params_str}) -> {self.return_type}"
        result += self._format_single_child(self.body)
        return result


class FormalParameter(ASTNode):
    """Function parameter with name and type"""
    def __init__(self, name: str, param_type: str, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.name = name
        self.param_type = param_type
    
    def __str__(self):
        return f"{self.name}:{self.param_type}"


# ===== STATEMENTS =====
class Assignment(ASTNode):
    """Assignment statement: identifier = expression"""
    def __init__(self, target: ASTNode, value: ASTNode, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.target = target  # Can be Identifier or IndexAccess
        self.value = value
    
    def __str__(self):
        return f"Assignment: {self.target} = {self.value}"


class IfStatement(ASTNode):
    """If statement with optional else"""
    def __init__(self, condition: ASTNode, then_block: Block, 
                 else_block: Optional[Block] = None, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block
    
    def __str__(self):
        result = f"If: {self.condition}"
        result += f"\n  Then:{self._format_single_child(self.then_block)}"
        if self.else_block:
            result += f"\n  Else:{self._format_single_child(self.else_block)}"
        return result


class WhileStatement(ASTNode):
    """While loop statement"""
    def __init__(self, condition: ASTNode, body: Block, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.condition = condition
        self.body = body
    
    def __str__(self):
        result = f"While: {self.condition}"
        result += self._format_single_child(self.body)
        return result


class ForStatement(ASTNode):
    """For loop statement"""
    def __init__(self, init: Optional[ASTNode], condition: ASTNode, 
                 update: Optional[ASTNode], body: Block, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body
    
    def __str__(self):
        init_str = str(self.init) if self.init else "none"
        update_str = str(self.update) if self.update else "none"
        result = f"For: init=({init_str}), condition=({self.condition}), update=({update_str})"
        result += self._format_single_child(self.body)
        return result


class ReturnStatement(ASTNode):
    """Return statement with expression"""
    def __init__(self, value: ASTNode, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.value = value
    
    def __str__(self):
        return f"Return: {self.value}"


# ===== BUILT-IN STATEMENTS =====
class PrintStatement(ASTNode):
    """__print statement"""
    def __init__(self, expression: ASTNode, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.expression = expression
    
    def __str__(self):
        return f"Print: {self.expression}"


class DelayStatement(ASTNode):
    """__delay statement"""
    def __init__(self, expression: ASTNode, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.expression = expression
    
    def __str__(self):
        return f"Delay: {self.expression}"


class WriteStatement(ASTNode):
    """__write statement"""
    def __init__(self, x: ASTNode, y: ASTNode, color: ASTNode, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.x = x
        self.y = y
        self.color = color
    
    def __str__(self):
        return f"Write: ({self.x}, {self.y}, {self.color})"


class WriteBoxStatement(ASTNode):
    """__write_box statement"""
    def __init__(self, x: ASTNode, y: ASTNode, width: ASTNode, 
                 height: ASTNode, color: ASTNode, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
    
    def __str__(self):
        return f"WriteBox: ({self.x}, {self.y}, {self.width}x{self.height}, {self.color})"


class ClearStatement(ASTNode):
    """__clear statement"""
    def __init__(self, color: ASTNode, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.color = color
    
    def __str__(self):
        return f"Clear: {self.color}"


# ===== EXPRESSIONS =====
class BinaryOperation(ASTNode):
    """Binary operation expression"""
    def __init__(self, left: ASTNode, operator: str, right: ASTNode,
                 line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.left = left
        self.operator = operator
        self.right = right
    
    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"


class UnaryOperation(ASTNode):
    """Unary operation expression"""
    def __init__(self, operator: str, operand: ASTNode, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.operator = operator
        self.operand = operand
    
    def __str__(self):
        return f"({self.operator} {self.operand})"


class CastExpression(ASTNode):
    """Type cast expression: expr as type"""
    def __init__(self, expression: ASTNode, target_type: str, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.expression = expression
        self.target_type = target_type

    def __str__(self):
        return f"Cast({self.expression} as {self.target_type})"


class FunctionCall(ASTNode):
    """Function call expression"""
    def __init__(self, name: str, arguments: List[ASTNode], line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.name = name
        self.arguments = arguments
    
    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self.arguments)
        return f"{self.name}({args_str})"


class IndexAccess(ASTNode):
    """Array/identifier index access (part of identifier per EBNF)"""
    def __init__(self, base: ASTNode, index: ASTNode, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.base = base
        self.index = index
    
    def __str__(self):
        return f"{self.base}[{self.index}]"


# ===== LITERALS AND IDENTIFIERS =====
class Literal(ASTNode):
    """Literal value (int, float, bool, colour)"""
    def __init__(self, value: Any, literal_type: str, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.value = value
        self.literal_type = literal_type
    
    def __str__(self):
        return f"{self.value}:{self.literal_type}"


class Identifier(ASTNode):
    """Variable identifier"""
    def __init__(self, name: str, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.name = name
    
    def __str__(self):
        return self.name


# ===== BUILT-IN EXPRESSIONS =====
class PadWidth(ASTNode):
    """__width built-in expression"""
    def __init__(self, line: int = 0, col: int = 0):
        super().__init__(line, col)
    
    def __str__(self):
        return "__width"


class PadHeight(ASTNode):
    """__height built-in expression"""
    def __init__(self, line: int = 0, col: int = 0):
        super().__init__(line, col)
    
    def __str__(self):
        return "__height"


class PadRead(ASTNode):
    """__read built-in expression"""
    def __init__(self, x: ASTNode, y: ASTNode, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"__read({self.x}, {self.y})"


class PadRandI(ASTNode):
    """__randi built-in expression"""
    def __init__(self, max_val: ASTNode, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.max_val = max_val
    
    def __str__(self):
        return f"__randi({self.max_val})"


# ===== UTILITY FUNCTIONS =====
def create_literal_from_token(token) -> Literal:
    """Helper function to create appropriate literal from token"""
    from lexer import TokenType
    
    if token.type == TokenType.INT_LITERAL:
        return Literal(int(token.lexeme), "int", token.line, token.col)
    elif token.type == TokenType.FLOAT_LITERAL:
        return Literal(float(token.lexeme), "float", token.line, token.col)
    elif token.type == TokenType.COLOUR_LITERAL:
        return Literal(token.lexeme, "colour", token.line, token.col)
    elif token.type == TokenType.TRUE:
        return Literal(True, "bool", token.line, token.col)
    elif token.type == TokenType.FALSE:
        return Literal(False, "bool", token.line, token.col)
    else:
        raise ValueError(f"Invalid literal token: {token}")


def get_operator_precedence(operator: str) -> int:
    """Get operator precedence for proper parsing"""
    precedence_map = {
        # Relational operators (lowest precedence in expression parsing)
        '==': 1, '!=': 1, '<': 1, '>': 1, '<=': 1, '>=': 1,
        # Additive operators
        '+': 2, '-': 2, 'or': 2,
        # Multiplicative operators (highest precedence)
        '*': 3, '/': 3, 'and': 3
    }
    return precedence_map.get(operator, 0)
