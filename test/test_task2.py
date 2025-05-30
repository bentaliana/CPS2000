"""
Task 2 - Parser Tests
Tests for hand-crafted LL(k) parser
"""

import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer.lexer import FSALexer
from parser.parser import PArLParser


def print_test_header(test_name, description):
    """Print test header"""
    print("\n" + "="*80)
    print(f"TEST: {test_name}")
    print(f"TESTING: {description}")
    print("="*80)


def print_ast(ast, max_lines=50):
    """Print AST structure"""
    print("\nPROGRAM AST:")
    print("-"*60)
    try:
        ast_str = str(ast)
        lines = ast_str.split('\n')
        for i, line in enumerate(lines[:max_lines]):
            # Handle unicode characters for Windows console
            print(line.encode('utf-8', errors='replace').decode('utf-8'))
        if len(lines) > max_lines:
            print(f"... ({len(lines) - max_lines} more lines)")
    except Exception as e:
        print(f"Error printing AST: {e}")
    print("-"*60)


def print_outcome(success, details=""):
    """Print test outcome"""
    print("\nTEST OUTCOME:")
    if success:
        print("PASS")
    else:
        print(f"FAIL: {details}")


def test_variable_declarations():
    """Test parsing of variable declarations"""
    print_test_header("Variable Declarations",
                     "Parser correctly handles variable declarations of all types")
    
    test_code = """
    let x:int = 42;
    let y:float = 3.14;
    let flag:bool = true;
    let color:colour = #ff0000;
    let computed:int = 5 + 3 * 2;
    """
    
    print("\nINPUT PROGRAM:")
    print(test_code)
    
    lexer = FSALexer()
    tokens = lexer.tokenize(test_code)
    parser = PArLParser(tokens)
    
    try:
        ast = parser.parse()
        print_ast(ast)
        
        if parser.has_errors():
            print_outcome(False, f"Parser reported {len(parser.errors)} errors")
            for error in parser.errors:
                print(f"  - {error}")
            return False
        else:
            print_outcome(True)
            return True
    except Exception as e:
        print_outcome(False, str(e))
        return False


def test_function_declarations():
    """Test parsing of function declarations"""
    print_test_header("Function Declarations",
                     "Parser correctly handles function declarations with parameters and return types")
    
    test_code = """
    fun simple() -> int {
        return 0;
    }
    
    fun add(x:int, y:int) -> int {
        return x + y;
    }
    
    fun complex(a:int, b:float, c:bool) -> colour {
        let result:colour = #000000;
        if (c) {
            result = (a as colour);
        }
        return result;
    }
    """
    
    print("\nINPUT PROGRAM:")
    print(test_code)
    
    lexer = FSALexer()
    tokens = lexer.tokenize(test_code)
    parser = PArLParser(tokens)
    
    try:
        ast = parser.parse()
        print_ast(ast)
        
        if parser.has_errors():
            print_outcome(False, f"Parser reported {len(parser.errors)} errors")
            return False
        else:
            print_outcome(True)
            return True
    except Exception as e:
        print_outcome(False, str(e))
        return False


def test_control_structures():
    """Test parsing of control structures"""
    print_test_header("Control Structures",
                     "Parser correctly handles if/else, while, and for statements")
    
    test_code = """
    let x:int = 10;
    
    if (x > 5) {
        __print x;
    } else {
        __print 0;
    }
    
    while (x > 0) {
        x = x - 1;
        if (x % 2 == 0) {
            __print x;
        }
    }
    
    for (let i:int = 0; i < 10; i = i + 1) {
        if (i % 3 == 0) {
            __print i;
        }
    }
    """
    
    print("\nINPUT PROGRAM:")
    print(test_code)
    
    lexer = FSALexer()
    tokens = lexer.tokenize(test_code)
    parser = PArLParser(tokens)
    
    try:
        ast = parser.parse()
        print_ast(ast)
        
        if parser.has_errors():
            print_outcome(False, f"Parser reported {len(parser.errors)} errors")
            return False
        else:
            print_outcome(True)
            return True
    except Exception as e:
        print_outcome(False, str(e))
        return False


