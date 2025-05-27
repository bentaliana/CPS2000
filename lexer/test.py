from lexer import FSALexer, TokenType

if __name__ == "__main__":
    lexer = FSALexer()
    
    # Read the whole file in one go
    with open("lexer/valid_test.parl", "r", encoding="utf-8") as f:
        source = f.read()

    # Tokenize the entire source at once
    tokens = lexer.tokenize(source)

    # Report any errors
    if lexer.report_errors(tokens):
        print("Lexical analysis completed successfully!")

    # Filter out the END token and any comments/whitespace if you like
    real_tokens = [t for t in tokens if t.type not in
                   (TokenType.END, TokenType.WHITESPACE,
                    TokenType.LINECOMMENT, TokenType.NEWLINE)]
    
    print(f"\nGenerated {len(real_tokens)} tokens:")
    for t in real_tokens:
        print(f"  {t}")
