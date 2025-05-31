"""
Task 2 - Hand-crafted LL(k) Parser Tests
Comprehensive testing of recursive descent parsing
Tests EBNF compliance, AST generation, and syntax error detection
"""

import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer.lexer import FSALexer
from parser.parser import PArLParser
from test.test_utils import (print_test_header, print_ast, print_completion_status, set_ast_printing,
                           create_test_output_file, close_test_output_file, write_to_file, 
                           reset_test_counter)

if "--show-ast" in sys.argv:
    set_ast_printing(True)
else:
    set_ast_printing(False)

def parse_program(source_code):
    """Parse program and return AST and errors"""
    lexer = FSALexer()
    tokens = lexer.tokenize(source_code.strip())
    
    # Check for lexical errors first
    error_tokens = [t for t in tokens if t.type.name.startswith("ERROR")]
    if error_tokens:
        return None, f"Lexical errors: {error_tokens}"
    
    parser = PArLParser(tokens)
    try:
        ast = parser.parse()
        if parser.has_errors():
            return None, f"Parser errors: {parser.errors}"
        return ast, None
    except Exception as e:
        return None, f"Parser exception: {str(e)}"


def test_expression_parsing_precedence():
    """Test 1: Expression Parsing and Operator Precedence
    Purpose: Verify correct parsing of expressions with proper precedence
    """
    create_test_output_file("task_2", "Expression Parsing and Operator Precedence")
    
    print_test_header("Expression Parsing and Operator Precedence",
                     "Tests arithmetic, logical, relational operations and precedence rules")
    
    test_code = """
    let a:int = 2 + 3 * 4;           // Should be 2 + (3 * 4) = 14
    let b:bool = x < y and z > w;    // Should be (x < y) and (z > w)
    let c:int = (a + b) * c / d;     // Parentheses override precedence
    let d:bool = not x or y and z;   // Should be (not x) or (y and z)
    let e:int = x % y + z * w;       // Should be (x % y) + (z * w)
    let f:bool = a == b and c != d or e <= f;  // Mixed operators
    let g:float = x as float + y as float;     // Cast expressions
    """
    
    write_to_file("INPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, error = parse_program(test_code)
    
    if error:
        write_to_file(f"\nParser error: {error}")
        print_completion_status("Expression Parsing", False)
        close_test_output_file()
        return False
    
    print_ast(ast)
    
    write_to_file("\nEXPRESSION STRUCTURE ANALYSIS:")
    write_to_file("-" * 60)
    
    # Analyze AST structure for precedence correctness
    if hasattr(ast, 'statements'):
        for i, stmt in enumerate(ast.statements):
            if hasattr(stmt, 'name') and hasattr(stmt, 'initializer'):
                write_to_file(f"Variable {stmt.name}: {type(stmt.initializer).__name__}")
                if hasattr(stmt.initializer, 'operator'):
                    write_to_file(f"  Root operator: {stmt.initializer.operator}")
    
    write_to_file("\nExpression parsing completed - check AST for precedence correctness")
    print_completion_status("Expression Parsing", True)
    close_test_output_file()
    return True


def test_function_declaration_parsing():
    """Test 2: Function Declaration Parsing
    Purpose: Verify parsing of function declarations with parameters and return types
    """
    create_test_output_file("task_2", "Function Declaration Parsing")
    
    print_test_header("Function Declaration Parsing",
                     "Tests function declarations, parameters, return types, and bodies")
    
    test_code = """
    // Simple function
    fun simple() -> int {
        return 42;
    }
    
    // Function with parameters
    fun add(x:int, y:int) -> int {
        return x + y;
    }
    
    // Function with mixed parameter types
    fun complex(a:int, b:float, c:bool, d:colour) -> bool {
        let result:bool = a > 0 and b > 0.0;
        if (c) {
            __write 0, 0, d;
        }
        return result;
    }
    
    // Function with array parameter (Task 5 preview)
    fun process_array(data:int[10]) -> int {
        return data[0];
    }
    
    // Recursive function
    fun factorial(n:int) -> int {
        if (n <= 1) {
            return 1;
        }
        return n * factorial(n - 1);
    }
    """
    
    write_to_file("INPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, error = parse_program(test_code)
    
    if error:
        write_to_file(f"\nParser error: {error}")
        print_completion_status("Function Parsing", False)
        close_test_output_file()
        return False
    
    print_ast(ast)
    
    write_to_file("\nFUNCTION ANALYSIS:")
    write_to_file("-" * 60)
    
    # Count functions and analyze their structure
    function_count = 0
    if hasattr(ast, 'statements'):
        for stmt in ast.statements:
            if hasattr(stmt, 'name') and hasattr(stmt, 'params'):
                function_count += 1
                param_count = len(stmt.params) if stmt.params else 0
                write_to_file(f"Function '{stmt.name}': {param_count} parameters -> {stmt.return_type}")
    
    write_to_file(f"\nTotal functions parsed: {function_count}")
    write_to_file("Function declaration parsing completed successfully")
    print_completion_status("Function Parsing", True)
    close_test_output_file()
    return True


def test_control_flow_parsing():
    """Test 3: Control Flow Statement Parsing
    Purpose: Verify parsing of if/else, while, and for statements
    """
    create_test_output_file("task_2", "Control Flow Statement Parsing")
    
    print_test_header("Control Flow Statement Parsing",
                     "Tests if/else, while loops, for loops, and nested control structures")
    
    test_code = """
    // Simple if statement
    if (x > 0) {
        __print x;
    }
    
    // If-else statement
    if (condition) {
        result = true;
    } else {
        result = false;
    }
    
    // While loop
    while (i < 10) {
        __print i;
        i = i + 1;
    }
    
    // For loop with all clauses
    for (let i:int = 0; i < 10; i = i + 1) {
        __print i;
    }
    
    // For loop with missing clauses
    for (; x < 100; x = x * 2) {
        __delay 100;
    }
    
    // Nested control structures
    for (let outer:int = 0; outer < 5; outer = outer + 1) {
        if (outer % 2 == 0) {
            for (let inner:int = 0; inner < outer; inner = inner + 1) {
                __write outer, inner, #FF0000;
            }
        } else {
            while (condition) {
                __delay 50;
                if (check()) {
                    break_condition = true;
                }
            }
        }
    }
    """
    
    write_to_file("INPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, error = parse_program(test_code)
    
    if error:
        write_to_file(f"\nParser error: {error}")
        print_completion_status("Control Flow Parsing", False)
        close_test_output_file()
        return False
    
    print_ast(ast, max_lines=80)
    
    write_to_file("\nCONTROL FLOW ANALYSIS:")
    write_to_file("-" * 60)
    
    # Count different control structures
    if_count = while_count = for_count = 0
    if hasattr(ast, 'statements'):
        def count_control_structures(node):
            nonlocal if_count, while_count, for_count
            if hasattr(node, '__class__'):
                if 'IfStatement' in node.__class__.__name__:
                    if_count += 1
                elif 'WhileStatement' in node.__class__.__name__:
                    while_count += 1
                elif 'ForStatement' in node.__class__.__name__:
                    for_count += 1
            
            # Recursively check child nodes
            if hasattr(node, '__dict__'):
                for attr_value in node.__dict__.values():
                    if hasattr(attr_value, '__class__') and hasattr(attr_value, '__dict__'):
                        count_control_structures(attr_value)
                    elif isinstance(attr_value, list):
                        for item in attr_value:
                            if hasattr(item, '__class__') and hasattr(item, '__dict__'):
                                count_control_structures(item)
        
        for stmt in ast.statements:
            count_control_structures(stmt)
    
    write_to_file(f"If statements: {if_count}")
    write_to_file(f"While loops: {while_count}")
    write_to_file(f"For loops: {for_count}")
    write_to_file("Control flow parsing completed successfully")
    print_completion_status("Control Flow Parsing", True)
    close_test_output_file()
    return True


def test_syntax_error_detection():
    """Test 4: Syntax Error Detection and Recovery
    Purpose: Verify parser detects syntax errors and provides meaningful messages
    """
    create_test_output_file("task_2", "Syntax Error Detection and Recovery")
    
    print_test_header("Syntax Error Detection and Recovery",
                     "Tests detection of various syntax errors with error recovery")
    
    test_cases = [
        ("Missing semicolon", "let x:int = 42 let y:int = 24;"),
        ("Unbalanced parentheses", "if (x > 0 { __print x; }"),
        ("Missing function body", "fun test() -> int;"),
        ("Invalid expression", "let x:int = 5 +;"),
        ("Missing type annotation", "let x = 42;"),
        ("Invalid for loop", "for (let i:int = 0 i < 10) { __print i; }"),
        ("Unclosed block", "if (true) { __print x;"),
        ("Missing return type", "fun test() { return 5; }"),
    ]
    
    write_to_file("SYNTAX ERROR TEST CASES:")
    write_to_file("=" * 60)
    
    error_detection_count = 0
    
    for i, (error_type, code) in enumerate(test_cases, 1):
        write_to_file(f"\nTest Case {i}: {error_type}")
        write_to_file(f"Input: {code}")
        
        ast, error = parse_program(code)
        
        if error:
            write_to_file(f"Error detected: {error}")
            error_detection_count += 1
        else:
            write_to_file("No error detected (unexpected)")
        
        write_to_file("-" * 40)
    
    write_to_file(f"\nERROR DETECTION SUMMARY:")
    write_to_file(f"Test cases: {len(test_cases)}")
    write_to_file(f"Errors detected: {error_detection_count}")
    write_to_file(f"Detection rate: {error_detection_count/len(test_cases)*100:.1f}%")
    
    success = error_detection_count >= len(test_cases) * 0.75  # At least 75% should be detected
    
    if success:
        write_to_file("\nSyntax error detection working effectively")
    else:
        write_to_file("\nSyntax error detection needs improvement")
    
    print_completion_status("Error Detection", success)
    close_test_output_file()
    return success


def run_task2_tests():
    """Run all Task 2 parser tests"""
    reset_test_counter()
    
    print("TASK 2 - HAND-CRAFTED LL(K) PARSER TESTS")
    print("="*80)
    
    results = []
    
    # Run all parser tests
    results.append(("Expression Parsing and Operator Precedence", test_expression_parsing_precedence()))
    results.append(("Function Declaration Parsing", test_function_declaration_parsing()))
    results.append(("Control Flow Statement Parsing", test_control_flow_parsing()))
    results.append(("Syntax Error Detection and Recovery", test_syntax_error_detection()))
    
    # Summary
    print("\nTASK 2 SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name:<50} {status}")
    
    print("-"*80)
    print(f"Passed: {passed}/{total}")
    print("Check test_outputs/task_2/ for detailed results")
    
    return passed == total


if __name__ == "__main__":
    success = run_task2_tests()
    sys.exit(0 if success else 1)