"""
Token Stream Management for PArL Parser
Provides clean abstraction for token iteration with lookahead support
"""

from typing import List, Optional
from lexer import Token, TokenType
from .parser_errors import UnexpectedTokenError, UnexpectedEOFError


class TokenStream:
    """Encapsulates token iteration with lookahead and error handling"""
    
    def __init__(self, tokens: List[Token]):
        # Filter out comments and whitespace, but keep error tokens for handling
        self.tokens = [t for t in tokens if t.type not in 
                      [TokenType.WHITESPACE, TokenType.NEWLINE, 
                       TokenType.LINECOMMENT, TokenType.BLOCKCOMMENT]]
        self.position = 0
        self.errors = []
    
    def current_token(self) -> Token:
        """Get current token"""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        # Return the last token (should be END token)
        return self.tokens[-1] if self.tokens else Token(TokenType.END, "", 0, 0)
    
    def peek(self, offset: int = 1) -> Token:
        """Look ahead at token with given offset (default 1 for next token)"""
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1] if self.tokens else Token(TokenType.END, "", 0, 0)
    
    def advance(self) -> Token:
        """Move to next token and return the current one"""
        current = self.current_token()
        if self.position < len(self.tokens) - 1:
            self.position += 1
        return current
    
    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types"""
        current = self.current_token()
        return current.type in token_types
    
    def expect(self, token_type: TokenType, context: str = None) -> Token:
        """Consume token if it matches expected type, otherwise raise error"""
        current = self.current_token()
        
        # Check for lexical errors first
        if current.type.name.startswith('ERROR'):
            from parser_errors import LexicalErrorInParsingError
            raise LexicalErrorInParsingError(current)
        
        if self.match(token_type):
            return self.advance()
        
        # Create descriptive error message
        expected_name = context if context else token_type.name.lower().replace('_', ' ')
        
        if current.type == TokenType.END:
            raise UnexpectedEOFError(expected_name, current)
        else:
            raise UnexpectedTokenError(expected_name, current)
    
    def at_end(self) -> bool:
        """Check if we're at the end of tokens"""
        return self.current_token().type == TokenType.END
    
    def consume_if_match(self, *token_types: TokenType) -> Optional[Token]:
        """Consume and return token if it matches any given type, otherwise return None"""
        if self.match(*token_types):
            return self.advance()
        return None
    
    def synchronize_on_error(self):
        """Skip tokens until we find a statement boundary for error recovery"""
        sync_tokens = {
            TokenType.SEMICOLON, TokenType.LBRACE, TokenType.RBRACE,
            TokenType.LET, TokenType.FUN, TokenType.IF, TokenType.WHILE,
            TokenType.FOR, TokenType.RETURN, TokenType.END
        }
        
        while not self.at_end():
            current = self.current_token()
            if current.type in sync_tokens:
                if current.type == TokenType.SEMICOLON:
                    self.advance()  # consume the semicolon
                break
            self.advance()
    
    def get_context_info(self, context_size: int = 3) -> str:
        """Get context information around current position for debugging"""
        start = max(0, self.position - context_size)
        end = min(len(self.tokens), self.position + context_size + 1)
        
        context_tokens = []
        for i in range(start, end):
            marker = " >> " if i == self.position else "    "
            token = self.tokens[i]
            context_tokens.append(f"{marker}{token.type.name}: '{token.lexeme}'")
        
        return "\n".join(context_tokens)