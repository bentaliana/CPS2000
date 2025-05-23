from enum import Enum, auto
from collections import defaultdict
import sys

class TokenType(Enum):
    # Identifiers and Literals
    IDENTIFIER = auto()
    INTEGER = auto()
    FLOAT = auto()
    BOOLEAN = auto()
    COLOUR = auto()
    
    # Keywords
    LET = auto()
    FUN = auto()
    IF = auto()
    ELSE = auto()
    FOR = auto()
    WHILE = auto()
    RETURN = auto()
    AS = auto()
    NOT = auto()
    AND = auto()
    OR = auto()
    TRUE = auto()
    FALSE = auto()
    
    # Built-ins 
    BUILTIN_PRINT = auto()
    BUILTIN_DELAY = auto()
    BUILTIN_WRITE = auto()
    BUILTIN_WRITE_BOX = auto()
    BUILTIN_RANDOM_INT = auto()  
    BUILTIN_READ = auto()
    BUILTIN_WIDTH = auto()
    BUILTIN_HEIGHT = auto()
    BUILTIN_CLEAR = auto()
    
    # Operators
    EQUAL = auto()
    SEMICOLON = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    SLASH = auto()
    LESS = auto()
    GREATER = auto()
    EXCL = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COLON = auto()
    COMMA = auto()
    HASH = auto()
    DOT = auto()
    EQUAL_EQUAL = auto()
    NOT_EQUAL = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()
    ARROW = auto()
    
    # Special
    ERROR = auto()
    END = auto()
    WHITESPACE = auto()
    LINECOMMENT = auto()
    BLOCKCOMMENT = auto()
    NEWLINE = auto()

class Token:
    def __init__(self, token_type, lexeme, line=0, col=0):
        self.type = token_type
        self.lexeme = sys.intern(lexeme)
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type.name}, '{self.lexeme}', line={self.line}, col={self.col})"

