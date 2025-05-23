from lexer import FSALexer, TokenType
# Test the lexer
if __name__ == "__main__":
    test_program = """
    /* This function takes two integers and return true if
    * the first argument is greater than the second.
    * Otherwise it returns false. */
    fun XGreaterY(x:int, y:int) -> bool {
        let ans:bool = true;
        if (y > x) { ans = false; }
        return ans;
    }

    // Same functionality as function above but using less code
    fun XGreaterY_2(x:int, y:int) -> bool {
    return x > y;
    }

    """

    lexer = FSALexer()
    tokens = lexer.tokenize(test_program)
    
    # Check for errors
    if lexer.report_errors(tokens):
        print("Lexical analysis completed successfully!")
    
    print(f"\nGenerated {len([t for t in tokens if t.type != TokenType.END])} tokens:")
    for token in tokens:  # Show first 50 tokens
        if token.type != TokenType.END:
            print(f"  {token}")
