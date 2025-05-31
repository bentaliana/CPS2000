"""
PArL Language Semantic Analyzer - SYSTEMATIC FIXES
Complete modulo support and enhanced type checking
"""

from typing import Dict, List, Optional, Set, Any, Union
from enum import Enum, auto
from parser.ast_nodes import *
from parser.parser_errors import ParserError


class SemanticErrorType(Enum):
    """Enumeration of semantic error types"""
    REDECLARATION = auto()
    UNDECLARED_VARIABLE = auto()
    UNDECLARED_FUNCTION = auto()
    TYPE_MISMATCH = auto()
    INVALID_ASSIGNMENT = auto()
    MISSING_RETURN = auto()
    INVALID_CAST = auto()
    ARGUMENT_COUNT_MISMATCH = auto()
    ARGUMENT_TYPE_MISMATCH = auto()
    INVALID_BUILTIN_ARGS = auto()


class SemanticError(Exception):
    """Semantic analysis error with detailed information"""
    def __init__(self, error_type: SemanticErrorType, message: str, 
                 node: ASTNode = None, line: int = 0, col: int = 0):
        self.error_type = error_type
        self.message = message
        self.node = node
        self.line = line if node is None else node.line
        self.col = col if node is None else node.col
        super().__init__(self.format_error())
    
    def format_error(self):
        return f"Semantic Error at line {self.line}, col {self.col}: {self.message}"


class Symbol:
    """Symbol table entry with type and scope information"""
    def __init__(self, name: str, symbol_type: Union[str, ArrayType], scope_level: int = 0, 
                 is_function: bool = False, is_parameter: bool = False):
        self.name = name
        self.symbol_type = symbol_type
        self.scope_level = scope_level
        self.is_function = is_function
        self.is_parameter = is_parameter
        self.is_initialized = False
        self.line_declared = 0
        self.col_declared = 0
        
        # For functions
        self.parameter_types: List[Union[str, ArrayType]] = []
        self.return_type: Union[str, ArrayType] = ""
    
    def __str__(self):
        if self.is_function:
            params = ", ".join(str(p) for p in self.parameter_types)
            return f"Function {self.name}({params}) -> {self.return_type}"
        else:
            return f"Variable {self.name}:{self.symbol_type}"

class SymbolTable:
    """Symbol table with scope management"""
    def __init__(self):
        self.scopes: List[Dict[str, Symbol]] = [{}]  # Stack of scopes
        self.current_scope_level = 0
        self.functions: Dict[str, Symbol] = {}  # Global function registry
        
        # Initialize built-in functions
        self._initialize_builtins()
    
    def _initialize_builtins(self):
        """Initialize built-in functions with their type signatures"""
        builtins = {
            "__print": (["int", "float", "bool", "colour"], "void"),
            "__delay": (["int"], "void"),
            "__write": (["int", "int", "colour"], "void"),
            "__write_box": (["int", "int", "int", "int", "colour"], "void"),
            "__clear": (["colour"], "void"),
            "__width": ([], "int"),
            "__height": ([], "int"),
            "__read": (["int", "int"], "colour"),
            "__randi": (["int"], "int"),
            "__random_int": (["int"], "int")  # Support both forms
        }
        
        for name, (param_types, return_type) in builtins.items():
            symbol = Symbol(name, return_type, 0, is_function=True)
            symbol.parameter_types = param_types
            symbol.return_type = return_type
            self.functions[name] = symbol
    
    def enter_scope(self):
        """Enter a new scope"""
        self.scopes.append({})
        self.current_scope_level += 1
    
    def exit_scope(self):
        """Exit current scope"""
        if len(self.scopes) > 1:
            self.scopes.pop()
            self.current_scope_level -= 1
    
    def declare_variable(self, name: str, var_type: str, node: ASTNode = None,
                        is_parameter: bool = False) -> Symbol:
        """Declare a variable in the current scope"""
        current_scope = self.scopes[-1]
        
        if name in current_scope:
            raise SemanticError(
                SemanticErrorType.REDECLARATION,
                f"Variable '{name}' already declared in current scope",
                node
            )
        
        symbol = Symbol(name, var_type, self.current_scope_level, 
                       is_parameter=is_parameter)
        if node:
            symbol.line_declared = node.line
            symbol.col_declared = node.col
        
        current_scope[name] = symbol
        return symbol
    
    def declare_function(self, name: str, return_type: str, 
                        param_types: List[str], node: ASTNode = None) -> Symbol:
        """Declare a function in the global scope"""
        if name in self.functions:
            raise SemanticError(
                SemanticErrorType.REDECLARATION,
                f"Function '{name}' already declared",
                node
            )
        
        symbol = Symbol(name, return_type, 0, is_function=True)
        symbol.parameter_types = param_types
        symbol.return_type = return_type
        if node:
            symbol.line_declared = node.line
            symbol.col_declared = node.col
        
        self.functions[name] = symbol
        return symbol
    
    def lookup_variable(self, name: str) -> Optional[Symbol]:
        """Look up a variable in current and enclosing scopes"""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None
    
    def lookup_function(self, name: str) -> Optional[Symbol]:
        """Look up a function"""
        return self.functions.get(name)


