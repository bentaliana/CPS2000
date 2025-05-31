"""
PArL Language Parser - Task 2 Implementation
Hand-crafted recursive descent LL(k) parser following assignment EBNF
"""

from typing import List, Optional, Union
from lexer import Token, TokenType, FSALexer
from .token_stream import TokenStream
from .ast_nodes import *
from .parser_errors import *


class PArLParser:
    """
    Recursive descent parser for PArL language
    Implements hand-crafted top-down LL(k) parsing as specified in assignment
    """
    
    def __init__(self, tokens: List[Token] = None, lexer: FSALexer = None):
        """
        Initialize parser with either token list or lexer (supporting both approaches)
        """
        if tokens is not None:
            # Token list approach
            self.stream = TokenStream(tokens)
            self.lexer = None
        elif lexer is not None:
            # GetNextToken approach (alternative mentioned in assignment)
            self.lexer = lexer
            self.stream = None
            raise NotImplementedError("GetNextToken approach not implemented in this version")
        else:
            raise ValueError("Must provide either tokens list or lexer")
        
        self.errors = []
        self.debug = False
    
    # ===== MAIN PARSING ENTRY POINT =====
    
    def parse(self) -> Program:
        """Main entry point for parsing"""
        try:
            return self.parse_program()
        except ParserError as e:
            self.errors.append(e)
            raise
    
    def parse_program(self) -> Program:
        """Parse top-level program: { Statement }"""
        statements = []
        start_token = self.stream.current_token()
        
        while not self.stream.at_end():
            try:
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
            except ParserError as e:
                self.errors.append(e)
                if self.debug:
                    print(f"Parse error: {e}")
                # Error recovery
                self.stream.synchronize_on_error()
                
                # If we're still not at a good recovery point, advance
                if not self.stream.at_end() and not self.stream.match(
                    TokenType.LET, TokenType.FUN, TokenType.IF, TokenType.WHILE,
                    TokenType.FOR, TokenType.RETURN, TokenType.LBRACE):
                    self.stream.advance()
        
        return Program(statements, start_token.line, start_token.col)
    
    # ===== STATEMENT PARSING =====
    
    def parse_statement(self) -> Optional[ASTNode]:
        """Parse any statement type based on current token"""
        current = self.stream.current_token()
        
        # Check for lexical errors first
        if current.type.name.startswith('ERROR'):
            raise LexicalErrorInParsingError(current)
        
        # Function declaration
        if self.stream.match(TokenType.FUN):
            return self.parse_function_declaration()
        
        # Variable declaration
        elif self.stream.match(TokenType.LET):
            stmt = self.parse_variable_declaration()
            self.stream.expect(TokenType.SEMICOLON, "';' after variable declaration")
            return stmt
        
        # Control flow statements
        elif self.stream.match(TokenType.IF):
            return self.parse_if_statement()
        elif self.stream.match(TokenType.WHILE):
            return self.parse_while_statement()
        elif self.stream.match(TokenType.FOR):
            return self.parse_for_statement()
        elif self.stream.match(TokenType.RETURN):
            stmt = self.parse_return_statement()
            self.stream.expect(TokenType.SEMICOLON, "';' after return statement")
            return stmt
        
        # Built-in statements
        elif self.stream.match(TokenType.BUILTIN_PRINT):
            stmt = self.parse_print_statement()
            self.stream.expect(TokenType.SEMICOLON, "';' after print statement")
            return stmt
        elif self.stream.match(TokenType.BUILTIN_DELAY):
            stmt = self.parse_delay_statement()
            self.stream.expect(TokenType.SEMICOLON, "';' after delay statement")
            return stmt
        elif self.stream.match(TokenType.BUILTIN_WRITE):
            stmt = self.parse_write_statement()
            self.stream.expect(TokenType.SEMICOLON, "';' after write statement")
            return stmt
        elif self.stream.match(TokenType.BUILTIN_WRITE_BOX):
            stmt = self.parse_write_box_statement()
            self.stream.expect(TokenType.SEMICOLON, "';' after write_box statement")
            return stmt
        elif self.stream.match(TokenType.BUILTIN_CLEAR):
            stmt = self.parse_clear_statement()
            self.stream.expect(TokenType.SEMICOLON, "';' after clear statement")
            return stmt
        
        # Block statement
        elif self.stream.match(TokenType.LBRACE):
            return self.parse_block()
        
        # Assignment or expression statement
        elif self.stream.match(TokenType.IDENTIFIER):
            # Look ahead to determine if it's an assignment
            # Need to handle identifier with potential array access per EBNF
            return self.parse_assignment_or_expression_statement()
        
        else:
            raise UnexpectedTokenError("statement", current)
    
    def parse_assignment_or_expression_statement(self) -> ASTNode:
        """Parse assignment or expression statement starting with identifier"""
        # Parse identifier (which may include array access per EBNF)
        target = self.parse_identifier_with_optional_index()
        
        # Check if this is an assignment
        if self.stream.match(TokenType.EQUAL):
            self.stream.advance()  # consume '='
            value = self.parse_expression()
            self.stream.expect(TokenType.SEMICOLON, "';' after assignment")
            return Assignment(target, value, target.line, target.col)
        else:
            # This is an expression statement (like function call)
            # The target should be a function call if it's a valid expression statement
            if not isinstance(target, FunctionCall):
                raise SyntaxError("Invalid expression statement", self.stream.current_token())
            self.stream.expect(TokenType.SEMICOLON, "';' after expression statement")
            return target
    
    def parse_variable_declaration(self) -> VariableDeclaration:
        """Parse variable declaration with array support"""
        start_token = self.stream.expect(TokenType.LET)
        name_token = self.stream.expect(TokenType.IDENTIFIER, "variable name")
        self.stream.expect(TokenType.COLON, "':' after variable name")
        var_type = self.parse_type()
        
        # Handle initialization
        initializer = None
        if self.stream.match(TokenType.EQUAL):
            self.stream.advance()  # consume '='
            
            if self.stream.match(TokenType.LBRACKET):
                # Array literal initialization
                initializer = self.parse_array_literal()
            else:
                # Regular expression initialization
                initializer = self.parse_expression()
        
        return VariableDeclaration(name_token.lexeme, var_type, initializer,
                                start_token.line, start_token.col)
    
    def parse_comma_separated_expression(self) -> ASTNode:
        """
        Parse expression up to (but not including) comma level.
        This is used for parsing arguments in built-in functions where
        commas are argument separators, not operators.
        """
        # Parse everything except comma at the top level
        # This includes all arithmetic, relational, and logical operations
        return self.parse_expression()
    
    def parse_array_literal(self) -> ArrayLiteral:
        """Parse array literal: [expr, expr, ...]"""
        start_token = self.stream.expect(TokenType.LBRACKET, "'[' for array literal")
        elements = []
        
        if not self.stream.match(TokenType.RBRACKET):
            elements.append(self.parse_expression())
            while self.stream.match(TokenType.COMMA):
                self.stream.advance()  # consume ','
                elements.append(self.parse_expression())
        
        self.stream.expect(TokenType.RBRACKET, "']' after array elements")
        return ArrayLiteral(elements, start_token.line, start_token.col)
    
    def parse_function_declaration(self) -> FunctionDeclaration:
        """Parse function declaration: 'fun' Identifier '(' [FormalParams] ')' '->' Type Block"""
        start_token = self.stream.expect(TokenType.FUN)
        name_token = self.stream.expect(TokenType.IDENTIFIER, "function name")
        self.stream.expect(TokenType.LPAREN, "'(' after function name")
        
        # Parse parameters
        params = []
        if not self.stream.match(TokenType.RPAREN):
            params = self.parse_formal_params()
        
        self.stream.expect(TokenType.RPAREN, "')' after parameters")
        self.stream.expect(TokenType.ARROW, "'->' before return type")
        return_type = self.parse_type()
        
        body = self.parse_block()
        
        return FunctionDeclaration(name_token.lexeme, params, return_type, body,
                                 start_token.line, start_token.col)
    
    def parse_formal_params(self) -> List[FormalParameter]:
        """Parse formal parameter list"""
        params = []
        params.append(self.parse_formal_param())
        
        while self.stream.match(TokenType.COMMA):
            self.stream.advance()  # consume ','
            params.append(self.parse_formal_param())
        
        return params
    
    def parse_formal_param(self) -> FormalParameter:
        """Parse single formal parameter: Identifier ':' Type"""
        name_token = self.stream.expect(TokenType.IDENTIFIER, "parameter name")
        self.stream.expect(TokenType.COLON, "':' after parameter name")
        param_type = self.parse_type()
        
        return FormalParameter(name_token.lexeme, param_type,
                             name_token.line, name_token.col)
    
    def parse_if_statement(self) -> IfStatement:
        """Parse if statement: 'if' '(' Expr ')' Block ['else' Block]"""
        start_token = self.stream.expect(TokenType.IF)
        self.stream.expect(TokenType.LPAREN, "'(' after 'if'")
        condition = self.parse_expression()
        self.stream.expect(TokenType.RPAREN, "')' after if condition")
        then_block = self.parse_block()
        
        else_block = None
        if self.stream.match(TokenType.ELSE):
            self.stream.advance()  # consume 'else'
            else_block = self.parse_block()
        
        return IfStatement(condition, then_block, else_block,
                          start_token.line, start_token.col)
    
    def parse_while_statement(self) -> WhileStatement:
        """Parse while statement: 'while' '(' Expr ')' Block"""
        start_token = self.stream.expect(TokenType.WHILE)
        self.stream.expect(TokenType.LPAREN, "'(' after 'while'")
        condition = self.parse_expression()
        self.stream.expect(TokenType.RPAREN, "')' after while condition")
        body = self.parse_block()
        
        return WhileStatement(condition, body, start_token.line, start_token.col)
    
    def parse_for_statement(self) -> ForStatement:
        """Parse for statement: 'for' '(' [VariableDecl] ';' Expr ';' [Assignment] ')' Block"""
        start_token = self.stream.expect(TokenType.FOR)
        self.stream.expect(TokenType.LPAREN, "'(' after 'for'")
        
        # Parse initialization (optional)
        init = None
        if not self.stream.match(TokenType.SEMICOLON):
            try:
                init = self.parse_variable_declaration()
            except ParserError as e:
                raise ParserError(f"Invalid for loop initialization: {e.message}", e.token)
        self.stream.expect(TokenType.SEMICOLON, "';' after for loop initialization")
        
        # Parse condition
        try:
            condition = self.parse_expression()
        except ParserError as e:
            raise ParserError(f"Invalid for loop condition: {e.message}", e.token)
        self.stream.expect(TokenType.SEMICOLON, "';' after for loop condition")
        
        # Parse update (optional) - improved error handling
        update = None
        if not self.stream.match(TokenType.RPAREN):
            try:
                target = self.parse_identifier_with_optional_index()
                self.stream.expect(TokenType.EQUAL, "'=' in for loop update")
                value = self.parse_expression()
                update = Assignment(target, value, target.line, target.col)
            except ParserError as e:
                # Better error message for for loop context
                raise ParserError(f"Invalid for loop update clause: {e.message}", e.token)
        
        self.stream.expect(TokenType.RPAREN, "')' after for loop clauses")
        
        try:
            body = self.parse_block()
        except ParserError as e:
            raise ParserError(f"Invalid for loop body: {e.message}", e.token)
        
        return ForStatement(init, condition, update, body,
                        start_token.line, start_token.col)

    
    def parse_return_statement(self) -> ReturnStatement:
        """Parse return statement: 'return' Expr"""
        start_token = self.stream.expect(TokenType.RETURN)
        value = self.parse_expression()
        return ReturnStatement(value, start_token.line, start_token.col)
    
    def parse_print_statement(self) -> PrintStatement:
        """Parse print statement: '__print' Expr"""
        start_token = self.stream.expect(TokenType.BUILTIN_PRINT)
        expr = self.parse_comma_separated_expression()
        return PrintStatement(expr, start_token.line, start_token.col)
    
    def parse_delay_statement(self) -> DelayStatement:
        """Parse delay statement: '__delay' Expr"""
        start_token = self.stream.expect(TokenType.BUILTIN_DELAY)
        expr = self.parse_comma_separated_expression()
        return DelayStatement(expr, start_token.line, start_token.col)

    def parse_write_statement(self) -> WriteStatement:
        """Parse write statement: '__write' Expr ',' Expr ',' Expr"""
        start_token = self.stream.expect(TokenType.BUILTIN_WRITE)
        x = self.parse_comma_separated_expression()
        self.stream.expect(TokenType.COMMA, "',' after first argument")
        y = self.parse_comma_separated_expression()
        self.stream.expect(TokenType.COMMA, "',' after second argument")
        color = self.parse_comma_separated_expression()
        return WriteStatement(x, y, color, start_token.line, start_token.col)

    def parse_write_box_statement(self) -> WriteBoxStatement:
        """Parse write_box statement: '__write_box' Expr ',' Expr ',' Expr ',' Expr ',' Expr"""
        start_token = self.stream.expect(TokenType.BUILTIN_WRITE_BOX)
        x = self.parse_comma_separated_expression()
        self.stream.expect(TokenType.COMMA, "',' after first argument")
        y = self.parse_comma_separated_expression()
        self.stream.expect(TokenType.COMMA, "',' after second argument")
        width = self.parse_comma_separated_expression()
        self.stream.expect(TokenType.COMMA, "',' after third argument")
        height = self.parse_comma_separated_expression()
        self.stream.expect(TokenType.COMMA, "',' after fourth argument")
        color = self.parse_comma_separated_expression()
        return WriteBoxStatement(x, y, width, height, color,
                                start_token.line, start_token.col)

    def parse_clear_statement(self) -> ClearStatement:
        """Parse clear statement: '__clear' Expr"""
        start_token = self.stream.expect(TokenType.BUILTIN_CLEAR)
        color = self.parse_comma_separated_expression()
        return ClearStatement(color, start_token.line, start_token.col)
    
    def parse_block(self) -> Block:
        """Parse block: '{' { Statement } '}'"""
        start_token = self.stream.expect(TokenType.LBRACE, "'{'")
        statements = []
        
        while not self.stream.match(TokenType.RBRACE) and not self.stream.at_end():
            try:
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
            except ParserError as e:
                self.errors.append(e)
                if self.debug:
                    print(f"Statement parse error: {e}")
                # Try to recover
                self.stream.synchronize_on_error()
                if self.stream.match(TokenType.RBRACE):
                    break
        
        self.stream.expect(TokenType.RBRACE, "'}'")
        return Block(statements, start_token.line, start_token.col)
    
    def parse_logical_or_expression(self) -> ASTNode:
        """Parse logical OR expression (lowest precedence after assignment)"""
        left = self.parse_logical_and_expression()
        
        while self.stream.match(TokenType.OR):
            op_token = self.stream.advance()
            right = self.parse_logical_and_expression()
            left = BinaryOperation(left, op_token.lexeme, right,
                                left.line, left.col)
        
        return left

    def parse_logical_and_expression(self) -> ASTNode:
        """Parse logical AND expression (higher than OR, lower than comparisons)"""
        left = self.parse_relational_expression()
        
        while self.stream.match(TokenType.AND):
            op_token = self.stream.advance()
            right = self.parse_relational_expression()
            left = BinaryOperation(left, op_token.lexeme, right,
                                left.line, left.col)
        
        return left
    
    # ===== EXPRESSION PARSING =====
    
    def parse_expression(self) -> ASTNode:
        """Parse expression with proper precedence hierarchy"""
        return self.parse_logical_or_expression()

    def parse_relational_expression(self) -> ASTNode:
        """Parse relational expression: SimpleExpr { RelationalOp SimpleExpr }"""
        left = self.parse_additive_expression()
        
        while self.stream.match(TokenType.EQUAL_EQUAL, TokenType.NOT_EQUAL,
                               TokenType.LESS, TokenType.GREATER,
                               TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL):
            op_token = self.stream.advance()
            right = self.parse_additive_expression()
            left = BinaryOperation(left, op_token.lexeme, right,
                                 left.line, left.col)
        
        return left
    
    def parse_additive_expression(self) -> ASTNode:
        """Parse additive expression: Term { AdditiveOp Term }"""
        left = self.parse_multiplicative_expression()
        
        # SYSTEMATIC FIX: Remove OR from here - it belongs at lower precedence
        while self.stream.match(TokenType.PLUS, TokenType.MINUS):  # No more OR here
            op_token = self.stream.advance()
            right = self.parse_multiplicative_expression()
            left = BinaryOperation(left, op_token.lexeme, right,
                                left.line, left.col)
        
        return left

    # UPDATE parse_multiplicative_expression - REMOVE TokenType.AND:
    def parse_multiplicative_expression(self) -> ASTNode:
        """Parse multiplicative expression: Factor { MultiplicativeOp Factor }"""
        left = self.parse_cast_expression()
        
        # SYSTEMATIC FIX: Remove AND from here - it belongs at lower precedence
        while self.stream.match(TokenType.MULTIPLY, TokenType.SLASH, TokenType.MODULO):  # No more AND here
            op_token = self.stream.advance()
            right = self.parse_cast_expression()
            left = BinaryOperation(left, op_token.lexeme, right,
                                left.line, left.col)
        
        return left
    
    def parse_cast_expression(self) -> ASTNode:
        """Parse cast expression: UnaryExpr [ 'as' Type ]"""
        expr = self.parse_unary_expression()
        
        # Handle cast at higher precedence than arithmetic operations
        if self.stream.match(TokenType.AS):
            as_token = self.stream.advance()  # consume 'as'
            target_type = self.parse_type()
            
            # Add validation for meaningful casts
            valid_types = {'int', 'float', 'bool', 'colour'}
            if target_type not in valid_types:
                raise ParserError(
                    f"Invalid cast target type '{target_type}'. Valid types are: {', '.join(valid_types)}", 
                    as_token
                )
            
            expr = CastExpression(expr, target_type, as_token.line, as_token.col)
        
        return expr

    def parse_unary_expression(self) -> ASTNode:
        """Parse unary expression: ['-' | 'not'] Factor"""
        if self.stream.match(TokenType.MINUS, TokenType.NOT):
            op_token = self.stream.advance()
            operand = self.parse_unary_expression()
            return UnaryOperation(op_token.lexeme, operand,
                                op_token.line, op_token.col)
        
        return self.parse_primary_expression()
    
    def parse_primary_expression(self) -> ASTNode:
        """Parse primary expression with array literal support"""
        current = self.stream.current_token()

        # Add this check at the start:
        if current.type.name.startswith('ERROR'):
            raise LexicalErrorInParsingError(current)

        # Array literals
        if current.type == TokenType.LBRACKET:
            return self.parse_array_literal()
        
        # Literals
        elif current.type in [TokenType.INT_LITERAL, TokenType.FLOAT_LITERAL,
                        TokenType.COLOUR_LITERAL, TokenType.TRUE, TokenType.FALSE]:
            return self.parse_literal()
        
        # Built-in functions
        elif current.type == TokenType.BUILTIN_WIDTH:
            self.stream.advance()
            return PadWidth(current.line, current.col)
        
        elif current.type == TokenType.BUILTIN_HEIGHT:
            self.stream.advance()
            return PadHeight(current.line, current.col)
        
        elif current.type == TokenType.BUILTIN_READ:
            return self.parse_pad_read()
        
        elif current.type == TokenType.BUILTIN_RANDI:
            return self.parse_pad_rand_int()
        
        # Identifier (variable, function call, or with array access)
        elif current.type == TokenType.IDENTIFIER:
            return self.parse_identifier_with_optional_index()
        
        # Parenthesized expression
        elif current.type == TokenType.LPAREN:
            self.stream.advance()  # consume '('
            expr = self.parse_expression()
            self.stream.expect(TokenType.RPAREN, "')' after expression")
            return expr
        
        else:
            raise UnexpectedTokenError("expression", current)
    
    def parse_identifier_with_optional_index(self) -> ASTNode:
        """
        Parse identifier with optional array access as per EBNF:
        ⟨Identifier⟩ ::= ⟨Letter⟩ { '_' | ⟨Letter⟩ | ⟨Digit⟩ } ['[' ⟨Expr⟩ ']']
        
        This can result in:
        1. Simple identifier
        2. Function call
        3. Identifier with array access (IndexAccess)
        """
        name_token = self.stream.expect(TokenType.IDENTIFIER, "identifier")
        base = Identifier(name_token.lexeme, name_token.line, name_token.col)
        
        # Check for array access first (per EBNF, this is part of identifier)
        if self.stream.match(TokenType.LBRACKET):
            self.stream.advance()  # consume '['
            index = self.parse_expression()
            self.stream.expect(TokenType.RBRACKET, "']' after array index")
            base = IndexAccess(base, index, name_token.line, name_token.col)
        
        # Then check for function call
        if self.stream.match(TokenType.LPAREN):
            if isinstance(base, IndexAccess):
                # More descriptive error
                raise SyntaxError(
                    f"Cannot call function on array access '{base.base.name}[...]'. "
                    f"Function calls and array indexing cannot be combined in this context.",
                    self.stream.current_token()
                )
            return self.parse_function_call_continuation(name_token.lexeme, name_token)
        
        return base
    
    def parse_function_call_continuation(self, name: str, name_token: Token) -> FunctionCall:
        """Parse function call continuation after identifier: '(' [ActualParams] ')'"""
        self.stream.expect(TokenType.LPAREN, "'(' for function call")
        
        arguments = []
        if not self.stream.match(TokenType.RPAREN):
            arguments.append(self.parse_expression())
            while self.stream.match(TokenType.COMMA):
                self.stream.advance()  # consume ','
                arguments.append(self.parse_expression())
        
        self.stream.expect(TokenType.RPAREN, "')' after function arguments")
        return FunctionCall(name, arguments, name_token.line, name_token.col)
    
    def parse_literal(self) -> Literal:
        """Parse literal values"""
        token = self.stream.advance()
        return create_literal_from_token(token)
    
    def parse_pad_read(self) -> PadRead:
        """Parse __read expression: '__read' Expr ',' Expr"""
        start_token = self.stream.expect(TokenType.BUILTIN_READ)
        x = self.parse_comma_separated_expression()
        self.stream.expect(TokenType.COMMA, "',' after first argument to __read")
        y = self.parse_comma_separated_expression()
        return PadRead(x, y, start_token.line, start_token.col)
    
    def parse_pad_rand_int(self) -> PadRandI:
        """Parse __randi expression: '__randi' Expr"""
        start_token = self.stream.expect(TokenType.BUILTIN_RANDI)
        max_val = self.parse_comma_separated_expression()
        return PadRandI(max_val, start_token.line, start_token.col)
    
    def parse_type(self) -> Union[str, ArrayType]:
        """Parse type specification including arrays: 'int' | 'int[5]' | 'int[]'"""
        token = self.stream.current_token()
        
        if token.type in [TokenType.TYPE_INT, TokenType.TYPE_FLOAT,
                        TokenType.TYPE_BOOL, TokenType.TYPE_COLOUR]:
            base_type = token.lexeme
            self.stream.advance()
            
            # Check for array declaration
            if self.stream.match(TokenType.LBRACKET):
                self.stream.advance()  # consume '['
                
                if self.stream.match(TokenType.RBRACKET):
                    # Dynamic array: int[]
                    self.stream.advance()  # consume ']'
                    return ArrayType(base_type, None)
                elif self.stream.match(TokenType.INT_LITERAL):
                    # Fixed-size array: int[5]
                    size_token = self.stream.advance()
                    size = int(size_token.lexeme)
                    if size <= 0:
                        raise ParserError(f"Array size must be positive, got {size}", size_token)
                    self.stream.expect(TokenType.RBRACKET, "']' after array size")
                    return ArrayType(base_type, size)
                else:
                    raise UnexpectedTokenError("array size or ']'", self.stream.current_token())
            
            return base_type
        else:
            raise UnexpectedTokenError("type (int, float, bool, or colour)", token)
    
    # ===== ERROR HANDLING AND UTILITIES =====
    
    def report_errors(self) -> bool:
        """Report all parsing errors"""
        if self.errors:
            print(f"Parsing Failed: {len(self.errors)} error(s) found")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
            return False
        return True
    
    def has_errors(self) -> bool:
        """Check if parser has encountered errors"""
        return len(self.errors) > 0
    
    def clear_errors(self):
        """Clear all accumulated errors"""
        self.errors.clear()