class FSALexer:
    """
    Fully table-driven FSA-based lexer for PArL language (Task 1)
    Implements the micro-syntax as specified in the assignment EBNF
    """
    
    def __init__(self):
        self._init_char_categories()
        self._init_transition_table()
        self._init_keywords_and_builtins()
        self.debug = False

    def _init_char_categories(self):
        """Initialize character categories for the transition table"""
        self.categories = [
            "letter",      # A-Z, a-z (excluding hex letters A-F, a-f)
            "hexletter",   # A-F, a-f
            "digit",       # 0-9
            "underscore",  # _
            "plus",        # +
            "minus",       # -
            "multiply",    # *
            "slash",       # /
            "equal",       # =
            "less",        # <
            "greater",     # >
            "excl",        # !
            "lparen",      # (
            "rparen",      # )
            "lbrace",      # {
            "rbrace",      # }
            "lbracket",    # [
            "rbracket",    # ]
            "colon",       # :
            "comma",       # ,
            "semicolon",   # ;
            "hash",        # #
            "dot",         # .
            "whitespace",  # space, tab, \r
            "newline",     # \n
            "other"        # any other character
        ]
        self.cat_map = {cat: idx for idx, cat in enumerate(self.categories)}

    def _categorize_char(self, c):
        """Categorize a single character according to PArL micro-syntax"""
        if not c:
            return "other"
        
        # Handle hex letters specifically (A-F, a-f)
        if c in 'ABCDEFabcdef':
            return "hexletter"
        elif c.isalpha():
            return "letter"
        elif c.isdigit():
            return "digit"
        elif c == '_':
            return "underscore"
        elif c == '+':
            return "plus"
        elif c == '-':
            return "minus"
        elif c == '*':
            return "multiply"
        elif c == '/':
            return "slash"
        elif c == '=':
            return "equal"
        elif c == '<':
            return "less"
        elif c == '>':
            return "greater"
        elif c == '!':
            return "excl"
        elif c == '(':
            return "lparen"
        elif c == ')':
            return "rparen"
        elif c == '{':
            return "lbrace"
        elif c == '}':
            return "rbrace"
        elif c == '[':
            return "lbracket"
        elif c == ']':
            return "rbracket"
        elif c == ':':
            return "colon"
        elif c == ',':
            return "comma"
        elif c == ';':
            return "semicolon"
        elif c == '#':
            return "hash"
        elif c == '.':
            return "dot"
        elif c in [' ', '\t', '\r']:
            return "whitespace"
        elif c == '\n':
            return "newline"
        else:
            return "other"

    def _init_transition_table(self):
        """
        Initialize the DFA transition table for PArL tokens
        State 0 is the initial state
        States with negative numbers indicate error states
        """
        # Initialize transition table with error state (-1)
        self.Tx = defaultdict(lambda: defaultdict(lambda: -1))
        self.accepting_states = {}
        
        def add_transition(from_state, char_categories, to_state):
            """Helper to add transitions for multiple character categories"""
            for category in char_categories:
                if category in self.cat_map:
                    self.Tx[from_state][self.cat_map[category]] = to_state

        # State 0: Initial state
        
        # === IDENTIFIERS AND KEYWORDS ===
        # Identifier: Letter { '_' | Letter | Digit }
        # Built-ins: '__' Letter { '_' | Letter | Digit }
        
        # Regular identifiers (starts with letter or hex letter)
        add_transition(0, ["letter", "hexletter"], 1)
        add_transition(1, ["letter", "hexletter", "digit", "underscore"], 1)
        self.accepting_states[1] = TokenType.IDENTIFIER
        
        # Built-ins (start with __)
        add_transition(0, ["underscore"], 2)  # First underscore
        add_transition(2, ["underscore"], 3)  # Second underscore  
        add_transition(3, ["letter", "hexletter"], 4)  # Must start with letter
        add_transition(4, ["letter", "hexletter", "digit", "underscore"], 4)
        self.accepting_states[4] = TokenType.IDENTIFIER  # Will be refined later
        
        # === NUMERIC LITERALS ===
        
        # Integer: Digit { Digit }
        add_transition(0, ["digit"], 5)
        add_transition(5, ["digit"], 5)
        self.accepting_states[5] = TokenType.INTEGER
        
        # Float: Digit { Digit } '.' Digit { Digit }
        add_transition(5, ["dot"], 6)  # From integer state
        add_transition(6, ["digit"], 7)  # Must have at least one digit after dot
        add_transition(7, ["digit"], 7)
        self.accepting_states[7] = TokenType.FLOAT
        
        # === COLOUR LITERALS ===
        # ColourLiteral: '#' Hex Hex Hex Hex Hex Hex
        add_transition(0, ["hash"], 8)
        add_transition(8, ["hexletter", "digit"], 9)   # 1st hex digit
        add_transition(9, ["hexletter", "digit"], 10)  # 2nd hex digit
        add_transition(10, ["hexletter", "digit"], 11) # 3rd hex digit
        add_transition(11, ["hexletter", "digit"], 12) # 4th hex digit
        add_transition(12, ["hexletter", "digit"], 13) # 5th hex digit
        add_transition(13, ["hexletter", "digit"], 14) # 6th hex digit
        self.accepting_states[14] = TokenType.COLOUR
        
        # === OPERATORS ===
        
        # Arrow: '->'
        add_transition(0, ["minus"], 15)
        add_transition(15, ["greater"], 16)
        self.accepting_states[15] = TokenType.MINUS
        self.accepting_states[16] = TokenType.ARROW
        
        # Equality operators: '=', '=='
        add_transition(0, ["equal"], 17)
        add_transition(17, ["equal"], 18)
        self.accepting_states[17] = TokenType.EQUAL
        self.accepting_states[18] = TokenType.EQUAL_EQUAL
        
        # Inequality: '!', '!='
        add_transition(0, ["excl"], 19)
        add_transition(19, ["equal"], 20)
        self.accepting_states[19] = TokenType.EXCL
        self.accepting_states[20] = TokenType.NOT_EQUAL
        
        # Less than: '<', '<='
        add_transition(0, ["less"], 21)
        add_transition(21, ["equal"], 22)
        self.accepting_states[21] = TokenType.LESS
        self.accepting_states[22] = TokenType.LESS_EQUAL
        
        # Greater than: '>', '>='
        add_transition(0, ["greater"], 23)
        add_transition(23, ["equal"], 24)
        self.accepting_states[23] = TokenType.GREATER
        self.accepting_states[24] = TokenType.GREATER_EQUAL
        
        # === COMMENTS ===
        
        # Line comment: '//'
        add_transition(0, ["slash"], 25)
        add_transition(25, ["slash"], 26)
        # Line comment continues until newline
        for cat in self.categories:
            if cat != "newline":
                add_transition(26, [cat], 26)
        add_transition(26, ["newline"], 27)
        self.accepting_states[27] = TokenType.LINECOMMENT
        
        # Block comment: '/*' ... '*/'
        add_transition(25, ["multiply"], 28)
        # Block comment can contain any character
        for cat in self.categories:
            add_transition(28, [cat], 28)
        add_transition(28, ["multiply"], 29)  # Possible end
        add_transition(29, ["slash"], 30)     # Confirmed end
        # If not '/', go back to comment content
        for cat in self.categories:
            if cat not in ["slash", "multiply"]:
                add_transition(29, [cat], 28)
        add_transition(29, ["multiply"], 29)  # Stay in end-check state
        self.accepting_states[30] = TokenType.BLOCKCOMMENT
        
        # Single slash (division operator)
        self.accepting_states[25] = TokenType.SLASH
        
        # === SINGLE CHARACTER TOKENS ===
        single_char_tokens = [
            (["plus"], TokenType.PLUS),
            (["multiply"], TokenType.MULTIPLY),
            (["lparen"], TokenType.LPAREN),
            (["rparen"], TokenType.RPAREN),
            (["lbrace"], TokenType.LBRACE),
            (["rbrace"], TokenType.RBRACE),
            (["lbracket"], TokenType.LBRACKET),
            (["rbracket"], TokenType.RBRACKET),
            (["colon"], TokenType.COLON),
            (["comma"], TokenType.COMMA),
            (["semicolon"], TokenType.SEMICOLON),
            (["dot"], TokenType.DOT),
        ]
        
        state_counter = 31
        for char_cats, token_type in single_char_tokens:
            add_transition(0, char_cats, state_counter)
            self.accepting_states[state_counter] = token_type
            state_counter += 1
        
        # === WHITESPACE ===
        add_transition(0, ["whitespace"], 100)
        self.accepting_states[100] = TokenType.WHITESPACE
        
        add_transition(0, ["newline"], 101)
        self.accepting_states[101] = TokenType.NEWLINE

    def _init_keywords_and_builtins(self):
        """Initialize keyword and built-in mappings"""
        self.keywords = {
            "let": TokenType.LET,
            "fun": TokenType.FUN,
            "if": TokenType.IF,
            "else": TokenType.ELSE,
            "for": TokenType.FOR,
            "while": TokenType.WHILE,
            "return": TokenType.RETURN,
            "as": TokenType.AS,
            "not": TokenType.NOT,
            "and": TokenType.AND,
            "or": TokenType.OR,
            "float": TokenType.FLOAT,
            "int": TokenType.INTEGER,
            "bool": TokenType.BOOLEAN,
            "colour": TokenType.COLOUR,
            "true": TokenType.TRUE,
            "false": TokenType.FALSE,
        }
        
        # Built-ins as specified in assignment EBNF
        self.builtins = {
            "__print": TokenType.BUILTIN_PRINT,
            "__delay": TokenType.BUILTIN_DELAY,
            "__write": TokenType.BUILTIN_WRITE,
            "__write_box": TokenType.BUILTIN_WRITE_BOX,
            "__random_int": TokenType.BUILTIN_RANDOM_INT,  # Corrected name
            "__read": TokenType.BUILTIN_READ,
            "__width": TokenType.BUILTIN_WIDTH,
            "__height": TokenType.BUILTIN_HEIGHT,
            "__clear": TokenType.BUILTIN_CLEAR,
        }

    def tokenize(self, text):
        """
        Tokenize input text using the FSA transition table
        Returns list of tokens
        """
        tokens = []
        pos = 0
        line = 1
        col = 1
        text_len = len(text)
        
        while pos < text_len:
            # Skip whitespace and track position
            start_pos = pos
            start_line = line
            start_col = col
            
            # Table-driven FSA simulation
            state = 0
            lexeme = ""
            last_accepting_state = -1
            last_accepting_pos = pos
            
            # Simulate DFA
            while pos < text_len:
                char = text[pos]
                char_category = self._categorize_char(char)
                char_cat_index = self.cat_map[char_category]
                
                next_state = self.Tx[state][char_cat_index]
                
                if next_state == -1:
                    # No valid transition
                    break
                
                # Valid transition
                state = next_state
                lexeme += char
                pos += 1
                
                # Update position tracking
                if char == '\n':
                    line += 1
                    col = 1
                else:
                    col += 1
                
                # Check if current state is accepting
                if state in self.accepting_states:
                    last_accepting_state = state
                    last_accepting_pos = pos
            
            # Process the token
            if last_accepting_state != -1:
                # We found a valid token
                final_lexeme = text[start_pos:last_accepting_pos]
                token_type = self.accepting_states[last_accepting_state]
                
                # Reset position to end of accepted token
                pos = last_accepting_pos
                line = start_line
                col = start_col
                
                # Recalculate line/col for end position
                for i in range(start_pos, last_accepting_pos):
                    if text[i] == '\n':
                        line += 1
                        col = 1
                    else:
                        col += 1
                
                # Refine token type based on lexeme
                token_type = self._refine_token_type(token_type, final_lexeme)
                
                # Add token if not whitespace/comment (unless debugging)
                if token_type not in [TokenType.WHITESPACE, TokenType.NEWLINE, 
                                    TokenType.LINECOMMENT, TokenType.BLOCKCOMMENT] or self.debug:
                    tokens.append(Token(token_type, final_lexeme, start_line, start_col))
                    
            else:
                # Lexical error - consume one character
                error_char = text[start_pos] if start_pos < text_len else ""
                tokens.append(Token(TokenType.ERROR, error_char, start_line, start_col))
                pos = start_pos + 1
                col += 1
        
        # Add end token
        tokens.append(Token(TokenType.END, "", line, col))
        return tokens

    def _refine_token_type(self, base_type, lexeme):
        """Refine token type based on lexeme content"""
        if base_type == TokenType.IDENTIFIER:
            # Check for keywords
            if lexeme in self.keywords:
                return self.keywords[lexeme]
            
            # Check for built-ins
            if lexeme in self.builtins:
                return self.builtins[lexeme]
            
            # Check for boolean literals
            if lexeme == "true":
                return TokenType.TRUE
            elif lexeme == "false":
                return TokenType.FALSE
        
        return base_type

    def report_errors(self, tokens):
        """Report any lexical errors found during tokenization"""
        errors = [token for token in tokens if token.type == TokenType.ERROR]
        if errors:
            print(f"Lexical Analysis Errors ({len(errors)} found):")
            for error in errors:
                print(f"  Line {error.line}, Col {error.col}: "
                      f"Invalid character '{error.lexeme}'")
            return False
        return True


