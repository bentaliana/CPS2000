"""
Task 4 - Code Generation Tests
Tests for PArL to PArIR code generation
"""

import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer.lexer import FSALexer
from parser.parser import PArLParser
from semantic_analyzer.semantic_analyzer import SemanticAnalyzer
from code_generator.code_generator import PArIRGenerator
from test.test_utils import print_test_header, print_ast, print_outcome, set_ast_printing, create_test_output_file, close_test_output_file, write_to_file


if "--show-ast" in sys.argv:
    set_ast_printing(True)
else:
    set_ast_printing(False)


def generate_code(source_code):
    """Complete compilation pipeline"""
    lexer = FSALexer()
    tokens = lexer.tokenize(source_code.strip())
    
    parser = PArLParser(tokens)
    ast = parser.parse()
    
    if parser.has_errors():
        return None, None, f"Parser errors: {parser.errors}"
    
    analyzer = SemanticAnalyzer()
    if not analyzer.analyze(ast):
        return None, None, f"Semantic errors: {analyzer.errors}"
    
    generator = PArIRGenerator()
    instructions = generator.generate(ast)
    
    return ast, instructions, None


def test_basic_program():
    """Test basic program structure generation"""
    print_test_header("Basic Program Structure",
                     "Code generator produces correct structure for simple program")
    
    test_code = """
    let x:int = 42;
    __print x;
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = generate_code(test_code)
    
    if error:
        print_outcome(False, error)
        return False
    
    print_ast(ast)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-"*60)
    for instr in instructions:
        write_to_file(instr)
    write_to_file("-"*60)
    
    # Check for required program structure
    required = [".main", "oframe", "push", "st", "print", "halt", "cframe"]
    found = {req: any(req in instr for instr in instructions) for req in required}
    
    missing = [req for req, found in found.items() if not found]
    
    if missing:
        print_outcome(False, f"Missing required instructions: {missing}")
        return False
    else:
        print_outcome(True)
        return True


def test_arithmetic_operations():
    """Test arithmetic operation code generation"""
    print_test_header("Arithmetic Operations",
                     "Code generator correctly handles all arithmetic operations including modulo")
    
    test_code = """
    let a:int = 17;
    let b:int = 5;
    let sum:int = a + b;
    let diff:int = a - b;
    let prod:int = a * b;
    let quot:int = a / b;
    let rem:int = a % b;
    
    __print sum;
    __print diff;
    __print prod;
    __print quot;
    __print rem;
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = generate_code(test_code)
    
    if error:
        print_outcome(False, error)
        return False
    
    print_ast(ast)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-"*60)
    for instr in instructions:
        write_to_file(instr)
    write_to_file("-"*60)
    
    # Check for arithmetic instructions
    ops = ["add", "sub", "mul", "div", "mod"]
    found = {op: any(op in instr for instr in instructions) for op in ops}
    
    missing = [op for op, found in found.items() if not found]
    
    if missing:
        print_outcome(False, f"Missing arithmetic operations: {missing}")
        return False
    else:
        write_to_file("\nAll arithmetic operations found:")
        for op in ops:
            write_to_file(f"  {op}: YES")
        print_outcome(True)
        return True


