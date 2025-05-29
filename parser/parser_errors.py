"""
Parser Error Classes for PArL Language Parser
Provides comprehensive error handling with position tracking
"""

class ParserError(Exception):
    """Base class for all parser errors"""
    def __init__(self, message: str, token=None, line: int = 0, col: int = 0):
        self.message = message
        self.token = token
        self.line = line if token is None else token.line
        self.col = col if token is None else token.col
        super().__init__(self.format_error())
    
    def format_error(self):
        if self.token:
            return f"Parser Error at line {self.line}, col {self.col}: {self.message} (found '{self.token.lexeme}')"
        return f"Parser Error at line {self.line}, col {self.col}: {self.message}"


class UnexpectedTokenError(ParserError):
    """Error for unexpected tokens during parsing"""
    def __init__(self, expected: str, found_token):
        message = f"Expected {expected}, but found '{found_token.lexeme}' ({found_token.type.name})"
        super().__init__(message, found_token)


class UnexpectedEOFError(ParserError):
    """Error for unexpected end of file"""
    def __init__(self, expected: str, last_token=None):
        message = f"Unexpected end of file. Expected {expected}"
        super().__init__(message, last_token)


class LexicalErrorInParsingError(ParserError):
    """Error when lexical error tokens are encountered during parsing"""
    def __init__(self, lexical_error_token):
        error_messages = {
            'ERROR_INVALID_FLOAT': "Invalid float literal",
            'ERROR_INVALID_COLOUR': "Invalid colour literal",
            'ERROR_UNTERMINATED_COMMENT': "Unterminated block comment",
            'ERROR_NESTED_COMMENT': "Nested block comment not allowed",
            'ERROR_STRAY_COMMENT_CLOSE': "Stray '*/' outside comment block",
            'ERROR': "Invalid character"
        }
        
        error_type = lexical_error_token.type.name
        message = error_messages.get(error_type, f"Lexical error: {lexical_error_token.lexeme}")
        super().__init__(message, lexical_error_token)


class SyntaxError(ParserError):
    """General syntax error during parsing"""
    def __init__(self, message: str, token=None):
        super().__init__(f"Syntax error: {message}", token)


class InvalidExpressionError(ParserError):
    """Error when an invalid expression is encountered"""
    def __init__(self, context: str, token):
        message = f"Invalid expression in {context}"
        super().__init__(message, token)


class MissingTokenError(ParserError):
    """Error when a required token is missing"""
    def __init__(self, expected_token: str, context: str, token=None):
        message = f"Missing {expected_token} in {context}"
        super().__init__(message, token)