def test_expressions():
    """Test parsing of expressions with correct precedence"""
    print_test_header("Expression Parsing",
                     "Parser correctly handles expression precedence and associativity")
    
    test_code = """
    let a:int = 1 + 2 * 3;
    let b:int = (1 + 2) * 3;
    let c:int = 10 % 3 + 2;
    let d:int = 10 + 3 % 2;
    let e:bool = not true and false or true;
    let f:int = -5 * 3;
    let g:float = 10 as float / 2.0;
    let h:bool = 5 > 3 and 10 <= 20;
    let i:int = a + b * c - d / 2 % 3;
    """
    
    print("\nINPUT PROGRAM:")
    print(test_code)
    
    lexer = FSALexer()
    tokens = lexer.tokenize(test_code)
    parser = PArLParser(tokens)
    
    try:
        ast = parser.parse()
        print_ast(ast)
        
        if parser.has_errors():
            print_outcome(False, f"Parser reported {len(parser.errors)} errors")
            return False
        else:
            print_outcome(True)
            return True
    except Exception as e:
        print_outcome(False, str(e))
        return False


def test_builtin_statements():
    """Test parsing of built-in statements"""
    print_test_header("Built-in Statements",
                     "Parser correctly handles all built-in function statements")
    
    test_code = """
    let x:int = 10;
    let y:int = 20;
    let color:colour = #ff0000;
    
    __print x;
    __delay 1000;
    __write x, y, color;
    __write_box 0, 0, 100, 100, #00ff00;
    __clear #000000;
    
    let w:int = __width;
    let h:int = __height;
    let rand:int = __randi 100;
    let pixel:colour = __read x, y;
    """
    
    print("\nINPUT PROGRAM:")
    print(test_code)
    
    lexer = FSALexer()
    tokens = lexer.tokenize(test_code)
    parser = PArLParser(tokens)
    
    try:
        ast = parser.parse()
        print_ast(ast)
        
        if parser.has_errors():
            print_outcome(False, f"Parser reported {len(parser.errors)} errors")
            return False
        else:
            print_outcome(True)
            return True
    except Exception as e:
        print_outcome(False, str(e))
        return False


def test_function_calls():
    """Test parsing of function calls"""
    print_test_header("Function Calls",
                     "Parser correctly handles function calls with arguments")
    
    test_code = """
    fun add(x:int, y:int) -> int {
        return x + y;
    }
    
    fun process(a:int, b:float, c:bool) -> float {
        if (c) {
            return (a as float) + b;
        }
        return b;
    }
    
    let result1:int = add(5, 10);
    let result2:int = add(1 + 2, 3 * 4);
    let result3:float = process(10, 3.14, true);
    let nested:int = add(add(1, 2), add(3, 4));
    """
    
    print("\nINPUT PROGRAM:")
    print(test_code)
    
    lexer = FSALexer()
    tokens = lexer.tokenize(test_code)
    parser = PArLParser(tokens)
    
    try:
        ast = parser.parse()
        print_ast(ast)
        
        if parser.has_errors():
            print_outcome(False, f"Parser reported {len(parser.errors)} errors")
            return False
        else:
            print_outcome(True)
            return True
    except Exception as e:
        print_outcome(False, str(e))
        return False


def test_nested_structures():
    """Test parsing of deeply nested structures"""
    print_test_header("Nested Structures",
                     "Parser correctly handles deeply nested control structures")
    
    test_code = """
    fun nested_test(n:int) -> int {
        let result:int = 0;
        
        if (n > 0) {
            if (n % 2 == 0) {
                while (n > 0) {
                    for (let i:int = 0; i < n; i = i + 1) {
                        if (i % 3 == 0) {
                            result = result + i;
                        } else {
                            if (i % 5 == 0) {
                                result = result - i;
                            }
                        }
                    }
                    n = n - 1;
                }
            } else {
                result = n * 2;
            }
        }
        
        return result;
    }
    """
    
    print("\nINPUT PROGRAM:")
    print(test_code)
    
    lexer = FSALexer()
    tokens = lexer.tokenize(test_code)
    parser = PArLParser(tokens)
    
    try:
        ast = parser.parse()
        print_ast(ast)
        
        if parser.has_errors():
            print_outcome(False, f"Parser reported {len(parser.errors)} errors")
            return False
        else:
            print_outcome(True)
            return True
    except Exception as e:
        print_outcome(False, str(e))
        return False


