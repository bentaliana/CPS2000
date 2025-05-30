from enum import Enum, auto
from collections import defaultdict
import sys

class TokenType(Enum):
    # Identifiers and Literals
    IDENTIFIER = auto()
    INT_LITERAL = auto()
    FLOAT_LITERAL = auto()
    COLOUR_LITERAL = auto()
    
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
    
    # Type keywords
    TYPE_INT = auto()
    TYPE_FLOAT = auto()
    TYPE_BOOL = auto()
    TYPE_COLOUR = auto()
    
    # Built-ins (corrected based on assignment EBNF and examples)
    BUILTIN_PRINT = auto()
    BUILTIN_DELAY = auto()
    BUILTIN_WRITE = auto()
    BUILTIN_WRITE_BOX = auto()
    BUILTIN_RANDI = auto()        # Corrected: __randi not __random_int
    BUILTIN_READ = auto()
    BUILTIN_WIDTH = auto()
    BUILTIN_HEIGHT = auto()
    BUILTIN_CLEAR = auto()        # Added: used in examples
    
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
    MODULO = auto()  # Add this line
    
    # Special
    ERROR = auto()
    END = auto()
    WHITESPACE = auto()
    LINECOMMENT = auto()
    BLOCKCOMMENT = auto()
    NEWLINE = auto()
    ERROR_INVALID_FLOAT = auto()
    ERROR_INVALID_COLOUR = auto()
    ERROR_UNTERMINATED_COMMENT = auto()
    ERROR_NESTED_COMMENT = auto()
    ERROR_STRAY_COMMENT_CLOSE = auto()

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
    Table-driven FSA-based lexer for PArL language (Task 1)
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
            "other",        # any other character
            "modulo",      # Add this line
        ]
        self.cat_map = {cat: idx for idx, cat in enumerate(self.categories)}

    def _categorize_char(self, c):
        """Categorize a single character according to PArL micro-syntax"""
        if c.isalpha():
            if c in 'ABCDEFabcdef': 
                return "hexletter"
            return "letter"
        if c.isdigit(): 
            return "digit"
        if c == '_': 
            return "underscore"
        if c == '+': 
            return "plus"
        if c == '-': 
            return "minus"
        if c == '*': 
            return "multiply"
        if c == '/': 
            return "slash"
        if c == '=': 
            return "equal"
        if c == '<': 
            return "less"
        if c == '>': 
            return "greater"
        if c == '!': 
            return "excl"
        if c == '(': 
            return "lparen"
        if c == ')': 
            return "rparen"
        if c == '{': 
            return "lbrace"
        if c == '}': 
            return "rbrace"
        if c == '[': 
            return "lbracket"
        if c == ']': 
            return "rbracket"
        if c == ':': 
            return "colon"
        if c == ',': 
            return "comma"
        if c == ';': 
            return "semicolon"
        if c == '#': 
            return "hash"
        if c == '.': 
            return "dot"
        if c == '%': 
            return "modulo"
        # Improved whitespace handling
        if c.isspace() and c != '\n':
            return "whitespace"
        if c == '\n': 
            return "newline"
        return "other"

    def _init_transition_table(self):
        """
        Initialize the DFA transition table for PArL tokens
        Following the assignment's EBNF grammar precisely
        """
        # Initialize transition table with error state (-1)
        self.Tx = defaultdict(lambda: defaultdict(lambda: -1))
        self.accepting_states = {}
        
        def add_transition(from_state, char_categories, to_state):
            """Helper to add transitions for multiple character categories"""
            for category in char_categories:
                if category in self.cat_map:
                    self.Tx[from_state][self.cat_map[category]] = to_state

        # ===== NUMERIC LITERALS =====
        # Integer: Digit { Digit }
        add_transition(0, ["digit"], 5)
        add_transition(5, ["digit"], 5)
        self.accepting_states[5] = TokenType.INT_LITERAL  # Accept integers

        # Float: Ensure ".123" and "123.45" are valid, "123." is invalid
        add_transition(5, ["dot"], 30)  # State 30: After integer part, saw '.')
        add_transition(30, ["digit"], 6)  # Valid float (e.g., "123.4")
        add_transition(6, ["digit"], 6)
        self.accepting_states[6] = TokenType.FLOAT_LITERAL

        # State 30 is now accepting as ERROR_INVALID_FLOAT to consume "123." as single token
        self.accepting_states[30] = TokenType.ERROR_INVALID_FLOAT

        # ===== COLOUR LITERALS =====
        add_transition(0, ["hash"], 8)
        add_transition(8, ["hexletter", "digit"], 9)   # 1st hex digit
        add_transition(9, ["hexletter", "digit"], 10)  # 2nd
        add_transition(10, ["hexletter", "digit"], 11) # 3rd
        add_transition(11, ["hexletter", "digit"], 12) # 4th
        add_transition(12, ["hexletter", "digit"], 13) # 5th
        add_transition(13, ["hexletter", "digit"], 14) # 6th
        self.accepting_states[14] = TokenType.COLOUR_LITERAL

        # Add error transitions for invalid characters in color literals
        # Consume invalid characters to make single error token
        for state in [8, 9, 10, 11, 12, 13]:
            # For any invalid character, go to error state that continues consuming
            for cat in ["letter", "other"]:  # Invalid hex characters
                add_transition(state, [cat], 44)  # State 44: colour error state
        
        # State 44: Continue consuming characters for invalid colour
        for cat in self.categories:
            if cat not in ["whitespace", "newline", "lparen", "rparen", "lbrace", "rbrace", 
                          "lbracket", "rbracket", "semicolon", "comma", "colon"]:
                add_transition(44, [cat], 44)
        self.accepting_states[44] = TokenType.ERROR_INVALID_COLOUR

        # ===== STRAY */ DETECTION =====
        add_transition(0, ["multiply"], 33)  # State 33: Saw '*' at top level
        add_transition(33, ["slash"], 34)    # State 34: Saw '*/' → error
        self.accepting_states[33] = TokenType.MULTIPLY  # Single '*' is valid multiply
        self.accepting_states[34] = TokenType.ERROR_STRAY_COMMENT_CLOSE

        # ===== OTHER EXISTING TRANSITIONS =====
        # Add other transitions here (e.g., identifiers, operators, etc.)
        # === IDENTIFIERS (Assignment EBNF: Letter { '_' | Letter | Digit }) ===
        # Regular identifiers start with letter or hexletter
        add_transition(0, ["letter", "hexletter"], 1)
        add_transition(1, ["letter", "hexletter", "digit", "underscore"], 1)
        self.accepting_states[1] = TokenType.IDENTIFIER
        
        # Built-ins: start with '__'
        add_transition(0, ["underscore"], 2)
        add_transition(2, ["underscore"], 3)
        add_transition(3, ["letter", "hexletter"], 4)
        add_transition(4, ["letter", "hexletter", "digit", "underscore"], 4)
        self.accepting_states[4] = TokenType.IDENTIFIER  # Will be refined to built-ins
        
        # === OPERATORS ===
        # Arrow: '->' (FIXED: proper precedence)
        add_transition(0, ["minus"], 15)
        add_transition(15, ["greater"], 16)
        self.accepting_states[15] = TokenType.MINUS  # Single minus is valid
        self.accepting_states[16] = TokenType.ARROW  # Arrow takes precedence
        
        # Equality: '=', '=='
        add_transition(0, ["equal"], 17)
        add_transition(17, ["equal"], 18)
        self.accepting_states[17] = TokenType.EQUAL
        self.accepting_states[18] = TokenType.EQUAL_EQUAL
        
        # Inequality: '!', '!='
        add_transition(0, ["excl"], 19)
        add_transition(19, ["equal"], 20)
        # Removed accepting state for state 19 (single '!')
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
        
        # === COMMENTS (Assignment: '//' line, '/*...*/' block) ===
        add_transition(0, ["slash"], 25)
        self.accepting_states[25] = TokenType.SLASH  # Division operator
        
        # Line comment: '//'
        add_transition(25, ["slash"], 26)
        # Continue until newline
        for cat in self.categories:
            if cat not in ["newline"]:
                add_transition(26, [cat], 26)
        self.accepting_states[26] = TokenType.LINECOMMENT
        
        # Block comment with nested error detection
        add_transition(25, ["multiply"], 27)  # Start of block comment
        
        # State 27: In comment body - FIXED FOR PROPER COMMENT HANDLING
        for cat in self.categories:
            if cat == "multiply":
                add_transition(27, ["multiply"], 28)  # Potential end marker
            elif cat == "slash":
                add_transition(27, ["slash"], 31)  # Track '/' for nested detection
            else:
                add_transition(27, [cat], 27)  # Stay in comment
        
        # State 28: Saw '*' in comment - potential end
        add_transition(28, ["slash"], 29)  # End of comment '*/'
        add_transition(28, ["multiply"], 28)  # Multiple asterisks
        # Go back to comment body if not '/'
        for cat in self.categories:
            if cat not in ["slash", "multiply"]:
                add_transition(28, [cat], 27)
        
        # State 31: Saw '/' in comment - check for nested '/*'
        add_transition(31, ["multiply"], 32)  # Nested '/*' → error
        self.accepting_states[32] = TokenType.ERROR_NESTED_COMMENT
        # Continue comment for other characters
        for cat in self.categories:
            if cat not in ["multiply"]:
                add_transition(31, [cat], 27)
        
        self.accepting_states[29] = TokenType.BLOCKCOMMENT
        
        # === SINGLE CHARACTER TOKENS ===
        single_tokens = [
            (45, ["plus"], TokenType.PLUS),  # Changed from 31 to 45 to avoid conflict
            # Note: multiply (33) is handled by stray comment detection above
            (35, ["lparen"], TokenType.LPAREN),
            (36, ["rparen"], TokenType.RPAREN),
            (37, ["lbrace"], TokenType.LBRACE),
            (38, ["rbrace"], TokenType.RBRACE),
            (39, ["lbracket"], TokenType.LBRACKET),
            (40, ["rbracket"], TokenType.RBRACKET),
            (41, ["colon"], TokenType.COLON),
            (42, ["comma"], TokenType.COMMA),
            (43, ["semicolon"], TokenType.SEMICOLON),
            (46, ["modulo"], TokenType.MODULO),  # Add this line
        ]
        
        for state_num, char_cats, token_type in single_tokens:
            add_transition(0, char_cats, state_num)
            self.accepting_states[state_num] = token_type
        
        # === WHITESPACE ===
        add_transition(0, ["whitespace"], 100)
        add_transition(100, ["whitespace"], 100)
        self.accepting_states[100] = TokenType.WHITESPACE
        
        add_transition(0, ["newline"], 101)
        self.accepting_states[101] = TokenType.NEWLINE

    def _init_keywords_and_builtins(self):
        """Initialize keyword and built-in mappings based on assignment EBNF"""
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
            "int": TokenType.TYPE_INT,
            "float": TokenType.TYPE_FLOAT,
            "bool": TokenType.TYPE_BOOL,
            "colour": TokenType.TYPE_COLOUR,
            "true": TokenType.TRUE,
            "false": TokenType.FALSE,
        }
        
        # Built-ins (CORRECTED to match assignment examples)
        self.builtins = {
            "__print": TokenType.BUILTIN_PRINT,
            "__delay": TokenType.BUILTIN_DELAY,
            "__write": TokenType.BUILTIN_WRITE,
            "__write_box": TokenType.BUILTIN_WRITE_BOX,
            "__randi": TokenType.BUILTIN_RANDI,           # FIXED: __randi not __random_int
            "__read": TokenType.BUILTIN_READ,
            "__width": TokenType.BUILTIN_WIDTH,
            "__height": TokenType.BUILTIN_HEIGHT,
            "__clear": TokenType.BUILTIN_CLEAR,
        }

    def tokenize(self, text):
        tokens = []
        pos = 0
        line = 1
        col = 1
        text_len = len(text)

        while pos < text_len:
            start_pos = pos
            start_line = line
            start_col = col

            state = 0
            last_state = 0
            last_accepting_state = -1
            last_accepting_pos = pos

            while pos < text_len:
                char = text[pos]
                char_category = self._categorize_char(char)
                char_cat_index = self.cat_map[char_category]

                next_state = self.Tx[state][char_cat_index]

                if next_state == -1:
                    break

                last_state = next_state
                state = next_state
                pos += 1

                if state in self.accepting_states:
                    last_accepting_state = state
                    last_accepting_pos = pos

            if last_accepting_state != -1:
                lexeme = text[start_pos:last_accepting_pos]
                token_type = self.accepting_states[last_accepting_state]
                pos = last_accepting_pos
                token_type = self._refine_token_type(token_type, lexeme)

                if (token_type not in [TokenType.WHITESPACE, TokenType.NEWLINE, 
                      TokenType.LINECOMMENT, TokenType.BLOCKCOMMENT] 
    or self.debug):
                    tokens.append(Token(token_type, lexeme, start_line, start_col))

                for i in range(start_pos, last_accepting_pos):
                    if text[i] == '\n':
                        line += 1
                        col = 1
                    else:
                        col += 1
            else:
                error_char = text[start_pos] if start_pos < text_len else ""
                error_type = self._determine_error_type(text, start_pos, last_state)
                tokens.append(Token(error_type, error_char, start_line, start_col))
                pos = start_pos + 1
                if error_char == '\n':
                    line += 1
                    col = 1
                else:
                    col += 1

        tokens.append(Token(TokenType.END, "", line, col))
        return tokens


    def _determine_error_type(self, text, error_pos, state):
        # Handle new error states
        if state == 30:
            return TokenType.ERROR_INVALID_FLOAT
        if state == 32:
            return TokenType.ERROR_NESTED_COMMENT
        if state == 34:
            return TokenType.ERROR_STRAY_COMMENT_CLOSE

        # If we errored while inside a block comment (states 27 or 28), it's unterminated
        if state in (27, 28, 31):  # Added state 31 for unterminated comments
            return TokenType.ERROR_UNTERMINATED_COMMENT

        if error_pos >= len(text):
            # Special case: if we end in a comment state, it's unterminated
            if state in (27, 28, 31):
                return TokenType.ERROR_UNTERMINATED_COMMENT
            return TokenType.ERROR

        remaining = text[error_pos:]

        # A lone '#' or malformed colour start → invalid colour
        if remaining.startswith('#'):
            return TokenType.ERROR_INVALID_COLOUR

        # A dot with no digits afterward → invalid float
        if state == 6:
            return TokenType.ERROR_INVALID_FLOAT

        return TokenType.ERROR


    def _refine_token_type(self, base_type, lexeme):
        """Refine token type based on lexeme (keywords/builtins) and validate colour literals."""
        # ——— Colour-literal validation ———
        if base_type == TokenType.COLOUR_LITERAL:
            # Must be exactly '#' plus six hex digits
            if len(lexeme) != 7 or any(c not in '0123456789ABCDEFabcdef' for c in lexeme[1:]):
                return TokenType.ERROR_INVALID_COLOUR

        # ——— Keyword/Builtin refinement ———
        if base_type == TokenType.IDENTIFIER:
            if lexeme in self.keywords:
                return self.keywords[lexeme]
            if lexeme in self.builtins:
                return self.builtins[lexeme]

        return base_type

    def report_errors(self, tokens):
        """Report lexical errors with descriptive messages"""
        error_msgs = {
            TokenType.ERROR_INVALID_FLOAT: "Invalid float literal",
            TokenType.ERROR_INVALID_COLOUR: "Invalid colour literal", 
            TokenType.ERROR_UNTERMINATED_COMMENT: "Unterminated block comment",
            TokenType.ERROR_NESTED_COMMENT: "Nested block comment",
            TokenType.ERROR_STRAY_COMMENT_CLOSE: "Stray '*/' outside comment",
        }
        errors = [t for t in tokens if t.type.name.startswith("ERROR")]
        if errors:
            print(f"Lexical Analysis Failed: {len(errors)} error(s) found")
            for error in errors:
                msg = error_msgs.get(error.type, f"Unexpected character '{error.lexeme}'")
                print(f"  Line {error.line}, Column {error.col}: {msg}")
            return False
        return True

    def print_transition_table(self):
        """Debug helper: print the transition table"""
        print("DFA Transition Table:")
        print("State\\Category", end="")
        for cat in self.categories:
            print(f"\t{cat[:8]}", end="")
        print()
        
        for state in sorted(self.Tx.keys()):
            print(f"State {state:2d}", end="")
            for cat_idx in range(len(self.categories)):
                next_state = self.Tx[state][cat_idx]
                if next_state == -1:
                    print(f"\t-", end="")
                else:
                    print(f"\t{next_state}", end="")
            if state in self.accepting_states:
                print(f"\t[{self.accepting_states[state].name}]")
            else:
                print()
