"""
Simple Array Test - Just compile and print PArIR code
"""

def test_draw_pattern():
    """Compile draw_pattern function and print PArIR output"""
    
    # Test program
    parl_code = """
    fun color() -> colour
    {
        return  (16777215 - __randi 16777215) as colour;
    }

    fun cc(x:int, y:int, iter:int) -> bool
    {
        __print x;
        __print y;
        __print iter;

        while (iter > 0) {
            let c:colour = color();
            let w:int = __randi __width;
            let h:int = __randi __height;

            __write w, h, c;

            iter = iter - 1;
        }

        return true;
    }

    let a:bool = cc(0, 0, 100000);
    __delay 1000;

"""
    
    try:
        # Import compiler components
        from lexer import FSALexer
        from parser.parser import PArLParser
        from semantic_analyzer import SemanticAnalyzer
        
        # Try different import paths for code generator
        try:
            from code_generator.code_generator import PArIRGenerator
        except ImportError:
            from code_generator import PArIRGenerator
        
        # Compile
        lexer = FSALexer()
        tokens = lexer.tokenize(parl_code)
        lexer.report_errors(tokens)
        
        parser = PArLParser(tokens=tokens)
        ast = parser.parse()
        
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        
        generator = PArIRGenerator()
        instructions = generator.generate(ast)
        
        # Print PArIR code
        for instr in instructions:
            print(instr)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_draw_pattern()