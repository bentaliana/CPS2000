"""
Task 3 - Semantic Analysis Tests
Tests for type checking and scope management
"""

import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import FSALexer
from parser import PArLParser
from semantic_analyzer import SemanticAnalyzer
from test.test_utils import print_test_header, print_ast, print_outcome, set_ast_printing, create_test_output_file, close_test_output_file, write_to_file


if "--show-ast" in sys.argv:
    set_ast_printing(True)
else:
    set_ast_printing(False)

def analyze_code(code):
    """Helper to analyze code"""
    lexer = FSALexer()
    tokens = lexer.tokenize(code.strip())
    
    parser = PArLParser(tokens)
    ast = parser.parse()
    
    if parser.has_errors():
        return None, None, parser.errors
    
    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(ast)
    
    return ast, success, analyzer.errors


def test_type_checking():
    """Test type checking for all operations"""
    print_test_header("Type Checking",
                     "Semantic analyzer correctly validates types in all operations")
    
    test_code = """
    fun type_test() -> int {
        // Arithmetic operations on compatible types
        let a:int = 10;
        let b:int = 5;
        let c:float = 3.14;
        let d:float = 2.0;
        
        let int_add:int = a + b;
        let int_sub:int = a - b;
        let int_mul:int = a * b;
        let int_div:int = a / b;
        let int_mod:int = a % b;
        
        let float_add:float = c + d;
        let float_sub:float = c - d;
        let float_mul:float = c * d;
        let float_div:float = c / d;
        let float_mod:float = c % d;
        
        // Comparison operations
        let cmp1:bool = a < b;
        let cmp2:bool = a > b;
        let cmp3:bool = a <= b;
        let cmp4:bool = a >= b;
        let cmp5:bool = a == b;
        let cmp6:bool = a != b;
        
        // Logical operations
        let flag1:bool = true;
        let flag2:bool = false;
        let log1:bool = flag1 and flag2;
        let log2:bool = flag1 or flag2;
        let log3:bool = not flag1;
        
        // Unary operations
        let neg_int:int = -a;
        let neg_float:float = -c;
        
        return int_add;
    }
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, success, errors = analyze_code(test_code)
    
    if ast:
        print_ast(ast)
    
    if success:
        write_to_file("\nSemantic analysis passed - all types valid")
        print_outcome(True)
        return True
    else:
        write_to_file(f"\nSemantic errors: {len(errors)}")
        for error in errors:
            write_to_file(f"  - {error}")
        print_outcome(False, "Type checking failed")
        return False


def test_type_errors():
    """Test detection of type errors"""
    print_test_header("Type Error Detection",
                     "Semantic analyzer correctly detects type mismatches")
    
    test_code = """
    let a:int = 10;
    let b:bool = true;
    let c:colour = #ff0000;
    
    // Type mismatches in binary operations
    let error1:int = a + b;
    let error2:int = a % b;
    let error3:bool = b * 5;
    let error4:colour = c + 1;
    
    // Type mismatches in assignments
    a = true;
    b = 42;
    c = 3.14;
    
    // Type mismatches in unary operations
    let error5:int = not a;
    let error6:bool = -b;
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, success, errors = analyze_code(test_code)
    
    if ast:
        print_ast(ast)
    
    if not success and len(errors) > 0:
        write_to_file(f"\nDetected {len(errors)} semantic errors:")
        for error in errors:
            write_to_file(f"  - {error}")
        print_outcome(True, "Correctly detected type errors")
        return True
    else:
        print_outcome(False, "Failed to detect type errors")
        return False


def test_scope_management():
    """Test variable scope management"""
    print_test_header("Scope Management",
                     "Semantic analyzer correctly manages variable scopes")
    
    test_code = """
    // Global scope
    let global_var:int = 100;
    
    fun outer(param1:int) -> int {
        // Function scope
        let local1:int = param1 + global_var;
        
        if (param1 > 0) {
            // Block scope
            let block_var:int = local1 * 2;
            global_var = block_var;  // Can access global
            return block_var;
        } else {
            // Different block scope
            let block_var:bool = false;  // Same name, different scope
            return 0;
        }
    }
    
    fun inner() -> int {
        // Can't access outer's locals
        let local1:float = 3.14;  // Same name as in outer, but different scope
        return global_var;
    }
    
    let result:int = outer(10);
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, success, errors = analyze_code(test_code)
    
    if ast:
        print_ast(ast)
    
    if success:
        write_to_file("\nScope management correct")
        print_outcome(True)
        return True
    else:
        write_to_file(f"\nSemantic errors: {len(errors)}")
        for error in errors:
            write_to_file(f"  - {error}")
        print_outcome(False, "Scope management failed")
        return False


def test_undefined_variables():
    """Test detection of undefined variables"""
    print_test_header("Undefined Variables",
                     "Semantic analyzer detects use of undefined variables")
    
    test_code = """
    fun test() -> int {
        let x:int = y;  // y is undefined
        let z:int = x + undefined_var;  // undefined_var is undefined
        return w;  // w is undefined
    }
    
    let a:int = b;  // b is undefined
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, success, errors = analyze_code(test_code)
    
    if ast:
        print_ast(ast)
    
    if not success and len(errors) > 0:
        write_to_file(f"\nDetected {len(errors)} undefined variable errors:")
        for error in errors:
            write_to_file(f"  - {error}")
        print_outcome(True, "Correctly detected undefined variables")
        return True
    else:
        print_outcome(False, "Failed to detect undefined variables")
        return False


