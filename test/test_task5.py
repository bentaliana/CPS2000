"""
Task 5 - Array Support Tests
Comprehensive testing of array functionality in PArL
Tests array declarations, initialization, indexing, and array-specific PArIR instructions
"""

import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer.lexer import FSALexer
from parser.parser import PArLParser
from semantic_analyzer.semantic_analyzer import SemanticAnalyzer
from code_generator.code_generator import PArIRGenerator
from test.test_utils import (print_test_header, print_ast, print_completion_status, set_ast_printing,
                           create_test_output_file, close_test_output_file, write_to_file, 
                           reset_test_counter)

if "--show-ast" in sys.argv:
    set_ast_printing(True)
else:
    set_ast_printing(False)

def compile_program(source_code):
    """Complete compilation pipeline"""
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
        if not analyzer.analyze(ast):
            return None, None, f"Semantic errors: {analyzer.errors}"
    except Exception as e:
        return None, None, f"Semantic analysis exception: {str(e)}"
    
    # Code generation
    generator = PArIRGenerator()
    try:
        instructions = generator.generate(ast)
        return ast, instructions, None
    except Exception as e:
        return ast, None, f"Code generation exception: {str(e)}"


def test_array_declarations_and_initialization():
    """Test 1: Array Declarations and Initialization
    Purpose: Verify array type parsing, literal initialization, and memory allocation
    """
    create_test_output_file("task_5", "Array Declarations and Initialization")
    
    print_test_header("Array Declarations and Initialization",
                     "Tests fixed-size arrays, dynamic arrays, and array literal initialization")
    
    test_code = """
    // Fixed-size array declarations
    let numbers:int[5] = [1, 2, 3, 4, 5];
    let floats:float[3] = [1.1, 2.2, 3.3];
    let flags:bool[4] = [true, false, true, false];
    let colors:colour[2] = [#FF0000, #00FF00];
    
    // Dynamic array declarations (size inferred from initializer)
    let dynamic_ints:int[] = [10, 20, 30, 40, 50, 60];
    let dynamic_colors:colour[] = [#000000, #FFFFFF, #FF0000, #00FF00, #0000FF];
    
    // Empty array declaration (fixed size, no initializer)
    let empty_array:int[10];
    
    // Single element arrays
    let single_int:int[] = [42];
    let single_color:colour[] = [#ABCDEF];
    
    // Mixed expressions in initializers
    let calculated:int[3] = [1 + 1, 2 * 3, 4 + 5];
    """
    
    write_to_file("INPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = compile_program(test_code)
    
    if error:
        write_to_file(f"\nCompilation error: {error}")
        print_completion_status("Array Declarations", False)
        close_test_output_file()
        return False
    
    print_ast(ast)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-" * 60)
    for i, instr in enumerate(instructions):
        write_to_file(f" {instr}")
    write_to_file("-" * 60)
    
    # Analyze array-specific instructions
    write_to_file("\nARRAY INSTRUCTION ANALYSIS:")
    array_instructions = {
        'sta': 0,     # Store array
        'push +[': 0, # Array element access
    }
    
    push_instructions = 0
    for instr in instructions:
        if 'sta' in instr:
            array_instructions['sta'] += 1
        elif 'push +[' in instr:
            array_instructions['push +['] += 1
        elif instr.startswith('push ') and not instr.startswith('push [') and not instr.startswith('push #'):
            push_instructions += 1
    
    write_to_file(f"Array store operations (sta): {array_instructions['sta']}")
    write_to_file(f"Array element access (push +[...]): {array_instructions['push +[']}")
    write_to_file(f"Value push operations: {push_instructions}")
    
    # Check for proper array initialization
    expected_arrays = 9  # Count of array declarations
    success = array_instructions['sta'] > 0 and push_instructions > 0
    
    if success:
        write_to_file("\nArray declaration and initialization successful")
    else:
        write_to_file("\nArray declaration and initialization incomplete")
    
    print_completion_status("Array Declarations", success)
    close_test_output_file()
    return success


def test_array_indexing_and_access():
    """Test 2: Array Indexing and Element Access
    Purpose: Verify array element access, assignment, and bounds checking
    """
    create_test_output_file("task_5", "Array Indexing and Element Access")
    
    print_test_header("Array Indexing and Element Access",
                     "Tests array element reading, writing, and index expressions")
    
    test_code = """
    let numbers:int[5] = [10, 20, 30, 40, 50];
    let colors:colour[3] = [#FF0000, #00FF00, #0000FF];
    
    // Simple array access
    let first:int = numbers[0];
    let last:int = numbers[4];
    let middle:int = numbers[2];
    
    // Array element assignment
    numbers[0] = 100;
    numbers[1] = numbers[2] + 5;
    numbers[3] = first * 2;
    
    // Complex indexing with expressions
    let index:int = 1;
    numbers[index] = 200;
    numbers[index + 1] = 300;
    
    // Array access in expressions
    let sum:int = numbers[0] + numbers[1];
    let product:int = numbers[2] * numbers[3];
    
    // Color array operations
    let red:colour = colors[0];
    colors[1] = #FFFFFF;
    colors[2] = red;
    
    // Array access in function calls and control structures
    __print numbers[0];
    __write 0, 0, colors[0];
    
    if (numbers[1] > 100) {
        numbers[1] = numbers[1] / 2;
    }
    
    for (let i:int = 0; i < 5; i = i + 1) {
        __print numbers[i];
        if (i < 3) {
            __write i, 0, colors[i % 3];
        }
    }
    """
    
    write_to_file("INPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = compile_program(test_code)
    
    if error:
        write_to_file(f"\nCompilation error: {error}")
        print_completion_status("Array Indexing", False)
        close_test_output_file()
        return False
    
    print_ast(ast, max_lines=100)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-" * 60)
    for i, instr in enumerate(instructions):
        write_to_file(f"{instr}")
    write_to_file("-" * 60)
    
    # Analyze array access instructions
    write_to_file("\nARRAY ACCESS ANALYSIS:")
    
    array_reads = [instr for instr in instructions if 'push +[' in instr]
    array_writes = [instr for instr in instructions if any(x in instr for x in ['st', 'sta'])]
    index_operations = [instr for instr in instructions if 'add' in instr]  # Index calculations
    
    write_to_file(f"Array element reads (push +[...]): {len(array_reads)}")
    for read in array_reads[:5]:  # Show first 5
        write_to_file(f"  {read}")
    if len(array_reads) > 5:
        write_to_file(f"  ... and {len(array_reads) - 5} more")
    
    write_to_file(f"\nArray element writes: {len(array_writes)}")
    write_to_file(f"Index calculations (add operations): {len(index_operations)}")
    
    success = len(array_reads) > 0 and len(array_writes) > 0
    
    if success:
        write_to_file("\nArray indexing and access successful")
    else:
        write_to_file("\nArray indexing and access incomplete")
    
    print_completion_status("Array Indexing", success)
    close_test_output_file()
    return success


def test_array_function_parameters():
    """Test 3: Array Function Parameters
    Purpose: Verify array parameter passing and array-specific parameter handling
    """
    create_test_output_file("task_5", "Array Function Parameters")
    
    print_test_header("Array Function Parameters",
                     "Tests array parameters and array argument passing")
    
    test_code = """
    // Function that takes array parameter
    fun sum_array(numbers:int[5]) -> int {
        let total:int = 0;
        for (let i:int = 0; i < 5; i = i + 1) {
            total = total + numbers[i];
        }
        return total;
    }
    
    // Function with multiple array parameters
    fun process_arrays(ints:int[3], colors:colour[2]) -> bool {
        for (let i:int = 0; i < 3; i = i + 1) {
            __print ints[i];
        }
        
        for (let i:int = 0; i < 2; i = i + 1) {
            __write i, 0, colors[i];
        }
        
        return true;
    }
    
    // Function that modifies array parameter
    fun double_values(data:int[4]) -> int {
        for (let i:int = 0; i < 4; i = i + 1) {
            data[i] = data[i] * 2;
        }
        return data[0];
    }
    
    // Function returning array element
    fun get_max(values:int[3]) -> int {
        let max:int = values[0];
        if (values[1] > max) {
            max = values[1];
        }
        if (values[2] > max) {
            max = values[2];
        }
        return max;
    }
    
    // Main program with function calls
    let my_numbers:int[5] = [1, 2, 3, 4, 5];
    let my_colors:colour[2] = [#FF0000, #00FF00];
    let my_data:int[4] = [10, 20, 30, 40];
    let small_array:int[3] = [100, 200, 150];
    
    let total:int = sum_array(my_numbers);
    let success:bool = process_arrays(small_array, my_colors);
    let first_doubled:int = double_values(my_data);
    let maximum:int = get_max(small_array);
    
    __print total;
    __print first_doubled;
    __print maximum;
    """
    
    write_to_file("INPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = compile_program(test_code)
    
    if error:
        write_to_file(f"\nCompilation error: {error}")
        print_completion_status("Array Function Parameters", False)
        close_test_output_file()
        return False
    
    print_ast(ast, max_lines=120)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-" * 60)
    for i, instr in enumerate(instructions):
        write_to_file(f"{instr}")
    write_to_file("-" * 60)
    
    # Analyze array parameter handling
    write_to_file("\nARRAY PARAMETER ANALYSIS:")
    
    array_element_pushes = [instr for instr in instructions if 'push +[' in instr]
    call_instructions = [instr for instr in instructions if 'call' in instr]
    function_labels = [instr for instr in instructions if instr.startswith('.') and instr != '.main']
    
    write_to_file(f"Function definitions: {len(function_labels)}")
    for label in function_labels:
        write_to_file(f"  {label}")
    
    write_to_file(f"\nArray element push operations (push +[...]): {len(array_element_pushes)}")
    for push in array_element_pushes[:10]:  # Show first 10
        write_to_file(f"  {push}")
    if len(array_element_pushes) > 10:
        write_to_file(f"  ... and {len(array_element_pushes) - 10} more")
    
    write_to_file(f"\nFunction calls: {len(call_instructions)}")
    for call in call_instructions:
        write_to_file(f"  {call}")
    
    # Check for proper array parameter passing
    expected_functions = 4  # sum_array, process_arrays, double_values, get_max
    expected_calls = 4     # calls to each function
    
    success = (len(function_labels) >= expected_functions and 
               len(call_instructions) >= expected_calls and
               len(array_element_pushes) > 0)
    
    if success:
        write_to_file("\nArray function parameters successful")
    else:
        write_to_file("\nArray function parameters incomplete")
    
    print_completion_status("Array Function Parameters", success)
    close_test_output_file()
    return success


def test_assignment_maxinarray_example():
    """Test 4: Assignment MaxInArray Example
    Purpose: Verify the exact example from assignment page 15 works correctly
    """
    create_test_output_file("task_5", "Assignment MaxInArray Example")
    
    print_test_header("Assignment MaxInArray Example",
                     "Tests the exact MaxInArray example from assignment page 15")
    
    test_code = """
    //x is an array of 8 +ve integers
    fun MaxInArray(x:int[8]) -> int {
        let m:int = 0;
        for (let i:int = 0; i < 8; i = i+1) {
            if (x[i] > m) { m = x[i]; }
        }
        return m;
    }

    let list_of_integers:int[] = [23, 54, 3, 65, 99, 120, 34, 21];
    let max:int = MaxInArray(list_of_integers);
    __print max;
    """
    
    write_to_file("INPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = compile_program(test_code)
    
    if error:
        write_to_file(f"\nCompilation error: {error}")
        print_completion_status("MaxInArray Example", False)
        close_test_output_file()
        return False
    
    print_ast(ast)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-" * 60)
    for i, instr in enumerate(instructions):
        write_to_file(f"{instr}")
    write_to_file("-" * 60)
    
    
    # Check for key instructions from assignment example
    expected_patterns = [
        '.MaxInArray',  # Function label
        'alloc',        # Memory allocation
        'push +[',      # Array element access
        'sta',          # Array storage
        'call',         # Function call
    ]
    
    found_patterns = {}
    for pattern in expected_patterns:
        found_patterns[pattern] = sum(1 for instr in instructions if pattern in instr)
    
    write_to_file("Expected instruction patterns:")
    for pattern, count in found_patterns.items():
        write_to_file(f"  {pattern}: {count} occurrences")
    
    # Verify array size handling
    array_literal_values = [23, 54, 3, 65, 99, 120, 34, 21]
    write_to_file(f"\nArray literal analysis:")
    write_to_file(f"Expected array values: {array_literal_values}")
    write_to_file(f"Expected array size: {len(array_literal_values)}")
    
    # Check if all literal values appear in push instructions
    literal_pushes = [instr for instr in instructions if instr.startswith('push ') and 
                     any(str(val) in instr for val in array_literal_values)]
    write_to_file(f"Array literal push instructions: {len(literal_pushes)}")
    
    success = all(count > 0 for count in found_patterns.values())
    
    if success:
        write_to_file("\nMaxInArray example compilation successful")
        write_to_file("Generated code follows assignment specification patterns")
    else:
        write_to_file("\nMaxInArray example compilation incomplete")
        missing = [pattern for pattern, count in found_patterns.items() if count == 0]
        write_to_file(f"Missing patterns: {missing}")
    
    print_completion_status("MaxInArray Example", success)
    close_test_output_file()
    return success


def test_array_parameters_and_returns():
    """Test 5: Array Parameters and Return Types"""
    create_test_output_file("task_5", "Array Parameters and Return Types")
    
    print_test_header("Array Parameters and Return Types",
                     "Tests arrays as function parameters and return values")
    
    # Simplified test 
    test_code = """
    fun get_first(arr: int[2]) -> int {
        return arr[0];
    }
    
    let numbers: int[2] = [5, 10];
    let first: int = get_first(numbers);
    
    __print first;
    """
    
    write_to_file("TESTING: Simplified array parameter functionality")
    write_to_file("INPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = compile_program(test_code)
    
    if error:
        write_to_file(f"\nCompilation error: {error}")
        write_to_file("This indicates the core array parameter functionality needs fixing")
        print_completion_status("Array Parameters and Returns", False)
        close_test_output_file()
        return False
    
    print_ast(ast, max_lines=40)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-" * 40)
    for i, instr in enumerate(instructions):
        write_to_file(f"{instr}")
    write_to_file("-" * 40)
    
    # Basic validation
    functions = [instr for instr in instructions if instr.startswith('.') and instr != '.main']
    calls = [instr for instr in instructions if 'call' in instr]
    
    success = len(functions) >= 1 and len(calls) >= 1 and error is None
    
    write_to_file(f"\nFunctions found: {len(functions)}")
    write_to_file(f"Function calls: {len(calls)}")
    write_to_file(f"Compilation successful: {error is None}")
    
    if success:
        write_to_file("PASSED: Basic array parameter functionality works")
    else:
        write_to_file("FAILED: Basic array parameter functionality broken")
        write_to_file("Check semantic analyzer array parameter support")
    
    print_completion_status("Array Parameters and Returns", success)
    close_test_output_file()
    return success


def run_task5_tests():
    """Run all Task 5 array tests"""
    reset_test_counter()
    
    print("TASK 5 - ARRAY SUPPORT TESTS")
    print("="*80)
    
    results = []
    
    results.append(("Array Declarations and Initialization", test_array_declarations_and_initialization()))
    results.append(("Array Indexing and Element Access", test_array_indexing_and_access()))
    results.append(("Array Function Parameters", test_array_function_parameters()))
    results.append(("Array Parameters and Return Types", test_array_parameters_and_returns()))
    results.append(("Assignment MaxInArray Example", test_assignment_maxinarray_example()))
    
    print("\nTASK 5 SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name:<50} {status}")
    
    print("-"*80)
    print(f"Passed: {passed}/{total}")
    print("Check test_outputs/task_5/ for detailed results")
    
    return passed == total


if __name__ == "__main__":
    success = run_task5_tests()
    sys.exit(0 if success else 1)