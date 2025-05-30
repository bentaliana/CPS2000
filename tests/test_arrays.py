"""
Integrated PArL Compiler Test Program
Tests all aspects of the compilation pipeline with systematic verification
"""

from lexer import FSALexer
from parser.parser import PArLParser
from semantic_analyzer import SemanticAnalyzer
from code_generator.code_generator import PArIRGenerator
import traceback

def compile_and_debug(source_code, test_name="Test", show_details=False):
    """
    Complete compilation pipeline with optional detailed output
    Returns success status and generated PArIR code
    """
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    
    if show_details:
        print("Source code:")
        print("-" * 40)
        for i, line in enumerate(source_code.strip().split('\n'), 1):
            print(f"{i:2}: {line}")
        print()

    try:
        # Step 1: Lexical Analysis
        lexer = FSALexer()
        tokens = lexer.tokenize(source_code)
        
        if show_details:
            print(f"1. LEXICAL ANALYSIS: {len(tokens)} tokens generated")
        
        if not lexer.report_errors(tokens):
            print("❌ Lexical analysis failed!")
            return False, None
        
        # Step 2: Parsing
        parser = PArLParser(tokens)
        ast = parser.parse()
        
        if show_details:
            print(f"2. PARSING: AST generated successfully")
        
        if not parser.report_errors():
            print("❌ Parsing failed!")
            return False, None
        
        # Step 3: Semantic Analysis
        analyzer = SemanticAnalyzer()
        
        if not analyzer.analyze(ast):
            print("❌ Semantic analysis failed!")
            analyzer.report_errors()
            return False, None
        
        if show_details:
            print(f"3. SEMANTIC ANALYSIS: Passed")
        
        # Step 4: Code Generation
        generator = PArIRGenerator(debug=False)
        parir_code = generator.generate(ast)
        
        print(f"✅ Compilation successful! {len(parir_code)} instructions generated")
        
        return True, parir_code
        
    except Exception as e:
        print(f"❌ Compilation failed: {e}")
        if show_details:
            traceback.print_exc()
        return False, None


def analyze_parir_output(parir_code, test_name):
    """Analyze PArIR code for key verification points"""
    print(f"\nAnalysis of {test_name}:")
    print("-" * 40)
    
    # Find main frame allocation
    main_frame_size = None
    for i, instr in enumerate(parir_code):
        if instr == "oframe" and i > 4:  # Skip the initial .main setup
            if i > 0 and parir_code[i-1].startswith("push "):
                main_frame_size = parir_code[i-1].replace("push ", "")
                print(f"📋 Main frame allocation: {main_frame_size}")
                break
    
    # Find variable storage instructions
    variable_indices = []
    for i, instr in enumerate(parir_code):
        if instr == "st" and i >= 2:
            if (parir_code[i-2].startswith("push ") and 
                parir_code[i-1].startswith("push ")):
                var_index = parir_code[i-2].replace("push ", "")
                frame_level = parir_code[i-1].replace("push ", "")
                if var_index.isdigit() and frame_level == "0":
                    variable_indices.append(var_index)
    
    if variable_indices:
        print(f"📋 Variable indices: {', '.join(variable_indices)}")
    
    # Find function calls
    function_calls = []
    for i, instr in enumerate(parir_code):
        if instr == "call" and i >= 2:
            if parir_code[i-1].startswith("push ."):
                func_name = parir_code[i-1].replace("push .", "")
                param_count = parir_code[i-2].replace("push ", "") if parir_code[i-2].startswith("push ") else "?"
                function_calls.append(f"{func_name}({param_count} params)")
    
    if function_calls:
        print(f"📋 Function calls: {', '.join(function_calls)}")
    
    print()


def run_test_suite():
    """Run comprehensive test suite"""
    print("PArL COMPILER TEST SUITE")
    print("=" * 80)
    
    # Test 1: Original problematic case
    test1_source = """
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
    
    success, parir = compile_and_debug(test1_source, "Original 3-Parameter Case")
    if success:
        analyze_parir_output(parir, "3-parameter function")
        print("Expected: frame=3, variable 'a' at index 2")
        
        print("\nGenerated PArIR:")
        for i, instr in enumerate(parir):
            print(f"{i:2}: {instr}")
    
    # Test 2: Frame allocation verification
    test_cases = [
        ("1 var, 1 param → frame=1, var at index 0", """