def test_function_validation():
    """Test function declaration and call validation"""
    print_test_header("Function Validation",
                     "Semantic analyzer validates function declarations and calls")
    
    test_code = """
    fun add(x:int, y:int) -> int {
        return x + y;
    }
    
    fun no_return(x:int) -> int {
        let y:int = x + 1;
        // Missing return statement
    }
    
    fun wrong_return(x:int) -> bool {
        return x;  // Wrong return type
    }
    
    fun test_calls() -> int {
        // Valid call
        let result1:int = add(5, 10);
        
        // Wrong number of arguments
        let result2:int = add(5);
        
        // Wrong argument types
        let result3:int = add(true, false);
        
        // Undefined function
        let result4:int = undefined_func(1, 2);
        
        return result1;
    }
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, success, errors = analyze_code(test_code)
    
    if ast:
        print_ast(ast)
    
    # Should have errors for missing return, wrong return type, wrong args, etc.
    if not success and len(errors) >= 4:
        write_to_file(f"\nDetected {len(errors)} function-related errors:")
        for error in errors:
            write_to_file(f"  - {error}")
        print_outcome(True, "Correctly detected function errors")
        return True
    else:
        print_outcome(False, f"Expected at least 4 errors, found {len(errors)}")
        return False


def test_builtin_validation():
    """Test validation of built-in functions"""
    print_test_header("Built-in Function Validation",
                     "Semantic analyzer validates built-in function usage")
    
    test_code = """
    // Valid built-in usage
    let w:int = __width;
    let h:int = __height;
    let rand:int = __randi 100;
    let pixel:colour = __read 10, 20;
    
    __print 42;
    __delay 1000;
    __write 10, 20, #ff0000;
    __write_box 0, 0, 100, 100, #00ff00;
    __clear #000000;
    
    // Invalid built-in usage
    __print true;  // Can print bool, but let's see
    __delay 3.14;  // Wrong type
    __write 1.5, 2.5, #ff0000;  // Wrong types for x, y
    __write 10, 20, 255;  // Wrong type for color
    __clear 0;  // Wrong type
    __randi 3.14;  // Wrong type
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, success, errors = analyze_code(test_code)
    
    if ast:
        print_ast(ast)
    
    # Should have errors for wrong types in built-ins
    if not success and len(errors) > 0:
        write_to_file(f"\nDetected {len(errors)} built-in usage errors:")
        for error in errors:
            write_to_file(f"  - {error}")
        print_outcome(True, "Correctly validated built-in usage")
        return True
    else:
        print_outcome(False, "Failed to detect built-in usage errors")
        return False


def test_cast_validation():
    """Test type casting validation"""
    print_test_header("Type Cast Validation",
                     "Semantic analyzer validates type casts")
    
    test_code = """
    // Valid casts
    let i:int = 42;
    let f:float = 3.14;
    let b:bool = true;
    let c:colour = #ff0000;
    
    let i_to_f:float = i as float;
    let f_to_i:int = f as int;
    let i_to_b:bool = i as bool;
    let b_to_i:int = b as int;
    let i_to_c:colour = i as colour;
    let c_to_i:int = c as int;
    
    // Complex cast expressions
    let complex:float = (10 + 5 * 2) as float;
    let chained:colour = ((255 * 256) as colour);
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, success, errors = analyze_code(test_code)
    
    if ast:
        print_ast(ast)
    
    if success:
        write_to_file("\nAll casts are valid")
        print_outcome(True)
        return True
    else:
        write_to_file(f"\nSemantic errors: {len(errors)}")
        for error in errors:
            write_to_file(f"  - {error}")
        print_outcome(False, "Cast validation failed")
        return False


def test_control_flow_conditions():
    """Test that control flow conditions are boolean"""
    print_test_header("Control Flow Conditions",
                     "Semantic analyzer ensures control flow conditions are boolean")
    
    test_code = """
    let x:int = 5;
    let flag:bool = true;
    
    // Valid conditions
    if (flag) { __print 1; }
    if (x > 0) { __print 2; }
    if (not flag) { __print 3; }
    
    while (x > 0) {
        x = x - 1;
    }
    
    for (let i:int = 0; i < 10; i = i + 1) {
        __print i;
    }
    
    // Invalid conditions
    if (x) { __print 4; }  // int is not bool
    while (42) { __print 5; }  // int literal is not bool
    for (let j:int = 0; j; j = j + 1) { }  // int is not bool
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, success, errors = analyze_code(test_code)
    
    if ast:
        print_ast(ast)
    
    # Should detect non-boolean conditions
    if not success and len(errors) >= 3:
        write_to_file(f"\nDetected {len(errors)} condition type errors:")
        for error in errors:
            write_to_file(f"  - {error}")
        print_outcome(True, "Correctly detected non-boolean conditions")
        return True
    else:
        print_outcome(False, "Failed to detect all non-boolean conditions")
        return False


