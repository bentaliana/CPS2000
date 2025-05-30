from lexer import FSALexer
from parser.parser import PArLParser
from semantic_analyzer import SemanticAnalyzer
from code_generator.code_generator import PArIRGenerator
import traceback

def debug_parl_compilation(source_code, test_name="Debug Test"):
    """
    Debug function that shows the complete compilation pipeline
    with intermediate results for lexer, parser, semantic analyzer, and code generator
    """
    print(f"\n{'='*80}")
    print(f"DEBUG TEST: {test_name}")
    print(f"{'='*80}")
    
    print("Source code:")
    print("-" * 40)
    for i, line in enumerate(source_code.strip().split('\n'), 1):
        print(f"{i:2}: {line}")
    print()

    # ===== STEP 1: LEXICAL ANALYSIS =====
    print("1. LEXICAL ANALYSIS")
    print("-" * 30)
    
    lexer = FSALexer()
    tokens = lexer.tokenize(source_code)
    
    print(f"Tokens generated: {len(tokens)}")
    print("Token stream:")
    for i, token in enumerate(tokens):
        if token.type.name not in ['WHITESPACE', 'NEWLINE', 'LINECOMMENT', 'BLOCKCOMMENT']:
            print(f"  {i:2}: {token.type.name:15} '{token.lexeme}' (line {token.line}, col {token.col})")
    
    # Check for lexical errors
    lexical_success = lexer.report_errors(tokens)
    if not lexical_success:
        print("❌ Lexical analysis failed!")
        return {
            'success': False,
            'error': "Lexical analysis failed!"
        }
    print("✅ Lexical analysis passed!")
    print()
    
    # ===== STEP 2: PARSING =====
    print("2. PARSING")
    print("-" * 30)
    
    parser = PArLParser(tokens)
    ast = parser.parse()
    
    print("Generated AST:")
    print(str(ast))
    
    # Check for parsing errors
    parsing_success = parser.report_errors()
    if not parsing_success:
        print("❌ Parsing failed!")
        return {
            'success': False,
            'error': "Parsing failed!"
        }
    print("✅ Parsing successful!")
    print()
    
    # ===== STEP 3: SEMANTIC ANALYSIS =====
    print("3. SEMANTIC ANALYSIS")
    print("-" * 30)
    
    semantic_analyzer = SemanticAnalyzer()
    semantic_success = semantic_analyzer.analyze(ast)
    
    if not semantic_success:
        semantic_analyzer.report_errors()
        print("❌ Semantic analysis failed!")
        return {
            'success': False,
            'error': "Semantic analysis failed!"
        }
    print("✅ Semantic analysis passed!")
    print()
    
    # ===== STEP 4: CODE GENERATION =====
    print("4. CODE GENERATION")
    print("-" * 30)
    
    code_generator = PArIRGenerator(debug=False)  # Set to True for detailed instruction generation logs
    parir_code = code_generator.generate(ast)
    
    print(f"Code generation successful! {len(parir_code)} instructions generated")
    print()
    print("Generated PArIR code:")
    print("-" * 40)
    for i, instruction in enumerate(parir_code):
        print(f"{i:2}: {instruction}")
    
    print()
    print("✅ Compilation pipeline completed successfully!")
    
    return {
        'tokens': tokens,
        'ast': ast,
        'parir_code': parir_code,
        'success': True
    }


# Test your function
if __name__ == "__main__":
    test_source = """
fun color() -> colour
{
    return (16777215 - __randi 16777215) as colour;
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
    
    result = debug_parl_compilation(test_source, "Function with While Loop")
    
    if result['success']:
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"✅ Lexical Analysis: {len(result['tokens'])} tokens")
        print("✅ Parsing: AST generated successfully")
        print("✅ Semantic Analysis: No errors")
        print(f"✅ Code Generation: {len(result['parir_code'])} instructions")
        
        print("\nFinal PArIR Code:")
        print("-" * 40)
        for instruction in result['parir_code']:
            print(instruction)
    else:
        print(f"\n❌ Compilation failed: {result['error']}")