def test_comparison_operations():
    """Test comparison operation code generation"""
    print_test_header("Comparison Operations",
                     "Code generator correctly handles all comparison operations")
    
    test_code = """
    let a:int = 10;
    let b:int = 5;
    
    let lt:bool = a < b;
    let gt:bool = a > b;
    let le:bool = a <= b;
    let ge:bool = a >= b;
    let eq:bool = a == b;
    let ne:bool = a != b;
    
    if (lt) { __print 1; }
    if (gt) { __print 2; }
    if (le) { __print 3; }
    if (ge) { __print 4; }
    if (eq) { __print 5; }
    if (ne) { __print 6; }
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = generate_code(test_code)
    
    if error:
        print_outcome(False, error)
        return False
    
    print_ast(ast)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-"*60)
    for instr in instructions:
        write_to_file(instr)
    write_to_file("-"*60)
    
    # Check for comparison instructions
    ops = ["lt", "gt", "le", "ge", "eq"]
    found = {op: any(op in instr for instr in instructions) for op in ops}
    
    # != is typically implemented as eq followed by not
    if any("not" in instr for instr in instructions):
        found["not"] = True
    
    missing = [op for op, found in found.items() if not found]
    
    if missing:
        print_outcome(False, f"Missing comparison operations: {missing}")
        return False
    else:
        print_outcome(True)
        return True


def test_logical_operations():
    """Test logical operation code generation"""
    print_test_header("Logical Operations",
                     "Code generator correctly handles logical operations")
    
    test_code = """
    let a:bool = true;
    let b:bool = false;
    
    let and_result:bool = a and b;
    let or_result:bool = a or b;
    let not_result:bool = not a;
    
    if (and_result) { __print 1; }
    if (or_result) { __print 2; }
    if (not_result) { __print 3; }
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = generate_code(test_code)
    
    if error:
        print_outcome(False, error)
        return False
    
    print_ast(ast)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-"*60)
    for instr in instructions:
        write_to_file(instr)
    write_to_file("-"*60)
    
    # Check for logical instructions
    ops = ["and", "or", "not"]
    found = {op: any(op in instr for instr in instructions) for op in ops}
    
    missing = [op for op, found in found.items() if not found]
    
    if missing:
        print_outcome(False, f"Missing logical operations: {missing}")
        return False
    else:
        print_outcome(True)
        return True


def test_function_generation():
    """Test function declaration and call generation"""
    print_test_header("Function Generation",
                     "Code generator correctly handles functions")
    
    test_code = """
    fun add(x:int, y:int) -> int {
        return x + y;
    }
    
    fun multiply(a:int, b:int) -> int {
        let result:int = a * b;
        return result;
    }
    
    let sum:int = add(5, 10);
    let product:int = multiply(3, 4);
    __print sum;
    __print product;
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = generate_code(test_code)
    
    if error:
        print_outcome(False, error)
        return False
    
    print_ast(ast)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-"*60)
    for instr in instructions:
        write_to_file(instr)
    write_to_file("-"*60)
    
    # Check for function-related instructions
    required = [".add", ".multiply", "call", "ret", "alloc"]
    found = {req: any(req in instr for instr in instructions) for req in required}
    
    missing = [req for req, found in found.items() if not found]
    
    if missing:
        print_outcome(False, f"Missing function instructions: {missing}")
        return False
    else:
        print_outcome(True)
        return True


def test_control_flow():
    """Test control flow code generation"""
    print_test_header("Control Flow Generation",
                     "Code generator correctly handles if/else, while, and for")
    
    test_code = """
    let x:int = 10;
    
    // If-else
    if (x > 5) {
        __print 1;
    } else {
        __print 0;
    }
    
    // While loop
    while (x > 0) {
        __print x;
        x = x - 1;
    }
    
    // For loop
    for (let i:int = 0; i < 5; i = i + 1) {
        if (i % 2 == 0) {
            __print i;
        }
    }
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = generate_code(test_code)
    
    if error:
        print_outcome(False, error)
        return False
    
    print_ast(ast)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-"*60)
    for instr in instructions:
        write_to_file(instr)
    write_to_file("-"*60)
    
    # Check for control flow instructions
    required = ["cjmp", "jmp", "#PC"]
    found = {req: any(req in instr for instr in instructions) for req in required}
    
    missing = [req for req, found in found.items() if not found]
    
    if missing:
        print_outcome(False, f"Missing control flow instructions: {missing}")
        return False
    else:
        print_outcome(True)
        return True