class TypeChecker:
    """Static type checking utilities with SYSTEMATIC MODULO SUPPORT"""
    
    VALID_TYPES = {"int", "float", "bool", "colour"}
    
    @staticmethod
    def is_valid_type(type_name: Union[str, ArrayType]) -> bool:
        """Check if a type is valid"""
        if isinstance(type_name, ArrayType):
            return TypeChecker.is_valid_type(type_name.element_type)
        return type_name in TypeChecker.VALID_TYPES
    
    @staticmethod
    def types_equal(type1: Union[str, ArrayType], type2: Union[str, ArrayType]) -> bool:
        """Check if two types are equal"""
        if isinstance(type1, ArrayType) and isinstance(type2, ArrayType):
            return (type1.element_type == type2.element_type and 
                    type1.size == type2.size)
        elif isinstance(type1, ArrayType) or isinstance(type2, ArrayType):
            return False
        else:
            return type1 == type2
    
    @staticmethod
    def can_cast(from_type: str, to_type: str) -> bool:
        """Check if a type can be cast to another type"""
        if from_type == to_type:
            return True
        
        # Define valid casts according to assignment spec
        valid_casts = {
            ("int", "float"): True,
            ("float", "int"): True,
            ("int", "bool"): True,
            ("bool", "int"): True,
            ("int", "colour"): True,
            ("colour", "int"): True,
        }
        
        return valid_casts.get((from_type, to_type), False)
    
    @staticmethod
    def get_binary_operation_result_type(left_type: str, operator: str, 
                                       right_type: str) -> Optional[str]:
        """Get the result type of a binary operation - SYSTEMATIC MODULO SUPPORT"""
        # Arithmetic operators including modulo
        if operator in ["+", "-", "*", "/", "%"]:
            if left_type == right_type and left_type in ["int", "float"]:
                return left_type
            return None
        
        # SYSTEMATIC FIX: Comparison operators ALWAYS return bool
        if operator in ["<", ">", "<=", ">=", "==", "!="]:
            # Check operands are compatible for comparison
            if left_type == right_type and left_type in ["int", "float", "bool", "colour"]:
                return "bool"  # ALWAYS return bool for comparisons
            return None
        
        # Logical operators require bool operands and return bool
        if operator in ["and", "or"]:
            if left_type == "bool" and right_type == "bool":
                return "bool"
            return None
        
        return None
    
    @staticmethod
    def get_unary_operation_result_type(operator: str, operand_type: str) -> Optional[str]:
        """Get the result type of a unary operation"""
        if operator == "-":
            if operand_type in ["int", "float"]:
                return operand_type
            return None
        
        if operator == "not":
            if operand_type == "bool":
                return "bool"
            return None
        
        return None


