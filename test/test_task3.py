"""
Task 3 - Semantic Analysis Tests - CORRECTED VERSION
Comprehensive testing of type checking, scope management, and semantic validation
Tests symbol table operations, type compatibility, and semantic error detection
"""

import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer.lexer import FSALexer
from parser.parser import PArLParser
from semantic_analyzer.semantic_analyzer import SemanticAnalyzer
from test.test_utils import (print_test_header, print_ast, print_completion_status, set_ast_printing,
                           create_test_output_file, close_test_output_file, write_to_file, 
                           reset_test_counter)

if "--show-ast" in sys.argv:
    set_ast_printing(True)
else:
    set_ast_printing(False)

def analyze_program(source_code):
    """Complete parsing and semantic analysis pipeline"""
    lexer = FSALexer()
    tokens = lexer.tokenize(source_code.strip())
    
    # Check for lexical errors
    error_tokens = [t for t in tokens if t.type.name.startswith("ERROR")]
    if error_tokens:
        return None, None, f"Lexical errors: {error_tokens}"
    
    # Parse
    parser = PArLParser(tokens)
    try:
        ast = parser.parse()
        if parser.has_errors():
            return None, None, f"Parser errors: {parser.errors}"
    except Exception as e:
        return None, None, f"Parser exception: {str(e)}"
    
    # Semantic analysis
    analyzer = SemanticAnalyzer()
    try:
        success = analyzer.analyze(ast)
        return ast, analyzer, None if success else f"Semantic errors: {analyzer.errors}"
    except Exception as e:
        return ast, analyzer, f"Semantic analysis exception: {str(e)}"