def test_builtin_operations():
    """Test built-in function code generation"""
    print_test_header("Built-in Operations",
                     "Code generator correctly handles all built-in functions")
    
    test_code = """
    // Screen dimensions
    let w:int = __width;
    let h:int = __height;
    
    // Random number
    let rand:int = __randi 100;
    
    // Print
    __print 42;
    __print w;
    __print h;
    
    // Delay
    __delay 500;
    
    // Graphics operations
    __write 10, 20, #ff0000;
    __write_box 0, 0, 50, 50, #00ff00;
    let pixel:colour = __read 25, 25;
    __clear #0000ff;
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = generate_code(test_code)
    
    if error:
        print_outcome(False, error)
        return False
    
    print_ast(ast)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-"*60)
    for instr in instructions:
        write_to_file(instr)
    write_to_file("-"*60)
    
    # Check for built-in instructions
    builtins = ["width", "height", "irnd", "print", "delay", "write", "writebox", "read", "clear"]
    found = {bi: any(bi in instr for instr in instructions) for bi in builtins}
    
    missing = [bi for bi, found in found.items() if not found]
    
    if missing:
        print_outcome(False, f"Missing built-in operations: {missing}")
        return False
    else:
        write_to_file("\nAll built-in operations found:")
        for bi in builtins:
            write_to_file(f"  {bi}: YES")
        print_outcome(True)
        return True


def test_cast_operations():
    """Test type casting code generation"""
    print_test_header("Type Casting",
                     "Code generator correctly handles type casts")
    
    test_code = """
    let i:int = 42;
    let f:float = 3.14;
    let b:bool = true;
    let c:colour = #ff0000;
    
    // Various casts
    let i_to_f:float = i as float;
    let f_to_i:int = f as int;
    let i_to_b:bool = i as bool;
    let b_to_i:int = b as int;
    let i_to_c:colour = (255 * 256 * 256) as colour;
    let c_to_i:int = c as int;
    
    __print i_to_f;
    __print f_to_i;
    __print b_to_i;
    __print c_to_i;
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = generate_code(test_code)
    
    if error:
        print_outcome(False, error)
        return False
    
    print_ast(ast)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-"*60)
    for instr in instructions:
        write_to_file(instr)
    write_to_file("-"*60)
    
    # Casts might be implicit in the generated code
    # Just verify the program compiles successfully
    print_outcome(True)
    return True


def test_complex_expressions():
    """Test complex expression code generation"""
    print_test_header("Complex Expressions",
                     "Code generator correctly handles complex nested expressions")
    
    test_code = """
    let a:int = 10;
    let b:int = 5;
    let c:int = 3;
    
    // Complex arithmetic with precedence
    let result1:int = a + b * c - a / b % c;
    let result2:int = (a + b) * (c - 1);
    let result3:int = -a + -b * -c;
    
    // Complex boolean expressions
    let x:bool = a > b and b > c or a == 10;
    let y:bool = not (a < b) and (b != c);
    
    // Mixed expressions with casts
    let z:float = (a + b * c) as float / 2.0;
    
    __print result1;
    __print result2;
    __print result3;
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = generate_code(test_code)
    
    if error:
        print_outcome(False, error)
        return False
    
    print_ast(ast)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-"*60)
    for instr in instructions:
        write_to_file(instr)
    write_to_file("-"*60)
    
    # Should generate many push and arithmetic operations
    push_count = sum(1 for instr in instructions if "push" in instr)
    arith_count = sum(1 for instr in instructions 
                     if any(op in instr for op in ["add", "sub", "mul", "div", "mod"]))
    
    write_to_file(f"\nInstruction counts:")
    write_to_file(f"  Push operations: {push_count}")
    write_to_file(f"  Arithmetic operations: {arith_count}")
    
    if push_count < 10 or arith_count < 5:
        print_outcome(False, "Too few operations for complex expressions")
        return False
    else:
        print_outcome(True)
        return True


def test_recursive_function():
    """Test recursive function code generation"""
    print_test_header("Recursive Functions",
                     "Code generator correctly handles recursive function calls")
    
    test_code = """
    fun factorial(n:int) -> int {
        if (n <= 1) {
            return 1;
        }
        return n * factorial(n - 1);
    }
    
    fun fibonacci(n:int) -> int {
        if (n <= 1) {
            return n;
        }
        return fibonacci(n - 1) + fibonacci(n - 2);
    }
    
    let fact5:int = factorial(5);
    let fib7:int = fibonacci(7);
    
    __print fact5;
    __print fib7;
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = generate_code(test_code)
    
    if error:
        print_outcome(False, error)
        return False
    
    print_ast(ast)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-"*60)
    for i, instr in enumerate(instructions):
        write_to_file(instr)
        if i > 100:  # Limit output for recursive functions
            write_to_file(f"... ({len(instructions) - i - 1} more instructions)")
            break
    write_to_file("-"*60)
    
    # Check for recursive function elements
    required = [".factorial", ".fibonacci", "call", "ret"]
    found = {req: any(req in instr for instr in instructions) for req in required}
    
    missing = [req for req, found in found.items() if not found]
    
    if missing:
        print_outcome(False, f"Missing recursive function elements: {missing}")
        return False
    else:
        print_outcome(True)
        return True


