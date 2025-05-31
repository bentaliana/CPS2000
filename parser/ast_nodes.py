"""
Abstract Syntax Tree Node Definitions for PArL Language
Enhanced with beautiful tree-style printing by default
"""

from typing import List, Optional, Any, Union
from abc import ABC, abstractmethod


class ASTNode(ABC):
    """Base class for all AST nodes with visitor pattern support and beautiful tree printing"""
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
        """Beautiful tree-style string representation"""
        pass
    
    def _tree_children(self, children, indent_level=1):
        """Helper for indentation-based tree printing"""
        if not children:
            return ""
        
        indent = "  " * indent_level  # 2 spaces per level
        result = ""
        
        for child in children:
            if child is not None:
                # Add the child with proper indentation
                result += f"\n{indent}{child._get_node_label()}"
                
                # Add grandchildren with increased indentation
                grandchildren = child._get_children()
                if grandchildren:
                    result += child._tree_children(grandchildren, indent_level + 1)
        
        return result
    
    def _get_node_label(self):
        """Get the label for this node in the tree"""
        return str(self)
    
    def _get_children(self):
        """Get child nodes for tree printing - override in subclasses"""
        return []


# ===== PROGRAM STRUCTURE =====
class Program(ASTNode):
    """Root AST node representing entire program"""
    def __init__(self, statements: List[ASTNode], line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.statements = statements
    
    def __str__(self):
        result = "Program"
        result += self._tree_children(self.statements, indent_level=1)
        return result
    
    def _get_node_label(self):
        return "Program"
    
    def _get_children(self):
        return self.statements


class Block(ASTNode):
    """Block of statements enclosed in braces"""
    def __init__(self, statements: List[ASTNode], line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.statements = statements
    
    def __str__(self):
        result = "Block"
        result += self._tree_children(self.statements)
        return result
    
    def _get_node_label(self):
        return "Block"
    
    def _get_children(self):
        return self.statements


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
        result = f"VarDecl: {self.name} : {self.var_type}"
        if self.initializer:
            result += self._tree_children([self.initializer])
        return result
    
    def _get_node_label(self):
        return f"VarDecl: {self.name} : {self.var_type}"
    
    def _get_children(self):
        return [self.initializer] if self.initializer else []


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
        params_str = ", ".join(f"{p.name}:{p.param_type}" for p in self.params)
        result = f"FuncDecl: {self.name}({params_str}) -> {self.return_type}"
        
        # Show parameters as children if they exist, then body
        children = self.params + [self.body]
        result += self._tree_children(children)
        return result
    
    def _get_node_label(self):
        params_str = ", ".join(f"{p.name}:{p.param_type}" for p in self.params)
        return f"FuncDecl: {self.name}({params_str}) -> {self.return_type}"
    
    def _get_children(self):
        return self.params + [self.body]


class FormalParameter(ASTNode):
    """Function parameter with name and type"""
    def __init__(self, name: str, param_type: str, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.name = name
        self.param_type = param_type
    
    def __str__(self):
        return f"Param: {self.name} : {self.param_type}"
    
    def _get_node_label(self):
        return f"Param: {self.name} : {self.param_type}"
    
    def _get_children(self):
        return []


# ===== STATEMENTS =====
class Assignment(ASTNode):
    """Assignment statement: identifier = expression"""
    def __init__(self, target: ASTNode, value: ASTNode, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.target = target
        self.value = value
    
    def __str__(self):
        result = "Assignment"
        result += self._tree_children([self.target, self.value])
        return result
    
    def _get_node_label(self):
        return "Assignment"
    
    def _get_children(self):
        return [self.target, self.value]


class IfStatement(ASTNode):
    """If statement with optional else"""
    def __init__(self, condition: ASTNode, then_block: Block, 
                 else_block: Optional[Block] = None, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block
    
    def __str__(self):
        result = "If"
        children = [self.condition, self.then_block]
        if self.else_block:
            children.append(self.else_block)
        result += self._tree_children(children)
        return result
    
    def _get_node_label(self):
        return "If"
    
    def _get_children(self):
        children = [self.condition, self.then_block]
        if self.else_block:
            children.append(self.else_block)
        return children


class WhileStatement(ASTNode):
    """While loop statement"""
    def __init__(self, condition: ASTNode, body: Block, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.condition = condition
        self.body = body
    
    def __str__(self):
        result = "While"
        result += self._tree_children([self.condition, self.body])
        return result
    
    def _get_node_label(self):
        return "While"
    
    def _get_children(self):
        return [self.condition, self.body]


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
        result = "For"
        children = []
        if self.init:
            children.append(self.init)
        children.append(self.condition)
        if self.update:
            children.append(self.update)
        children.append(self.body)
        result += self._tree_children(children)
        return result
    
    def _get_node_label(self):
        return "For"
    
    def _get_children(self):
        children = []
        if self.init:
            children.append(self.init)
        children.append(self.condition)
        if self.update:
            children.append(self.update)
        children.append(self.body)
        return children


class ReturnStatement(ASTNode):
    """Return statement with expression"""
    def __init__(self, value: ASTNode, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.value = value
    
    def __str__(self):
        result = "Return"
        result += self._tree_children([self.value])
        return result
    
    def _get_node_label(self):
        return "Return"
    
    def _get_children(self):
        return [self.value]


# ===== BUILT-IN STATEMENTS =====
class PrintStatement(ASTNode):
    """__print statement"""
    def __init__(self, expression: ASTNode, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.expression = expression
    
    def __str__(self):
        result = "Print"
        result += self._tree_children([self.expression])
        return result
    
    def _get_node_label(self):
        return "Print"
    
    def _get_children(self):
        return [self.expression]


class DelayStatement(ASTNode):
    """__delay statement"""
    def __init__(self, expression: ASTNode, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.expression = expression
    
    def __str__(self):
        result = "Delay"
        result += self._tree_children([self.expression])
        return result
    
    def _get_node_label(self):
        return "Delay"
    
    def _get_children(self):
        return [self.expression]


class WriteStatement(ASTNode):
    """__write statement"""
    def __init__(self, x: ASTNode, y: ASTNode, color: ASTNode, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.x = x
        self.y = y
        self.color = color
    
    def __str__(self):
        result = "Write"
        result += self._tree_children([self.x, self.y, self.color])
        return result
    
    def _get_node_label(self):
        return "Write"
    
    def _get_children(self):
        return [self.x, self.y, self.color]


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
        result = "WriteBox"
        result += self._tree_children([self.x, self.y, self.width, self.height, self.color])
        return result
    
    def _get_node_label(self):
        return "WriteBox"
    
    def _get_children(self):
        return [self.x, self.y, self.width, self.height, self.color]


class ClearStatement(ASTNode):
    """__clear statement"""
    def __init__(self, color: ASTNode, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.color = color
    
    def __str__(self):
        result = "Clear"
        result += self._tree_children([self.color])
        return result
    
    def _get_node_label(self):
        return "Clear"
    
    def _get_children(self):
        return [self.color]


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
        result = f"BinaryOp: {self.operator}"
        result += self._tree_children([self.left, self.right])
        return result
    
    def _get_node_label(self):
        return f"BinaryOp: {self.operator}"
    
    def _get_children(self):
        return [self.left, self.right]


class UnaryOperation(ASTNode):
    """Unary operation expression"""
    def __init__(self, operator: str, operand: ASTNode, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.operator = operator
        self.operand = operand
    
    def __str__(self):
        result = f"UnaryOp: {self.operator}"
        result += self._tree_children([self.operand])
        return result
    
    def _get_node_label(self):
        return f"UnaryOp: {self.operator}"
    
    def _get_children(self):
        return [self.operand]


class CastExpression(ASTNode):
    """Type cast expression: expr as type"""
    def __init__(self, expression: ASTNode, target_type: str, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.expression = expression
        self.target_type = target_type

    def __str__(self):
        result = f"Cast -> {self.target_type}"
        result += self._tree_children([self.expression])
        return result
    
    def _get_node_label(self):
        return f"Cast -> {self.target_type}"
    
    def _get_children(self):
        return [self.expression]


class FunctionCall(ASTNode):
    """Function call expression"""
    def __init__(self, name: str, arguments: List[ASTNode], line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.name = name
        self.arguments = arguments
    
    def __str__(self):
        result = f"FuncCall: {self.name}"
        if self.arguments:
            result += self._tree_children(self.arguments)
        return result
    
    def _get_node_label(self):
        return f"FuncCall: {self.name}"
    
    def _get_children(self):
        return self.arguments


class IndexAccess(ASTNode):
    """Array/identifier index access (part of identifier per EBNF)"""
    def __init__(self, base: ASTNode, index: ASTNode, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.base = base
        self.index = index
    
    def __str__(self):
        result = "IndexAccess"
        result += self._tree_children([self.base, self.index])
        return result
    
    def _get_node_label(self):
        return "IndexAccess"
    
    def _get_children(self):
        return [self.base, self.index]


# ===== LITERALS AND IDENTIFIERS =====
class Literal(ASTNode):
    """Literal value (int, float, bool, colour)"""
    def __init__(self, value: Any, literal_type: str, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.value = value
        self.literal_type = literal_type
    
    def __str__(self):
        return f"Literal: {self.value} ({self.literal_type})"
    
    def _get_node_label(self):
        return f"Literal: {self.value} ({self.literal_type})"
    
    def _get_children(self):
        return []


class Identifier(ASTNode):
    """Variable identifier"""
    def __init__(self, name: str, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.name = name
    
    def __str__(self):
        return f"Identifier: {self.name}"
    
    def _get_node_label(self):
        return f"Identifier: {self.name}"
    
    def _get_children(self):
        return []


# ===== BUILT-IN EXPRESSIONS =====
class PadWidth(ASTNode):
    """__width built-in expression"""
    def __init__(self, line: int = 0, col: int = 0):
        super().__init__(line, col)
    
    def __str__(self):
        return "BuiltIn: __width"
    
    def _get_node_label(self):
        return "BuiltIn: __width"
    
    def _get_children(self):
        return []


class PadHeight(ASTNode):
    """__height built-in expression"""
    def __init__(self, line: int = 0, col: int = 0):
        super().__init__(line, col)
    
    def __str__(self):
        return "BuiltIn: __height"
    
    def _get_node_label(self):
        return "BuiltIn: __height"
    
    def _get_children(self):
        return []


class PadRead(ASTNode):
    """__read built-in expression"""
    def __init__(self, x: ASTNode, y: ASTNode, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.x = x
        self.y = y
    
    def __str__(self):
        result = "BuiltIn: __read"
        result += self._tree_children([self.x, self.y])
        return result
    
    def _get_node_label(self):
        return "BuiltIn: __read"
    
    def _get_children(self):
        return [self.x, self.y]


class PadRandI(ASTNode):
    """__randi built-in expression"""
    def __init__(self, max_val: ASTNode, line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.max_val = max_val
    
    def __str__(self):
        result = "BuiltIn: __randi"
        result += self._tree_children([self.max_val])
        return result
    
    def _get_node_label(self):
        return "BuiltIn: __randi"
    
    def _get_children(self):
        return [self.max_val]


# ===== ARRAY SUPPORT =====
class ArrayType:
    """Represents array type information"""
    def __init__(self, element_type: str, size: Optional[int] = None):
        self.element_type = element_type
        self.size = size  # None for dynamic arrays
        self.is_array = True
    
    def __str__(self):
        if self.size is not None:
            return f"{self.element_type}[{self.size}]"
        return f"{self.element_type}[]"
    
    def __eq__(self, other):
        if isinstance(other, str):
            return False  # Arrays are never equal to primitive types
        if not isinstance(other, ArrayType):
            return False
        return (self.element_type == other.element_type and 
                self.size == other.size)


class ArrayLiteral(ASTNode):
    """Array literal: [expr, expr, ...]"""
    def __init__(self, elements: List[ASTNode], line: int = 0, col: int = 0):
        super().__init__(line, col)
        self.elements = elements
    
    def __str__(self):
        result = f"ArrayLiteral: [{len(self.elements)} elements]"
        if self.elements:
            result += self._tree_children(self.elements)
        return result
    
    def _get_node_label(self):
        return f"ArrayLiteral: [{len(self.elements)} elements]"
    
    def _get_children(self):
        return self.elements


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
        '*': 3, '/': 3, '%': 3, 'and': 3
    }
    return precedence_map.get(operator, 0)