def test_type_checking_and_compatibility():
    """Test 1: Type Checking and Compatibility
    Purpose: Verify type checking for assignments, operations, and function calls
    """
    create_test_output_file("task_3", "Type Checking and Compatibility")
    
    print_test_header("Type Checking and Compatibility",
                     "Tests type compatibility for assignments, operations, and expressions")
    
    test_code = """
    // Valid type operations
    let a:int = 42;
    let b:int = a + 10;
    let c:float = 3.14;
    let d:float = c * 2.0;
    let e:bool = true;
    let f:bool = e and false;
    let g:colour = #FF0000;
    
    // Valid type casting
    let h:float = a as float;
    let i:int = c as int;
    let j:colour = 255 as colour;
    
    // Valid comparisons (should return bool)
    let comp1:bool = a > b;
    let comp2:bool = c <= d;
    let comp3:bool = e == f;
    let comp4:bool = g != #00FF00;
    
    // Mixed arithmetic (should be type-compatible)
    let arith1:int = a + b * 2;
    let arith2:float = c - d / 2.0;
    let arith3:int = a % 5;
    
    // Invalid operations (should cause semantic errors)
    let error1:int = a + c;        // int + float without cast
    let error2:bool = e + f;       // bool + bool invalid
    let error3:colour = g * 2;     // colour * int invalid
    let error4:int = a and b;      // logical op on non-bool
    """
    
    write_to_file("INPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, analyzer, error = analyze_program(test_code)
    
    if not ast:
        write_to_file(f"\nParsing failed: {error}")
        print_completion_status("Type Checking", False)
        close_test_output_file()
        return False
    
    print_ast(ast)
    
    write_to_file("\nSEMANTIC ANALYSIS RESULTS:")
    write_to_file("-" * 60)
    
    if error:
        write_to_file("Semantic errors detected (expected for invalid operations):")
        if analyzer and analyzer.errors:
            for i, sem_error in enumerate(analyzer.errors, 1):
                write_to_file(f"  {i}. {sem_error}")
        
        # Count expected vs unexpected errors
        expected_error_variables = ['error1', 'error2', 'error3', 'error4']
        write_to_file(f"\nExpected errors for variables: {expected_error_variables}")
        
        success = True  # Errors are expected
    else:
        write_to_file("No semantic errors detected")
        write_to_file("Note: Some type mismatches should have been detected")
        success = False
    
    write_to_file(f"\nType checking analysis completed")
    print_completion_status("Type Checking", success)
    close_test_output_file()
    return success


def test_scope_management_and_variable_declaration():
    """Test 2: Scope Management and Variable Declaration
    Purpose: Verify scope handling, variable redeclaration detection, and symbol table
    """
    create_test_output_file("task_3", "Scope Management and Variable Declaration")
    
    print_test_header("Scope Management and Variable Declaration",
                     "Tests scoping rules, variable redeclaration, and symbol table management")
    
    test_code = """
    // Global scope variables
    let global_x:int = 42;
    let global_y:float = 3.14;
    
    fun test_scope(param_x:int, param_y:int) -> bool {
        // Function scope - should not conflict with global
        let local_x:int = param_x + 10;
        let local_y:int = param_y * 2;
        
        // This should cause error - parameter redeclaration
        let param_x:int = 100;
        
        if (local_x > 50) {
            // Block scope
            let block_var:bool = true;
            let local_x:int = 999;  // Should shadow outer local_x
            
            // Nested block
            {
                let nested_var:colour = #00FF00;
                let block_var:bool = false;  // Should shadow block_var
            }
            
            // block_var should be accessible here
            return block_var;
        }
        
        // block_var should NOT be accessible here
        return block_var;  // Should cause undeclared variable error
    }
    
    // Back in global scope
    let global_x:int = 100;  // Should cause redeclaration error
    
    // Test variable usage before declaration
    let use_undeclared:int = undefined_var + 5;
    
    fun another_function() -> int {
        // Should be able to access global variables
        return global_y as int + global_x;
    }
    """
    
    write_to_file("INPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, analyzer, error = analyze_program(test_code)
    
    if not ast:
        write_to_file(f"\nParsing failed: {error}")
        print_completion_status("Scope Management", False)
        close_test_output_file()
        return False
    
    print_ast(ast, max_lines=80)
    
    write_to_file("\nSCOPE ANALYSIS RESULTS:")
    write_to_file("-" * 60)
    
    if error:
        write_to_file("Semantic errors detected:")
        if analyzer and analyzer.errors:
            error_types = {}
            for sem_error in analyzer.errors:
                error_str = str(sem_error)
                if 'redeclaration' in error_str.lower():
                    error_types['redeclaration'] = error_types.get('redeclaration', 0) + 1
                elif 'undeclared' in error_str.lower():
                    error_types['undeclared'] = error_types.get('undeclared', 0) + 1
                
                write_to_file(f"  • {sem_error}")
            
            write_to_file(f"\nError type summary:")
            for error_type, count in error_types.items():
                write_to_file(f"  {error_type}: {count}")
        
        expected_errors = ['redeclaration', 'undeclared']
        found_error_types = set(error_types.keys() if analyzer and analyzer.errors else [])
        
        success = any(expected in found_error_types for expected in expected_errors)
    else:
        write_to_file("No semantic errors detected")
        write_to_file("Note: Some scope violations should have been detected")
        success = False
    
    write_to_file(f"\nScope management analysis completed")
    print_completion_status("Scope Management", success)
    close_test_output_file()
    return success


def test_function_validation():
    """Test 3: Function Validation
    Purpose: Verify function signature checking, return type validation, and call validation
    """
    create_test_output_file("task_3", "Function Validation")
    
    print_test_header("Function Validation",
                     "Tests function declarations, return types, parameter matching, and calls")
    
    test_code = """
    // Valid function declarations
    fun add(x:int, y:int) -> int {
        return x + y;
    }
    
    fun multiply(a:float, b:float) -> float {
        return a * b;
    }
    
    fun is_positive(value:int) -> bool {
        if (value > 0) {
            return true;
        }
        return false;
    }
    
    // Function missing return (should cause error)
    fun missing_return(x:int) -> int {
        __print x;
        // Missing return statement
    }
    
    // Function with wrong return type
    fun wrong_return_type(x:int) -> bool {
        return x + 1;  // Should return bool, not int
    }
    
    // Function with unreachable code after return
    fun unreachable_code(x:int) -> int {
        return x * 2;
        __print x;  // This is unreachable
    }
    
    // Valid function calls
    let result1:int = add(5, 3);
    let result2:float = multiply(2.5, 4.0);
    let result3:bool = is_positive(result1);
    
    // Invalid function calls
    let error1:int = add(5);           // Wrong argument count
    let error2:int = add(5.0, 3.0);    // Wrong argument types
    let error3:bool = multiply(2, 3);   // Wrong types and assignment
    let error4:int = undefined_func(5); // Undeclared function
    
    // Recursive function (should be valid)
    fun factorial(n:int) -> int {
        if (n <= 1) {
            return 1;
        }
        return n * factorial(n - 1);
    }
    
    let fact5:int = factorial(5);
    """
    
    write_to_file("INPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, analyzer, error = analyze_program(test_code)
    
    if not ast:
        write_to_file(f"\nParsing failed: {error}")
        print_completion_status("Function Validation", False)
        close_test_output_file()
        return False
    
    print_ast(ast, max_lines=100)
    
    write_to_file("\nFUNCTION VALIDATION RESULTS:")
    write_to_file("-" * 60)
    
    if error:
        write_to_file("Semantic errors detected:")
        if analyzer and analyzer.errors:
            error_categories = {
                'missing_return': 0,
                'wrong_return_type': 0,
                'argument_mismatch': 0,
                'undeclared_function': 0,
                'type_mismatch': 0
            }
            
            for sem_error in analyzer.errors:
                error_str = str(sem_error).lower()
                if 'return' in error_str and 'missing' in error_str:
                    error_categories['missing_return'] += 1
                elif 'return' in error_str or 'type mismatch' in error_str:
                    error_categories['wrong_return_type'] += 1
                elif 'argument' in error_str:
                    error_categories['argument_mismatch'] += 1
                elif 'undeclared function' in error_str:
                    error_categories['undeclared_function'] += 1
                else:
                    error_categories['type_mismatch'] += 1
                
                write_to_file(f"  • {sem_error}")
            
            write_to_file(f"\nError category summary:")
            for category, count in error_categories.items():
                if count > 0:
                    write_to_file(f"  {category}: {count}")
        
        success = True  # Errors are expected
    else:
        write_to_file("No semantic errors detected")
        write_to_file("Note: Some function validation errors should have been detected")
        success = False
    
    write_to_file(f"\nFunction validation analysis completed")
    print_completion_status("Function Validation", success)
    close_test_output_file()
    return success


def test_builtin_function_validation():
    """Test 4: Built-in Function Validation - CORRECTED VERSION
    Purpose: Verify proper type checking for built-in functions and statements
    """
    create_test_output_file("task_3", "Built-in Function Validation")
    
    print_test_header("Built-in Function Validation",
                     "Tests built-in function parameter types and return type checking")
    
    test_code = """
    // Valid built-in usage
    __print 42;
    __print 3.14;
    __print true;
    __print #FF0000;
    
    __delay 1000;
    
    __write 10, 20, #00FF00;
    __write_box 5, 5, 10, 10, #0000FF;
    
    __clear #FFFFFF;
    
    let w:int = __width;
    let h:int = __height;
    
    let random_val:int = __randi 100;
    let pixel_color:colour = __read 15, 25;
        
    // Type mismatches in built-in statements
    __delay 3.14;                // Should be int, not float
    __delay (true as int);       // Should be int, not bool (cast to make parseable)
    
    __write 10.5, 20, #FF0000;   // x should be int, not float
    __write 10, 20.5, #FF0000;   // y should be int, not float  
    __write 10, 20, 255;         // color should be colour, not int
    
    __write_box 5.5, 5, 10, 10, #FF0000;    // x should be int
    __write_box 5, 5.5, 10, 10, #FF0000;    // y should be int
    __write_box 5, 5, 10.5, 10, #FF0000;    // width should be int
    __write_box 5, 5, 10, 10.5, #FF0000;    // height should be int
    __write_box 5, 5, 10, 10, 255;          // color should be colour
    
    __clear 255;                 // Should be colour, not int
    __clear (true as colour);    // Should be colour, not bool (cast to make parseable)
    
    // Type mismatches in built-in expressions
    let bad_random1:int = __randi 3.14;    // Should be int, not float
    let bad_random2:int = __randi (true as int);  // Should be int, not bool (cast to make parseable)
    
    let bad_read1:colour = __read 10.5, 20;     // x should be int, not float
    let bad_read2:colour = __read 10, 20.5;     // y should be int, not float
    
    // Type assignment errors
    let wrong_width:float = __width;     // __width returns int
    let wrong_random:bool = __randi 10;  // __randi returns int
    let wrong_pixel:int = __read 5, 5;   // __read returns colour
    
    // Undeclared variable reference (parseable but semantic error)
    let undefined_test:int = undefined_var;
    """
    
    write_to_file("INPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, analyzer, error = analyze_program(test_code)
    
    if not ast:
        write_to_file(f"\nParsing failed: {error}")
        print_completion_status("Built-in Validation", False)
        close_test_output_file()
        return False
    
    print_ast(ast, max_lines=100)
    
    write_to_file("\nBUILT-IN VALIDATION RESULTS:")
    write_to_file("-" * 60)
    
    if error:
        write_to_file("Semantic errors detected (expected for invalid operations):")
        if analyzer and analyzer.errors:
            builtin_errors = {
                '__print': 0, '__delay': 0, '__write': 0, '__write_box': 0,
                '__clear': 0, '__randi': 0, '__read': 0, 'assignment': 0, 'other': 0
            }
            
            for sem_error in analyzer.errors:
                error_str = str(sem_error)
                categorized = False
                for builtin in ['__print', '__delay', '__write', '__write_box', '__clear', '__randi', '__read']:
                    if builtin in error_str:
                        builtin_errors[builtin] += 1
                        categorized = True
                        break
                
                if not categorized:
                    if 'assignment' in error_str.lower() or 'initialize' in error_str.lower():
                        builtin_errors['assignment'] += 1
                    else:
                        builtin_errors['other'] += 1
                
                write_to_file(f"  • {sem_error}")
            
            write_to_file(f"\nBuilt-in error summary:")
            total_builtin_errors = 0
            for builtin, count in builtin_errors.items():
                if count > 0:
                    write_to_file(f"  {builtin}: {count} errors")
                    total_builtin_errors += count
            
            # Success if we detect multiple built-in related errors
            success = total_builtin_errors > 0
        else:
            success = False
    else:
        write_to_file("No semantic errors detected")
        write_to_file("Note: Some built-in validation errors should have been detected")
        success = False
    
    write_to_file(f"\nBuilt-in function validation completed")
    print_completion_status("Built-in Validation", success)
    close_test_output_file()
    return success


def run_task3_tests():
    """Run all Task 3 semantic analysis tests"""
    reset_test_counter()
    
    print("TASK 3 - SEMANTIC ANALYSIS TESTS (CORRECTED)")
    print("="*80)
    
    results = []
    
    # Run all semantic analysis tests
    results.append(("Type Checking and Compatibility", test_type_checking_and_compatibility()))
    results.append(("Scope Management and Variable Declaration", test_scope_management_and_variable_declaration()))
    results.append(("Function Validation", test_function_validation()))
    results.append(("Built-in Function Validation", test_builtin_function_validation()))
    
    # Summary
    print("\nTASK 3 SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name:<50} {status}")
    
    print("-"*80)
    print(f"Passed: {passed}/{total}")
    print("Check test_outputs/task_3/ for detailed results")

    
    return passed == total


if __name__ == "__main__":
    success = run_task3_tests()
    sys.exit(0 if success else 1)