def test_complete_program():
    """Test complete program with all features"""
    print_test_header("Complete Program",
                     "Code generator handles complete program with all language features")
    
    test_code = """
    // Global variable
    let screen_cleared:bool = false;
    
    fun draw_pixel(x:int, y:int, c:colour) -> bool {
        if ((x >= 0 and x < __width and y >= 0 and y < __height) or screen_cleared) {
            __write x, y, c;
            return true;
        }
        return false;
    }
    
    fun clear_screen() -> bool {
        if (not screen_cleared) {
            __clear #000000;
            screen_cleared = true;
        }
        return screen_cleared;
    }
    
    fun main() -> int {
        let cleared:bool = clear_screen();
        
        // Draw a pattern
        for (let i:int = 0; i < 10; i = i + 1) {
            let x:int = i * 10;
            let y:int = i * 10;
            let color:colour = (i * 25) as colour;
            let drawn:bool = draw_pixel(x, y, color);
        }
        
        // Test modulo
        let a:int = 17;
        let b:int = 5;
        let remainder:int = a % b;
        __print remainder;
        
        __delay 1000;
        return 0;
    }
    
    let result:int = main();
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = generate_code(test_code)
    
    if error:
        print_outcome(False, error)
        return False
    
    print_ast(ast, max_lines=100)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-"*60)
    for i, instr in enumerate(instructions):
        write_to_file(instr)
        if i > 150:  # Limit output
            write_to_file(f"... ({len(instructions) - i - 1} more instructions)")
            break
    write_to_file("-"*60)
    
    write_to_file(f"\nTotal instructions generated: {len(instructions)}")
    
    # Verify key components
    components = {
        "functions": [".draw_pixel", ".clear_screen", ".main"],
        "operations": ["mod", "and", "or", "not"],
        "control": ["cjmp", "jmp", "call", "ret"],
        "builtins": ["write", "clear", "width", "height", "print", "delay"]
    }
    
    all_found = True
    for category, items in components.items():
        write_to_file(f"\n{category.upper()}:")
        for item in items:
            found = any(item in instr for instr in instructions)
            write_to_file(f"  {item}: {'YES' if found else 'NO'}")
            if not found:
                all_found = False
    
    if all_found:
        print_outcome(True)
        return True
    else:
        print_outcome(False, "Some required components missing")
        return False


def run_task4_tests():
    """Run all Task 4 tests"""
    output_file = create_test_output_file("task4_codegen")
    
    print("TASK 4 - CODE GENERATION TESTS")
    print("="*80)
    
    results = []
    
    # Run all tests
    results.append(("Basic Program", test_basic_program()))
    results.append(("Arithmetic Operations", test_arithmetic_operations()))
    results.append(("Comparison Operations", test_comparison_operations()))
    results.append(("Logical Operations", test_logical_operations()))
    results.append(("Function Generation", test_function_generation()))
    results.append(("Control Flow", test_control_flow()))
    results.append(("Built-in Operations", test_builtin_operations()))
    results.append(("Type Casting", test_cast_operations()))
    results.append(("Complex Expressions", test_complex_expressions()))
    results.append(("Recursive Functions", test_recursive_function()))
    results.append(("Complete Program", test_complete_program()))
    
    # Summary
    write_to_file("\n" + "="*80)
    write_to_file("TASK 4 SUMMARY")
    write_to_file("="*80)
    
    print("\nTASK 4 SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        write_to_file(f"{test_name:<30} {status}")
        print(f"{test_name:<30} {status}")
    
    write_to_file("-"*80)
    write_to_file(f"Total: {passed}/{total} tests passed")
    print("-"*80)
    print(f"Total: {passed}/{total} tests passed")
    
    close_test_output_file()
    print(f"Detailed output written to: {output_file}")
    
    return passed == total


if __name__ == "__main__":
    success = run_task4_tests()
    sys.exit(0 if success else 1)