class SemanticAnalyzer:
    """
    Semantic analyzer implementing the visitor pattern
    Performs type checking, scope management, and semantic validation
    """
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors: List[SemanticError] = []
        self.current_function: Optional[Symbol] = None
        self.current_return_type: Optional[str] = None
        self.function_has_return = False
    
    def analyze(self, ast: Program) -> bool:
        """Main entry point for semantic analysis"""
        try:
            self.visit_program(ast)
            return len(self.errors) == 0
        except Exception as e:
            if not isinstance(e, SemanticError):
                error = SemanticError(
                    SemanticErrorType.TYPE_MISMATCH,
                    f"Internal semantic analysis error: {str(e)}"
                )
                self.errors.append(error)
            return False
    
    def visit_program(self, node: Program):
        """Visit program node - entry point"""
        # First pass: collect all function declarations
        for stmt in node.statements:
            if isinstance(stmt, FunctionDeclaration):
                self._declare_function(stmt)
        
        # Second pass: analyze function bodies and main program
        for stmt in node.statements:
            if isinstance(stmt, FunctionDeclaration):
                self.visit_function_declaration(stmt)
            else:
                self.visit_statement(stmt)
    
    def _declare_function(self, node: FunctionDeclaration):
        """Pre-declare function for forward references"""
        param_types = [param.param_type for param in node.params]
        
        # Validate parameter types
        for param in node.params:
            if not TypeChecker.is_valid_type(param.param_type):
                self._add_error(SemanticErrorType.TYPE_MISMATCH,
                              f"Invalid parameter type '{param.param_type}'", node)
        
        # Validate return type
        if not TypeChecker.is_valid_type(node.return_type):
            self._add_error(SemanticErrorType.TYPE_MISMATCH,
                          f"Invalid return type '{node.return_type}'", node)
        
        try:
            self.symbol_table.declare_function(node.name, node.return_type, 
                                             param_types, node)
        except SemanticError as e:
            self.errors.append(e)
    
    def visit_function_declaration(self, node: FunctionDeclaration):
        """Visit function declaration"""
        # Set current function context
        self.current_function = self.symbol_table.lookup_function(node.name)
        self.current_return_type = node.return_type
        self.function_has_return = False
        
        # Enter function scope
        self.symbol_table.enter_scope()
        
        # Declare parameters
        for param in node.params:
            try:
                symbol = self.symbol_table.declare_variable(
                    param.name, param.param_type, param, is_parameter=True
                )
                symbol.is_initialized = True  # Parameters are always initialized
            except SemanticError as e:
                self.errors.append(e)
        
        # Analyze function body
        self.visit_block(node.body)
        
        # Check return statement requirements
        if node.return_type != "void" and not self.function_has_return:
            self._add_error(SemanticErrorType.MISSING_RETURN,
                          f"Function '{node.name}' must return a value of type '{node.return_type}'", 
                          node)
        
        # Exit function scope
        self.symbol_table.exit_scope()
        self.current_function = None
        self.current_return_type = None
    
    def visit_block(self, node: Block):
        """Visit block statement"""
        self.symbol_table.enter_scope()
        
        for stmt in node.statements:
            self.visit_statement(stmt)
        
        self.symbol_table.exit_scope()
    
    def visit_statement(self, node: ASTNode):
        """Dispatch statement visits"""
        if isinstance(node, VariableDeclaration):
            self.visit_variable_declaration(node)
        elif isinstance(node, Assignment):
            self.visit_assignment(node)
        elif isinstance(node, IfStatement):
            self.visit_if_statement(node)
        elif isinstance(node, WhileStatement):
            self.visit_while_statement(node)
        elif isinstance(node, ForStatement):
            self.visit_for_statement(node)
        elif isinstance(node, ReturnStatement):
            self.visit_return_statement(node)
        elif isinstance(node, PrintStatement):
            self.visit_print_statement(node)
        elif isinstance(node, DelayStatement):
            self.visit_delay_statement(node)
        elif isinstance(node, WriteStatement):
            self.visit_write_statement(node)
        elif isinstance(node, WriteBoxStatement):
            self.visit_write_box_statement(node)
        elif isinstance(node, ClearStatement):
            self.visit_clear_statement(node)
        elif isinstance(node, Block):
            self.visit_block(node)
        elif isinstance(node, FunctionCall):
            self.visit_function_call(node)
        else:
            self._add_error(SemanticErrorType.TYPE_MISMATCH,
                          f"Unknown statement type: {type(node).__name__}", node)
    
    def visit_variable_declaration(self, node: VariableDeclaration):
        """Visit variable declaration with array support"""
        var_type = node.var_type
        
        # Validate type
        if not TypeChecker.is_valid_type(var_type):
            if isinstance(var_type, ArrayType):
                self._add_error(SemanticErrorType.TYPE_MISMATCH,
                            f"Invalid array element type '{var_type.element_type}'", node)
            else:
                self._add_error(SemanticErrorType.TYPE_MISMATCH,
                            f"Invalid variable type '{var_type}'", node)
            return
        
        # Validate array constraints
        if isinstance(var_type, ArrayType):
            if var_type.size is not None and var_type.size <= 0:
                self._add_error(SemanticErrorType.TYPE_MISMATCH,
                            f"Array size must be positive, got {var_type.size}", node)
                return
        
        # Check for conflict with function parameters
        if self.current_function:
            for scope in self.symbol_table.scopes:
                if node.name in scope and scope[node.name].is_parameter:
                    self._add_error(SemanticErrorType.REDECLARATION,
                                f"Variable '{node.name}' conflicts with function parameter", node)
                    return
        
        # Check initializer if present
        if node.initializer:
            if isinstance(node.initializer, ArrayLiteral):
                # Array literal initialization
                if not isinstance(var_type, ArrayType):
                    self._add_error(SemanticErrorType.TYPE_MISMATCH,
                                f"Cannot initialize non-array variable '{node.name}' with array literal", node)
                    return
                
                # Check element types
                for i, elem in enumerate(node.initializer.elements):
                    elem_type = self.visit_expression(elem)
                    if elem_type and elem_type != var_type.element_type:
                        self._add_error(SemanticErrorType.TYPE_MISMATCH,
                                    f"Array element {i} type mismatch: expected '{var_type.element_type}', got '{elem_type}'", elem)
                
                # Check size constraints
                actual_size = len(node.initializer.elements)
                if var_type.size is not None and actual_size != var_type.size:
                    self._add_error(SemanticErrorType.TYPE_MISMATCH,
                                f"Array size mismatch: declared {var_type.size}, initialized with {actual_size} elements", node)
                
                # Update dynamic array size
                if var_type.size is None:
                    var_type.size = actual_size
            else:
                # Regular expression initialization
                init_type = self.visit_expression(node.initializer)
                if isinstance(var_type, ArrayType):
                    self._add_error(SemanticErrorType.TYPE_MISMATCH,
                                f"Cannot initialize array variable '{node.name}' with scalar expression", node)
                elif init_type and not TypeChecker.types_equal(init_type, var_type):
                    self._add_error(SemanticErrorType.TYPE_MISMATCH,
                                f"Cannot initialize variable '{node.name}' of type '{var_type}' with expression of type '{init_type}'", node)
        
        # Declare variable
        try:
            symbol = self.symbol_table.declare_variable(node.name, var_type, node)
            if node.initializer:
                symbol.is_initialized = True
        except SemanticError as e:
            self.errors.append(e)
    
    def visit_assignment(self, node: Assignment):
        """Visit assignment statement with array support"""
        if isinstance(node.target, Identifier):
            # Simple variable assignment
            var_symbol = self.symbol_table.lookup_variable(node.target.name)
            if not var_symbol:
                self._add_error(SemanticErrorType.UNDECLARED_VARIABLE,
                            f"Undeclared variable '{node.target.name}'", node.target)
                return
            
            target_type = var_symbol.symbol_type
            
            if isinstance(target_type, ArrayType):
                self._add_error(SemanticErrorType.INVALID_ASSIGNMENT,
                            f"Cannot assign to entire array '{node.target.name}'. Use array indexing for element assignment.", node)
                return
            
            value_type = self.visit_expression(node.value)
            if value_type and not TypeChecker.types_equal(target_type, value_type):
                self._add_error(SemanticErrorType.TYPE_MISMATCH,
                            f"Cannot assign expression of type '{value_type}' to variable of type '{target_type}'", node)
            
            var_symbol.is_initialized = True
                
        elif isinstance(node.target, IndexAccess):
            # Array element assignment
            if isinstance(node.target.base, Identifier):
                var_symbol = self.symbol_table.lookup_variable(node.target.base.name)
                if not var_symbol:
                    self._add_error(SemanticErrorType.UNDECLARED_VARIABLE,
                                f"Undeclared variable '{node.target.base.name}'", node.target.base)
                    return
                
                if not isinstance(var_symbol.symbol_type, ArrayType):
                    self._add_error(SemanticErrorType.TYPE_MISMATCH,
                                f"Cannot index non-array variable '{node.target.base.name}'", node.target)
                    return
                
                # Check index type
                index_type = self.visit_expression(node.target.index)
                if index_type and index_type != "int":
                    self._add_error(SemanticErrorType.TYPE_MISMATCH,
                                f"Array index must be int, got '{index_type}'", node.target.index)
                
                # Check value type
                value_type = self.visit_expression(node.value)
                expected_type = var_symbol.symbol_type.element_type
                if value_type and value_type != expected_type:
                    self._add_error(SemanticErrorType.TYPE_MISMATCH,
                                f"Cannot assign '{value_type}' to array element of type '{expected_type}'", node)
            else:
                self._add_error(SemanticErrorType.INVALID_ASSIGNMENT,
                            "Complex array assignment not supported", node.target)
        else:
            self._add_error(SemanticErrorType.INVALID_ASSIGNMENT,
                        "Invalid assignment target", node.target)
    
    def visit_if_statement(self, node: IfStatement):
        """Visit if statement"""
        # Check condition
        condition_type = self.visit_expression(node.condition)
        if condition_type and condition_type != "bool":
            self._add_error(SemanticErrorType.TYPE_MISMATCH,
                          f"If condition must be boolean, got '{condition_type}'", 
                          node.condition)
        
        # Visit branches
        self.visit_block(node.then_block)
        if node.else_block:
            self.visit_block(node.else_block)
    
    def visit_while_statement(self, node: WhileStatement):
        """Visit while statement"""
        # Check condition
        condition_type = self.visit_expression(node.condition)
        if condition_type and condition_type != "bool":
            self._add_error(SemanticErrorType.TYPE_MISMATCH,
                          f"While condition must be boolean, got '{condition_type}'", 
                          node.condition)
        
        # Visit body
        self.visit_block(node.body)
    
    def visit_for_statement(self, node: ForStatement):
        """Visit for statement"""
        self.symbol_table.enter_scope()
        
        # Visit initialization
        if node.init:
            self.visit_variable_declaration(node.init)
        
        # Check condition
        condition_type = self.visit_expression(node.condition)
        if condition_type and condition_type != "bool":
            self._add_error(SemanticErrorType.TYPE_MISMATCH,
                          f"For condition must be boolean, got '{condition_type}'", 
                          node.condition)
        
        # Visit update
        if node.update:
            self.visit_assignment(node.update)
        
        # Visit body
        self.visit_block(node.body)
        
        self.symbol_table.exit_scope()
    
    def visit_return_statement(self, node: ReturnStatement):
        """Visit return statement"""
        if not self.current_function:
            self._add_error(SemanticErrorType.MISSING_RETURN,
                          "Return statement outside function", node)
            return
        
        return_value_type = self.visit_expression(node.value)
        expected_type = self.current_return_type
        
        if return_value_type and expected_type and return_value_type != expected_type:
            self._add_error(SemanticErrorType.TYPE_MISMATCH,
                          f"Function must return '{expected_type}', got '{return_value_type}'", 
                          node)
        
        self.function_has_return = True
    
    def visit_print_statement(self, node: PrintStatement):
        """Visit print statement"""
        expr_type = self.visit_expression(node.expression)
        if expr_type and expr_type not in ["int", "float", "bool", "colour"]:
            self._add_error(SemanticErrorType.INVALID_BUILTIN_ARGS,
                          f"__print expects printable type, got '{expr_type}'", node)
    
    def visit_delay_statement(self, node: DelayStatement):
        """Visit delay statement"""
        expr_type = self.visit_expression(node.expression)
        if expr_type and expr_type != "int":
            self._add_error(SemanticErrorType.INVALID_BUILTIN_ARGS,
                          f"__delay expects int, got '{expr_type}'", node)
    
    def visit_write_statement(self, node: WriteStatement):
        """Visit write statement"""
        x_type = self.visit_expression(node.x)
        y_type = self.visit_expression(node.y)
        color_type = self.visit_expression(node.color)
        
        if x_type and x_type != "int":
            self._add_error(SemanticErrorType.INVALID_BUILTIN_ARGS,
                          f"__write x coordinate must be int, got '{x_type}'", node)
        if y_type and y_type != "int":
            self._add_error(SemanticErrorType.INVALID_BUILTIN_ARGS,
                          f"__write y coordinate must be int, got '{y_type}'", node)
        if color_type and color_type != "colour":
            self._add_error(SemanticErrorType.INVALID_BUILTIN_ARGS,
                          f"__write color must be colour, got '{color_type}'", node)
    
    def visit_write_box_statement(self, node: WriteBoxStatement):
        """Visit write_box statement"""
        x_type = self.visit_expression(node.x)
        y_type = self.visit_expression(node.y)
        width_type = self.visit_expression(node.width)
        height_type = self.visit_expression(node.height)
        color_type = self.visit_expression(node.color)
        
        expected_int_args = [
            (x_type, "x coordinate"),
            (y_type, "y coordinate"),
            (width_type, "width"),
            (height_type, "height")
        ]
        
        for arg_type, arg_name in expected_int_args:
            if arg_type and arg_type != "int":
                self._add_error(SemanticErrorType.INVALID_BUILTIN_ARGS,
                              f"__write_box {arg_name} must be int, got '{arg_type}'", node)
        
        if color_type and color_type != "colour":
            self._add_error(SemanticErrorType.INVALID_BUILTIN_ARGS,
                          f"__write_box color must be colour, got '{color_type}'", node)
    
    def visit_clear_statement(self, node: ClearStatement):
        """Visit clear statement"""
        color_type = self.visit_expression(node.color)
        if color_type and color_type != "colour":
            self._add_error(SemanticErrorType.INVALID_BUILTIN_ARGS,
                          f"__clear expects colour, got '{color_type}'", node)
    
    def visit_expression(self, node: ASTNode) -> Optional[Union[str, ArrayType]]:
        """Visit expression and return its type"""
        if isinstance(node, BinaryOperation):
            return self.visit_binary_operation(node)
        elif isinstance(node, UnaryOperation):
            return self.visit_unary_operation(node)
        elif isinstance(node, CastExpression):
            return self.visit_cast_expression(node)
        elif isinstance(node, FunctionCall):
            return self.visit_function_call(node)
        elif isinstance(node, ArrayLiteral):
            return self.visit_array_literal(node)
        elif isinstance(node, IndexAccess):
            return self.visit_index_access(node)
        elif isinstance(node, Literal):
            return self.visit_literal(node)
        elif isinstance(node, Identifier):
            return self.visit_identifier(node)
        elif isinstance(node, PadWidth):
            return "int"
        elif isinstance(node, PadHeight):
            return "int"
        elif isinstance(node, PadRead):
            return self.visit_pad_read(node)
        elif isinstance(node, PadRandI):
            return self.visit_pad_rand_i(node)
        else:
            self._add_error(SemanticErrorType.TYPE_MISMATCH,
                        f"Unknown expression type: {type(node).__name__}", node)
            return None
        
    def visit_binary_operation(self, node: BinaryOperation) -> Optional[str]:
        """
        Visit binary operation - SYSTEMATIC MODULO SUPPORT
        """
        left_type = self.visit_expression(node.left)
        right_type = self.visit_expression(node.right)

        # Both operands must have valid types to proceed
        if not left_type or not right_type:
            return None

        result_type = TypeChecker.get_binary_operation_result_type(
            left_type, node.operator, right_type
        )

        if not result_type:
            # SYSTEMATIC FIX: Include modulo in error message
            operator_categories = {
                'arithmetic': ['+', '-', '*', '/', '%'],
                'comparison': ['<', '>', '<=', '>=', '==', '!='],
                'logical': ['and', 'or']
            }
            
            category = "unknown"
            for cat, ops in operator_categories.items():
                if node.operator in ops:
                    category = cat
                    break
            
            self._add_error(SemanticErrorType.TYPE_MISMATCH,
                            f"Invalid {category} operation: '{left_type}' {node.operator} '{right_type}'. "
                            f"Operands must have matching types.", 
                            node)
            return None

        return result_type
    
    def visit_unary_operation(self, node: UnaryOperation) -> Optional[str]:
        """Visit unary operation"""
        operand_type = self.visit_expression(node.operand)
        
        if not operand_type:
            return None
        
        result_type = TypeChecker.get_unary_operation_result_type(
            node.operator, operand_type
        )
        
        if not result_type:
            self._add_error(SemanticErrorType.TYPE_MISMATCH,
                          f"Invalid unary operation: {node.operator} '{operand_type}'", 
                          node)
            return None
        
        return result_type
    
    def visit_cast_expression(self, node: CastExpression) -> Optional[str]:
        """Visit cast expression"""
        expr_type = self.visit_expression(node.expression)
        target_type = node.target_type

        if expr_type is None:
            return None

        # Check if cast is allowed
        if not TypeChecker.can_cast(expr_type, target_type):
            self._add_error(SemanticErrorType.TYPE_MISMATCH,
                            f"Cannot cast from '{expr_type}' to '{target_type}'",
                            node)
            return None

        return target_type
    
    def visit_function_call(self, node: FunctionCall) -> Optional[str]:
        """Visit function call"""
        func_symbol = self.symbol_table.lookup_function(node.name)
        
        if not func_symbol:
            self._add_error(SemanticErrorType.UNDECLARED_FUNCTION,
                          f"Undeclared function '{node.name}'", node)
            return None
        
        # Check argument count
        expected_count = len(func_symbol.parameter_types)
        actual_count = len(node.arguments)
        
        if actual_count != expected_count:
            self._add_error(SemanticErrorType.ARGUMENT_COUNT_MISMATCH,
                          f"Function '{node.name}' expects {expected_count} arguments, "
                          f"got {actual_count}", node)
            return func_symbol.return_type
        
        # Check argument types
        for i, (arg, expected_type) in enumerate(zip(node.arguments, func_symbol.parameter_types)):
            actual_type = self.visit_expression(arg)
            if actual_type and actual_type != expected_type:
                self._add_error(SemanticErrorType.ARGUMENT_TYPE_MISMATCH,
                              f"Argument {i+1} to function '{node.name}' expects '{expected_type}', "
                              f"got '{actual_type}'", arg)
        
        return func_symbol.return_type
    
    def visit_literal(self, node: Literal) -> str:
        """Visit literal"""
        return node.literal_type
    
    def visit_identifier(self, node: Identifier) -> Optional[str]:
        """Visit identifier"""
        symbol = self.symbol_table.lookup_variable(node.name)
        
        if not symbol:
            self._add_error(SemanticErrorType.UNDECLARED_VARIABLE,
                          f"Undeclared variable '{node.name}'", node)
            return None
        
        return symbol.symbol_type
    
    def visit_pad_read(self, node: PadRead) -> Optional[str]:
        """Visit __read built-in"""
        x_type = self.visit_expression(node.x)
        y_type = self.visit_expression(node.y)
        
        if x_type and x_type != "int":
            self._add_error(SemanticErrorType.INVALID_BUILTIN_ARGS,
                          f"__read x coordinate must be int, got '{x_type}'", node)
        if y_type and y_type != "int":
            self._add_error(SemanticErrorType.INVALID_BUILTIN_ARGS,
                          f"__read y coordinate must be int, got '{y_type}'", node)
        
        return "colour"
    
    def visit_pad_rand_i(self, node: PadRandI) -> Optional[str]:
        """Visit __randi built-in"""
        max_type = self.visit_expression(node.max_val)
        
        if max_type and max_type != "int":
            self._add_error(SemanticErrorType.INVALID_BUILTIN_ARGS,
                          f"__randi max value must be int, got '{max_type}'", node)
        
        return "int"
    
    def visit_array_literal(self, node: ArrayLiteral) -> Optional[ArrayType]:
        """Visit array literal"""
        if not node.elements:
            self._add_error(SemanticErrorType.TYPE_MISMATCH,
                        "Empty array literals not allowed", node)
            return None
        
        # Determine element type from first element
        first_type = self.visit_expression(node.elements[0])
        if not first_type:
            return None
        
        # Check all elements have same type
        for i, elem in enumerate(node.elements[1:], 1):
            elem_type = self.visit_expression(elem)
            if elem_type and not TypeChecker.types_equal(elem_type, first_type):
                self._add_error(SemanticErrorType.TYPE_MISMATCH,
                            f"Array element {i} type mismatch: expected '{first_type}', got '{elem_type}'", elem)
        
        return ArrayType(first_type, len(node.elements))

    def visit_index_access(self, node: IndexAccess) -> Optional[str]:
        """Visit array index access"""
        if isinstance(node.base, Identifier):
            var_symbol = self.symbol_table.lookup_variable(node.base.name)
            if not var_symbol:
                self._add_error(SemanticErrorType.UNDECLARED_VARIABLE,
                            f"Undeclared variable '{node.base.name}'", node.base)
                return None
            
            if not isinstance(var_symbol.symbol_type, ArrayType):
                self._add_error(SemanticErrorType.TYPE_MISMATCH,
                            f"Cannot index non-array variable '{node.base.name}'", node)
                return None
            
            # Check index type
            index_type = self.visit_expression(node.index)
            if index_type and index_type != "int":
                self._add_error(SemanticErrorType.TYPE_MISMATCH,
                            f"Array index must be int, got '{index_type}'", node.index)
            
            return var_symbol.symbol_type.element_type
        else:
            self._add_error(SemanticErrorType.TYPE_MISMATCH,
                        "Complex array access not supported", node)
            return None

    def _add_error(self, error_type: SemanticErrorType, message: str, node: ASTNode = None):
        """Add a semantic error to the error list"""
        error = SemanticError(error_type, message, node)
        self.errors.append(error)
    
    def report_errors(self) -> bool:
        """Report all semantic errors"""
        if self.errors:
            print(f"Semantic Analysis Failed: {len(self.errors)} error(s) found")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
            return False
        return True
    
    def has_errors(self) -> bool:
        """Check if analyzer has encountered errors"""
        return len(self.errors) > 0
    
    def clear_errors(self):
        """Clear all accumulated errors"""
        self.errors.clear()