def test_modulo_type_checking():
    """Test modulo operator type checking"""
    print_test_header("Modulo Type Checking",
                     "Semantic analyzer correctly type-checks modulo operations")
    
    test_code = """
    // Valid modulo operations
    let a:int = 17;
    let b:int = 5;
    let c:float = 17.5;
    let d:float = 5.5;
    
    let int_mod:int = a % b;
    let float_mod:float = c % d;
    
    // Invalid modulo operations
    let flag:bool = true;
    let color:colour = #ff0000;
    
    let error1:int = a % flag;
    let error2:int = flag % b;
    let error3:int = a % color;
    let error4:int = color % color;
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, success, errors = analyze_code(test_code)
    
    if ast:
        print_ast(ast)
    
    # Should have errors for invalid modulo operations
    if not success and len(errors) >= 4:
        write_to_file(f"\nDetected {len(errors)} modulo type errors:")
        for error in errors:
            write_to_file(f"  - {error}")
        print_outcome(True, "Correctly validated modulo operations")
        return True
    else:
        print_outcome(False, "Failed to detect invalid modulo operations")
        return False


def test_complex_semantic_program():
    """Test semantic analysis on a complex program"""
    print_test_header("Complex Program Semantic Analysis",
                     "Semantic analyzer handles complex program with all features")
    
    test_code = """
    let global_counter:int = 0;
    
    fun factorial(n:int) -> int {
        if (n <= 1) {
            return 1;
        }
        return n * factorial(n - 1);
    }
    
    fun test_operations(x:int, y:int) -> bool {
        let sum:int = x + y;
        let diff:int = x - y;
        let prod:int = x * y;
        let quot:int = x / y;
        let rem:int = x % y;
        
        __print sum;
        __print rem;
        
        return rem == 0;
    }
    
    fun draw_pattern() -> int {
        for (let i:int = 0; i < 10; i = i + 1) {
            for (let j:int = 0; j < 10; j = j + 1) {
                if ((i + j) % 2 == 0) {
                    let color:colour = #ff0000;
                    __write i * 10, j * 10, color;
                } else {
                    let color:colour = #0000ff;
                    __write i * 10, j * 10, color;
                }
            }
        }
        
        global_counter = global_counter + 1;
        return global_counter;
    }
    
    // Main code
    let fact5:int = factorial(5);
    __print fact5;
    
    let divisible:bool = test_operations(20, 5);
    if (divisible) {
        __print 1;
    } else {
        __print 0;
    }
    
    let patterns:int = draw_pattern();
    __delay 1000;
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, success, errors = analyze_code(test_code)
    
    if ast:
        print_ast(ast, max_lines=100)
    
    if success:
        write_to_file("\nComplex program semantic analysis passed")
        print_outcome(True)
        return True
    else:
        write_to_file(f"\nSemantic errors: {len(errors)}")
        for error in errors:
            write_to_file(f"  - {error}")
        print_outcome(False, "Complex program semantic analysis failed")
        return False


def run_task3_tests():
    """Run all Task 3 tests"""
    output_file = create_test_output_file("task3_semantic")
    
    print("TASK 3 - SEMANTIC ANALYSIS TESTS")
    print("="*80)
    
    results = []
    
    # Run all tests
    results.append(("Type Checking", test_type_checking()))
    results.append(("Type Error Detection", test_type_errors()))
    results.append(("Scope Management", test_scope_management()))
    results.append(("Undefined Variables", test_undefined_variables()))
    results.append(("Function Validation", test_function_validation()))
    results.append(("Built-in Validation", test_builtin_validation()))
    results.append(("Cast Validation", test_cast_validation()))
    results.append(("Control Flow Conditions", test_control_flow_conditions()))
    results.append(("Modulo Type Checking", test_modulo_type_checking()))
    results.append(("Complex Program", test_complex_semantic_program()))
    
    # Summary
    write_to_file("\n" + "="*80)
    write_to_file("TASK 3 SUMMARY")
    write_to_file("="*80)
    
    print("\nTASK 3 SUMMARY")
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
    success = run_task3_tests()
    sys.exit(0 if success else 1)