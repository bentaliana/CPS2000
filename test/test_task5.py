"""
Task 5 - Array Tests
Tests for array functionality across all compiler phases
"""

import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer.lexer import FSALexer, TokenType
from parser.parser import PArLParser
from semantic_analyzer.semantic_analyzer import SemanticAnalyzer
from code_generator.code_generator import PArIRGenerator
from test.test_utils import print_test_header, print_ast, print_outcome, set_ast_printing, create_test_output_file, close_test_output_file, write_to_file


if "--show-ast" in sys.argv:
    set_ast_printing(True)
else:
    set_ast_printing(False)


# ============================================================================
# LEXER ARRAY TESTS
# ============================================================================

def test_array_lexing():
    """Test lexing of array-related tokens"""
    print_test_header("Array Lexing",
                     "Lexer correctly tokenizes array declarations and operations")
    
    test_code = """
    let numbers:int[] = [1, 2, 3, 4, 5];
    let colors:colour[] = [#ff0000, #00ff00, #0000ff];
    let value:int = numbers[0];
    numbers[1] = 10;
    fun process(data:int[10]) -> int { return data[0]; }
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    lexer = FSALexer()
    tokens = lexer.tokenize(test_code)
    
    write_to_file("\nTOKENS:")
    for token in tokens:
        if token.type not in [TokenType.WHITESPACE, TokenType.NEWLINE]:
            write_to_file(f"{token.lexeme} -> {token.type.name}")
    
    # Check for array-related tokens
    required_tokens = [TokenType.LBRACKET, TokenType.RBRACKET, TokenType.COMMA]
    found_types = {token.type for token in tokens}
    
    missing = [t for t in required_tokens if t not in found_types]
    
    if missing:
        print_outcome(False, f"Missing array tokens: {[t.name for t in missing]}")
        return False
    else:
        print_outcome(True)
        return True


# ============================================================================
# PARSER ARRAY TESTS
# ============================================================================

def test_array_parsing():
    """Test parsing of array declarations"""
    print_test_header("Array Declaration Parsing",
                     "Parser correctly handles array variable declarations")
    
    test_code = """
    let empty:int[] = [];
    let numbers:int[] = [1, 2, 3, 4, 5];
    let floats:float[] = [1.1, 2.2, 3.3];
    let bools:bool[] = [true, false, true];
    let colors:colour[] = [#ff0000, #00ff00, #0000ff];
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    lexer = FSALexer()
    tokens = lexer.tokenize(test_code)
    parser = PArLParser(tokens)
    
    try:
        ast = parser.parse()
        print_ast(ast)
        
        if parser.has_errors():
            error_details = f"Parser errors: {parser.errors}"
            print_outcome(False, error_details)
            return False
        else:
            print_outcome(True)
            return True
    except Exception as e:
        print_outcome(False, str(e))
        return False


def test_array_access_parsing():
    """Test parsing of array access"""
    print_test_header("Array Access Parsing",
                     "Parser correctly handles array element access")
    
    test_code = """
    let numbers:int[] = [10, 20, 30, 40, 50];
    let first:int = numbers[0];
    let last:int = numbers[4];
    let computed:int = numbers[2 + 1];
    
    // Array element assignment
    numbers[0] = 100;
    numbers[1 + 1] = 200;
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    lexer = FSALexer()
    tokens = lexer.tokenize(test_code)
    parser = PArLParser(tokens)
    
    try:
        ast = parser.parse()
        print_ast(ast)
        
        if parser.has_errors():
            error_details = f"Parser errors: {parser.errors}"
            print_outcome(False, error_details)
            return False
        else:
            print_outcome(True)
            return True
    except Exception as e:
        print_outcome(False, str(e))
        return False


def test_array_function_parsing():
    """Test parsing of arrays in function parameters"""
    print_test_header("Array Function Parameter Parsing",
                     "Parser correctly handles arrays as function parameters")
    
    test_code = """
    fun sum_array(arr:int[5]) -> int {
        let sum:int = 0;
        for (let i:int = 0; i < 5; i = i + 1) {
            sum = sum + arr[i];
        }
        return sum;
    }
    
    fun process_colors(colors:colour[3]) -> colour {
        return colors[1];
    }
    
    let numbers:int[] = [1, 2, 3, 4, 5];
    let total:int = sum_array(numbers);
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    lexer = FSALexer()
    tokens = lexer.tokenize(test_code)
    parser = PArLParser(tokens)
    
    try:
        ast = parser.parse()
        print_ast(ast)
        
        if parser.has_errors():
            error_details = f"Parser errors: {parser.errors}"
            print_outcome(False, error_details)
            return False
        else:
            print_outcome(True)
            return True
    except Exception as e:
        print_outcome(False, str(e))
        return False


# ============================================================================
# SEMANTIC ANALYSIS ARRAY TESTS
# ============================================================================

def test_array_type_checking():
    """Test array type checking"""
    print_test_header("Array Type Checking",
                     "Semantic analyzer correctly validates array types")
    
    test_code = """
    // Valid array operations
    let numbers:int[] = [1, 2, 3, 4, 5];
    let first:int = numbers[0];
    numbers[1] = 10;
    
    // Type consistency in array literals
    let floats:float[] = [1.1, 2.2, 3.3];
    let mixed_valid:float[] = [1.0, 2.0, 3.0];  // int literals can be float
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    lexer = FSALexer()
    tokens = lexer.tokenize(test_code)
    parser = PArLParser(tokens)
    ast = parser.parse()
    
    print_ast(ast)
    
    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(ast)
    
    if success:
        write_to_file("\nArray type checking passed")
        print_outcome(True)
        return True
    else:
        write_to_file(f"\nSemantic errors: {analyzer.errors}")
        print_outcome(False, "Array type checking failed")
        return False


def test_array_type_errors():
    """Test detection of array type errors"""
    print_test_header("Array Type Error Detection",
                     "Semantic analyzer detects array type mismatches")
    
    test_code = """
    // Mixed types in array literal
    let mixed:int[] = [1, 2, true, 4];
    
    // Wrong element type access
    let numbers:int[] = [1, 2, 3];
    let wrong:bool = numbers[0];
    
    // Wrong type assignment
    numbers[1] = true;
    
    // Non-integer index
    let value:int = numbers[1.5];
    
    // Indexing non-array
    let x:int = 5;
    let y:int = x[0];
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    lexer = FSALexer()
    tokens = lexer.tokenize(test_code)
    parser = PArLParser(tokens)
    ast = parser.parse()
    
    print_ast(ast)
    
    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(ast)
    
    if not success and len(analyzer.errors) >= 5:
        write_to_file(f"\nDetected {len(analyzer.errors)} array type errors:")
        for error in analyzer.errors:
            write_to_file(f"  - {error}")
        print_outcome(True, "Correctly detected array type errors")
        return True
    else:
        print_outcome(False, f"Expected at least 5 errors, found {len(analyzer.errors)}")
        return False


def test_array_function_semantics():
    """Test array function parameter semantics"""
    print_test_header("Array Function Semantics",
                     "Semantic analyzer validates array function parameters")
    
    test_code = """
    fun process_array(data:int[5]) -> int {
        return data[0] + data[4];
    }
    
    fun find_max(arr:int[8]) -> int {
        let max:int = arr[0];
        for (let i:int = 1; i < 8; i = i + 1) {
            if (arr[i] > max) {
                max = arr[i];
            }
        }
        return max;
    }
    
    // Valid calls
    let numbers:int[] = [1, 2, 3, 4, 5];
    let result1:int = process_array(numbers);
    
    let big_array:int[] = [10, 20, 30, 40, 50, 60, 70, 80];
    let max_val:int = find_max(big_array);
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    lexer = FSALexer()
    tokens = lexer.tokenize(test_code)
    parser = PArLParser(tokens)
    ast = parser.parse()
    
    print_ast(ast)
    
    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(ast)
    
    if success:
        write_to_file("\nArray function semantics passed")
        print_outcome(True)
        return True
    else:
        write_to_file(f"\nSemantic errors: {analyzer.errors}")
        print_outcome(False, "Array function semantics failed")
        return False


# ============================================================================
# CODE GENERATION ARRAY TESTS
# ============================================================================

def test_array_code_generation():
    """Test array code generation"""
    print_test_header("Array Code Generation",
                     "Code generator produces correct PArIR for array operations")
    
    test_code = """
    fun get_element(arr:int[5], index:int) -> int {
        return arr[index];
    }

    let numbers:int[] = [10, 20, 30, 40, 50];
    let first:int = numbers[0];
    let third:int = numbers[2];

    numbers[1] = 25;
    numbers[3] = 45;

    let element:int = get_element(numbers, 1);

    __print first;
    __print third;
    __print element;
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    lexer = FSALexer()
    tokens = lexer.tokenize(test_code)
    parser = PArLParser(tokens)
    ast = parser.parse()
    
    print_ast(ast)
    
    analyzer = SemanticAnalyzer()
    if not analyzer.analyze(ast):
        error_details = f"Semantic errors: {analyzer.errors}"
        print_outcome(False, error_details)
        return False
    
    generator = PArIRGenerator()
    instructions = generator.generate(ast)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-"*60)
    for instr in instructions:
        write_to_file(instr)
    write_to_file("-"*60)
    
    # Check for array operations
    required = ["pusha", "sta", "push [", "push +["]
    found = {req: any(req in instr for instr in instructions) for req in required}
    
    missing = [req for req, found in found.items() if not found]
    
    if missing:
        print_outcome(False, f"Missing array operations: {missing}")
        return False
    else:
        print_outcome(True)
        return True


def test_array_function_codegen():
    """Test array function code generation"""
    print_test_header("Array Function Code Generation",
                     "Code generator handles arrays in functions")
    
    test_code = """
    fun sum_array(arr:int[5]) -> int {
        let sum:int = 0;
        for (let i:int = 0; i < 5; i = i + 1) {
            sum = sum + arr[i];
        }
        return sum;
    }
    
    let numbers:int[] = [1, 2, 3, 4, 5];
    let total:int = sum_array(numbers);
    __print total;
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    lexer = FSALexer()
    tokens = lexer.tokenize(test_code)
    parser = PArLParser(tokens)
    ast = parser.parse()
    
    print_ast(ast)
    
    analyzer = SemanticAnalyzer()
    if not analyzer.analyze(ast):
        error_details = f"Semantic errors: {analyzer.errors}"
        print_outcome(False, error_details)
        return False
    
    generator = PArIRGenerator()
    instructions = generator.generate(ast)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-"*60)
    for instr in instructions:
        write_to_file(instr)
    write_to_file("-"*60)
    
    # Check for function and array operations
    required = [".sum_array", "call", "pusha", "push +["]
    found = {req: any(req in instr for instr in instructions) for req in required}
    
    missing = [req for req, found in found.items() if not found]
    
    if missing:
        print_outcome(False, f"Missing required operations: {missing}")
        return False
    else:
        print_outcome(True)
        return True


def test_maxinarray_complete():
    """Test complete MaxInArray example"""
    print_test_header("MaxInArray Complete Test",
                     "Complete compilation of MaxInArray function")
    
    test_code = """
    fun MaxInArray(x:int[8]) -> int {
        let m:int = 0;
        for (let i:int = 0; i < 8; i = i+1) {
            if (x[i] > m) { 
                m = x[i]; 
            }
        }
        return m;
    }

    let list_of_integers:int[] = [23, 54, 3, 65, 99, 120, 34, 21];
    let max:int = MaxInArray(list_of_integers);
    __print max;
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    # Lexical analysis
    lexer = FSALexer()
    tokens = lexer.tokenize(test_code)
    
    write_to_file("\nLEXICAL ANALYSIS: Success")
    
    # Parsing
    parser = PArLParser(tokens)
    ast = parser.parse()
    
    if parser.has_errors():
        error_details = f"Parser errors: {parser.errors}"
        print_outcome(False, error_details)
        return False
    
    write_to_file("PARSING: Success")
    print_ast(ast, max_lines=100)
    
    # Semantic analysis
    analyzer = SemanticAnalyzer()
    if not analyzer.analyze(ast):
        error_details = f"Semantic errors: {analyzer.errors}"
        print_outcome(False, error_details)
        return False
    
    write_to_file("SEMANTIC ANALYSIS: Success")
    
    # Code generation
    generator = PArIRGenerator()
    instructions = generator.generate(ast)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-"*60)
    for i, instr in enumerate(instructions):
        write_to_file(instr)
        if i > 100:
            write_to_file(f"... ({len(instructions) - i - 1} more instructions)")
            break
    write_to_file("-"*60)
    
    write_to_file(f"\nTotal instructions: {len(instructions)}")
    
    # Verify key components
    components = {
        ".MaxInArray": "Function definition",
        "pusha": "Array operations",
        "push +[": "Array indexing",
        "call": "Function call",
        "print": "Print result"
    }
    
    all_found = True
    write_to_file("\nVerifying components:")
    for component, description in components.items():
        found = any(component in instr for instr in instructions)
        write_to_file(f"  {description} ({component}): {'YES' if found else 'NO'}")
        if not found:
            all_found = False
    
    if all_found:
        print_outcome(True)
        return True
    else:
        print_outcome(False, "Missing required components")
        return False


def test_multidimensional_simulation():
    """Test simulation of multidimensional arrays using 1D arrays"""
    print_test_header("Multidimensional Array Simulation",
                     "Simulating 2D arrays using 1D arrays with index calculation")
    
    test_code = """
    // Simulate a 3x3 matrix using a 1D array
    fun get_matrix_element(matrix:int[9], row:int, col:int) -> int {
        let index:int = row * 3 + col;
        return matrix[index];
    }
    
    fun set_matrix_element(matrix:int[9], row:int, col:int, value:int) -> int {
        let index:int = row * 3 + col;
        matrix[index] = value;
        return value;
    }
    
    // Create identity matrix
    let matrix:int[] = [1, 0, 0, 0, 1, 0, 0, 0, 1];
    
    // Access elements
    let diag1:int = get_matrix_element(matrix, 0, 0);
    let diag2:int = get_matrix_element(matrix, 1, 1);
    let diag3:int = get_matrix_element(matrix, 2, 2);
    
    __print diag1;
    __print diag2;
    __print diag3;
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    lexer = FSALexer()
    tokens = lexer.tokenize(test_code)
    parser = PArLParser(tokens)
    ast = parser.parse()
    
    print_ast(ast, max_lines=100)
    
    analyzer = SemanticAnalyzer()
    if not analyzer.analyze(ast):
        error_details = f"Semantic errors: {analyzer.errors}"
        print_outcome(False, error_details)
        return False
    
    generator = PArIRGenerator()
    instructions = generator.generate(ast)
    
    write_to_file("\nGENERATED PArIR (partial):")
    write_to_file("-"*60)
    for i, instr in enumerate(instructions[:80]):
        write_to_file(instr)
    if len(instructions) > 80:
        write_to_file(f"... ({len(instructions) - 80} more instructions)")
    write_to_file("-"*60)
    
    print_outcome(True)
    return True


def test_array_algorithms():
    """Test array algorithms (sorting simulation)"""
    print_test_header("Array Algorithms",
                     "Implementing array algorithms like finding min/max")
    
    test_code = """
    fun find_min_max(arr:int[10]) -> int {
        let min:int = arr[0];
        let max:int = arr[0];
        
        for (let i:int = 1; i < 10; i = i + 1) {
            if (arr[i] < min) {
                min = arr[i];
            }
            if (arr[i] > max) {
                max = arr[i];
            }
        }
        
        __print min;
        __print max;
        return max - min;  // Return range
    }
    
    fun count_evens(arr:int[10]) -> int {
        let count:int = 0;
        for (let i:int = 0; i < 10; i = i + 1) {
            if (arr[i] % 2 == 0) {
                count = count + 1;
            }
        }
        return count;
    }
    
    let data:int[] = [15, 3, 27, 8, 42, 19, 6, 31, 12, 25];
    let range:int = find_min_max(data);
    let evens:int = count_evens(data);
    
    __print range;
    __print evens;
    """
    
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    lexer = FSALexer()
    tokens = lexer.tokenize(test_code)
    parser = PArLParser(tokens)
    ast = parser.parse()
    
    print_ast(ast, max_lines=100)
    
    analyzer = SemanticAnalyzer()
    if not analyzer.analyze(ast):
        error_details = f"Semantic errors: {analyzer.errors}"
        print_outcome(False, error_details)
        return False
    
    generator = PArIRGenerator()
    instructions = generator.generate(ast)
    
    write_to_file(f"\nGenerated {len(instructions)} instructions")
    print_outcome(True)
    return True


def run_task5_tests():
    """Run all Task 5 array tests"""
    output_file = create_test_output_file("task5_arrays")
    
    print("TASK 5 - ARRAY TESTS")
    print("="*80)
    
    results = []
    
    # Lexer tests
    results.append(("Array Lexing", test_array_lexing()))
    
    # Parser tests
    results.append(("Array Declaration Parsing", test_array_parsing()))
    results.append(("Array Access Parsing", test_array_access_parsing()))
    results.append(("Array Function Parsing", test_array_function_parsing()))
    
    # Semantic tests
    results.append(("Array Type Checking", test_array_type_checking()))
    results.append(("Array Type Errors", test_array_type_errors()))
    results.append(("Array Function Semantics", test_array_function_semantics()))
    
    # Code generation tests
    results.append(("Array Code Generation", test_array_code_generation()))
    results.append(("Array Function CodeGen", test_array_function_codegen()))
    results.append(("MaxInArray Complete", test_maxinarray_complete()))
    results.append(("Multidimensional Simulation", test_multidimensional_simulation()))
    results.append(("Array Algorithms", test_array_algorithms()))
    
    # Summary
    write_to_file("\n" + "="*80)
    write_to_file("TASK 5 SUMMARY")
    write_to_file("="*80)
    
    print("\nTASK 5 SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        write_to_file(f"{test_name:<35} {status}")
        print(f"{test_name:<35} {status}")
    
    write_to_file("-"*80)
    write_to_file(f"Total: {passed}/{total} tests passed")
    print("-"*80)
    print(f"Total: {passed}/{total} tests passed")
    
    close_test_output_file()
    print(f"Detailed output written to: {output_file}")
    
    return passed == total


if __name__ == "__main__":
    success = run_task5_tests()
    sys.exit(0 if success else 1)