def test_error_detection():
    """Test parser error detection"""
    print_test_header("Error Detection",
                     "Parser correctly detects and reports syntax errors")
    
    error_cases = [
        ("let x:int = ;", "Missing expression"),
        ("let :int = 5;", "Missing identifier"),
        ("if x > 0 { }", "Missing parentheses"),
        ("fun test() { return 5; }", "Missing return type"),
        ("{ let x:int = 5 }", "Missing semicolon"),
        ("let x:int = (5;", "Unmatched parenthesis")
    ]
    
    all_detected = True
    
    for test_code, description in error_cases:
        print(f"\n{description}:")
        print(f"INPUT: {test_code}")
        
        lexer = FSALexer()
        tokens = lexer.tokenize(test_code)
        parser = PArLParser(tokens)
        
        try:
            ast = parser.parse()
            if parser.has_errors():
                print(f"ERRORS DETECTED: {len(parser.errors)}")
                for error in parser.errors[:2]:  # Show first 2 errors
                    print(f"  - {error}")
            else:
                print("NO ERRORS DETECTED")
                all_detected = False
        except Exception as e:
            print(f"EXCEPTION: {str(e)[:100]}")
    
    print_outcome(all_detected)
    return all_detected


def test_complex_program():
    """Test parsing a complete complex program"""
    print_test_header("Complex Program",
                     "Parser correctly handles a complete program with all features")
    
    test_code = """
    fun fibonacci(n:int) -> int {
        if (n <= 1) {
            return n;
        }
        return fibonacci(n - 1) + fibonacci(n - 2);
    }
    
    fun test_modulo(a:int, b:int) -> int {
        let quotient:int = a / b;
        let remainder:int = a % b;
        
        if (remainder == 0) {
            return quotient;
        }
        
        return remainder;
    }
    
    fun main() -> int {
        let fib10:int = fibonacci(10);
        __print fib10;
        
        let mod_result:int = test_modulo(17, 5);
        __print mod_result;
        
        for (let i:int = 0; i < 10; i = i + 1) {
            if (i % 2 == 0) {
                let color:colour = (i * 1000) as colour;
                __write i * 10, i * 10, color;
            }
        }
        
        return 0;
    }
    
    let result:int = main();
    """
    
    print("\nINPUT PROGRAM:")
    print(test_code)
    
    lexer = FSALexer()
    tokens = lexer.tokenize(test_code)
    parser = PArLParser(tokens)
    
    try:
        ast = parser.parse()
        print_ast(ast, max_lines=100)
        
        if parser.has_errors():
            print_outcome(False, f"Parser reported {len(parser.errors)} errors")
            return False
        else:
            print_outcome(True)
            return True
    except Exception as e:
        print_outcome(False, str(e))
        return False


def run_task2_tests():
    """Run all Task 2 tests"""
    print("TASK 2 - PARSER TESTS")
    print("="*80)
    
    results = []
    
    # Run all tests
    results.append(("Variable Declarations", test_variable_declarations()))
    results.append(("Function Declarations", test_function_declarations()))
    results.append(("Control Structures", test_control_structures()))
    results.append(("Expression Parsing", test_expressions()))
    results.append(("Built-in Statements", test_builtin_statements()))
    results.append(("Function Calls", test_function_calls()))
    results.append(("Nested Structures", test_nested_structures()))
    results.append(("Error Detection", test_error_detection()))
    results.append(("Complex Program", test_complex_program()))
    
    # Summary
    print("\n" + "="*80)
    print("TASK 2 SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<30} {status}")
    
    print("-"*80)
    print(f"Total: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    success = run_task2_tests()
    sys.exit(0 if success else 1)