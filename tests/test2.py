from semantic_analyzer import SemanticAnalyzer
from lexer import FSALexer
from parser.parser import PArLParser
from code_generator.code_generator import PArIRGenerator

"""
Debug Test - Show all compilation stages for troubleshooting
"""

def debug_compilation():
    """Debug compilation with detailed output at each stage"""
    
    # Test program
    parl_code = """
fun color() -> colour {
    return (16777215 - __randi 16777215) as colour;
}

fun cc(x:int, y:int, iter:int) -> bool {
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
        print("=" * 80)
        print("STAGE 1: LEXICAL ANALYSIS")
        print("=" * 80)
        
        lexer = FSALexer()
        tokens = lexer.tokenize(parl_code)
        
        if not lexer.report_errors(tokens):
            print("❌ LEXICAL ANALYSIS FAILED")
            return
        
        print("✅ LEXICAL ANALYSIS PASSED")
        print(f"Generated {len(tokens)} tokens")
        
        # Show first 20 tokens for debugging
        print("\nFirst 20 tokens:")
        for i, token in enumerate(tokens[:20]):
            print(f"  {i:2}: {token.type.name:15} '{token.lexeme}'")
        if len(tokens) > 20:
            print(f"  ... and {len(tokens) - 20} more tokens")
        
        print("\n" + "=" * 80)
        print("STAGE 2: PARSING")
        print("=" * 80)
        
        parser = PArLParser(tokens=tokens)
        ast = parser.parse()
        
        if parser.has_errors():
            print("❌ PARSING FAILED")
            parser.report_errors()
            return
        
        print("✅ PARSING PASSED")
        print("\nAST Structure:")
        print(str(ast))
        
        print("\n" + "=" * 80)
        print("STAGE 3: SEMANTIC ANALYSIS")
        print("=" * 80)
        
        analyzer = SemanticAnalyzer()
        
        if not analyzer.analyze(ast):
            print("❌ SEMANTIC ANALYSIS FAILED")
            analyzer.report_errors()
            return
        
        print("✅ SEMANTIC ANALYSIS PASSED")
        print("Symbol table contents:")
        print(f"  Functions: {list(analyzer.symbol_table.functions.keys())}")
        
        print("\n" + "=" * 80)
        print("STAGE 4: CODE GENERATION")
        print("=" * 80)
        
        generator = PArIRGenerator(debug=True)  # Enable debug output
        instructions = generator.generate(ast)
        
        print(f"✅ CODE GENERATION COMPLETED")
        print(f"Generated {len(instructions)} instructions")
        
        print("\n" + "=" * 80)
        print("GENERATED PArIR CODE")
        print("=" * 80)
        
        for i, instr in enumerate(instructions):
            print(f"{i:2}: {instr}")
        
        print("\n" + "=" * 80)
        print("COMPARISON WITH EXPECTED")
        print("=" * 80)
        
        expected_instructions = [
            ".main", "push 4", "jmp", "halt", "push 3", "oframe",
            "push #PC+10", "jmp", ".color", "push 0", "alloc",
            "push 16777215", "irnd", "push 16777215", "sub", "ret",
            "push #PC+51", "jmp", ".cc", "push 3", "alloc"
        ]
        
        print("Checking first 20 instructions:")
        for i, (actual, expected) in enumerate(zip(instructions[:20], expected_instructions)):
            match = "✅" if actual == expected else "❌"
            print(f"{i:2}: {match} Got: '{actual}' | Expected: '{expected}'")
        
        # Identify specific differences
        print("\n" + "=" * 80)
        print("PROBLEM ANALYSIS")
        print("=" * 80)
        
        problems = []
        
        # Check main frame allocation
        if len(instructions) > 4 and instructions[4] != "push 3":
            problems.append(f"Main frame allocation: got '{instructions[4]}', expected 'push 3'")
        
        # Check function parameter handling
        cc_func_start = None
        for i, instr in enumerate(instructions):
            if instr == ".cc":
                cc_func_start = i
                break
        
        if cc_func_start and cc_func_start + 1 < len(instructions):
            alloc_instr = instructions[cc_func_start + 1]
            if alloc_instr != "push 3":
                problems.append(f"Function cc allocation: got '{alloc_instr}', expected 'push 3'")
        
        # Check variable access patterns
        frame_level_issues = []
        for i, instr in enumerate(instructions):
            if "push [" in instr and ":1]" in instr:
                frame_level_issues.append(f"Line {i}: {instr} (should probably be :0])")
        
        if frame_level_issues:
            problems.append("Frame level issues found:")
            for issue in frame_level_issues:
                problems.append(f"  {issue}")
        
        if problems:
            print("🔍 IDENTIFIED PROBLEMS:")
            for problem in problems:
                print(f"  • {problem}")
        else:
            print("✅ No obvious problems found in generated code")
        
        return True
        
    except Exception as e:
        print(f"💥 COMPILATION ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 DEBUGGING COMPILATION PIPELINE")
    print("This will show detailed output for each compilation stage\n")
    
    success = debug_compilation()
    
    if success:
        print("\n🎯 DEBUGGING COMPLETE")
        print("Check the output above to identify specific issues")
    else:
        print("\n💀 DEBUGGING FAILED")
        print("Fix the errors shown above and try again")