fun f(x:int) -> int { return x; }
let a:int = f(42);
"""),
        ("1 var, 2 param → frame=2, var at index 1", """
fun f(x:int, y:int) -> int { return x + y; }
let a:int = f(1, 2);
"""),
        ("2 var, 1 param → frame=2, vars at index 0,1", """
fun f(x:int) -> int { return x; }
let a:int = f(42);
let b:int = 24;
"""),
        ("Simple while loop", """
let i:int = 3;
while (i > 0) {
    __print i;
    i = i - 1;
}
"""),
        ("Built-in functions", """
let w:int = __width;
let h:int = __height;
__write_box 0, 0, w, h, #ff0000;
""")
    ]
    
    for description, source in test_cases:
        success, parir = compile_and_debug(source, description)
        if success:
            analyze_parir_output(parir, description)
    
    # Test 3: Type casting verification
    casting_test = """
let x:int = 42;
let f:float = x as float;
let c:colour = 255 as colour;
__print f as int;
"""
    
    success, parir = compile_and_debug(casting_test, "Type Casting")
    if success:
        analyze_parir_output(parir, "type casting")


def quick_test(source_code, name="Quick Test"):
    """Quick test function for interactive testing"""
    success, parir = compile_and_debug(source_code, name, show_details=True)
    if success:
        print("\nGenerated PArIR:")
        print("-" * 40)
        for i, instr in enumerate(parir):
            print(f"{i:2}: {instr}")
        analyze_parir_output(parir, name)
    return success, parir


def interactive_mode():
    """Interactive testing mode"""
    print("\n" + "="*60)
    print("INTERACTIVE MODE")
    print("="*60)
    print("Enter PArL code (type 'END' on a new line to finish):")
    print("Type 'exit' to quit, 'suite' to run full test suite")
    
    while True:
        print("\n> ", end="")
        command = input().strip()
        
        if command.lower() == 'exit':
            break
        elif command.lower() == 'suite':
            run_test_suite()
            continue
        elif command.lower() == 'end':
            continue
        
        # Collect multi-line input
        lines = [command] if command else []
        while True:
            line = input()
            if line.strip() == 'END':
                break
            lines.append(line)
        
        if lines:
            source = '\n'.join(lines)
            quick_test(source, "Interactive Test")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "suite":
            run_test_suite()
        elif command == "interactive":
            interactive_mode()
        elif command == "original":
            # Run just the original problematic case
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
            success, parir = compile_and_debug(test_source, "Original Case", show_details=True)
            if success:
                print("\nFinal PArIR Code:")
                print("-" * 40)
                for instr in parir:
                    print(instr)
                    
                print("\n" + "="*60)
                print("VERIFICATION")
                print("="*60)
                print("Expected output should have:")
                print("- Main frame: push 3")
                print("- Variable 'a' storage: push 2, push 0, st")
                print("- Correct jump calculations in while loop")
                analyze_parir_output(parir, "verification")
        else:
            print("Unknown command. Available commands:")
            print("  suite      - Run full test suite")
            print("  interactive - Enter interactive mode")
            print("  original   - Test original problematic case")
    else:
        print("PArL Compiler Test Program")
        print("=" * 40)
        print("Usage:")
        print("  python test_program.py suite        - Run all tests")
        print("  python test_program.py interactive  - Interactive mode")
        print("  python test_program.py original     - Test original case")
        print("\nRunning original test case by default...")
        
        # Default: run the original test case
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
        success, parir = compile_and_debug(test_source, "Original Problematic Case", show_details=True)
        if success:
            print("\nGenerated PArIR Code:")
            print("-" * 40)
            for instr in parir:
                print(instr)
            analyze_parir_output(parir, "original case")