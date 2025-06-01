"""
Task 4 - PArIR Code Generation Tests
Comprehensive testing of PArIR instruction generation
Tests memory management, control flow, function calls, and instruction correctness
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


def test_basic_arithmetic_and_memory():
    """Test 1: Basic Arithmetic and Memory Operations
    Purpose: Verify generation of arithmetic operations and memory management
    """
    create_test_output_file("task_4", "Basic Arithmetic and Memory Operations")
    
    print_test_header("Basic Arithmetic and Memory Operations",
                     "Tests variable declarations, arithmetic operations, and memory access")
    
    test_code = """
    let a:int = 10;
    let b:int = 20;
    let c:int = a + b;
    let d:int = c * 2;
    let e:int = d - a;
    let f:int = e / 5;
    let g:int = f % 3;
    
    let x:float = 3.14;
    let y:float = x * 2.0;
    
    let flag:bool = true;
    let result:bool = flag and false;
    
    let color1:colour = #FF0000;
    let color2:colour = 255 as colour;
    """
    
    write_to_file("INPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = compile_program(test_code)
    
    if error:
        write_to_file(f"\nCompilation error: {error}")
        print_completion_status("Arithmetic and Memory", False)
        close_test_output_file()
        return False
    
    print_ast(ast)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-" * 60)
    for i, instr in enumerate(instructions):
        write_to_file(f"{instr}")
    write_to_file("-" * 60)
    
    # Analyze generated instructions
    write_to_file("\nINSTRUCTION ANALYSIS:")
    instruction_counts = {}
    for instr in instructions:
        op = instr.split()[0] if instr.split() else ""
        instruction_counts[op] = instruction_counts.get(op, 0) + 1
    
    write_to_file(f"Total instructions: {len(instructions)}")
    write_to_file("Instruction frequency:")
    for op, count in sorted(instruction_counts.items()):
        write_to_file(f"  {op}: {count}")
    
    # Check for essential instructions
    required_ops = ['push', 'st', 'add', 'mul', 'sub', 'div', 'mod', 'oframe', 'halt']
    missing_ops = [op for op in required_ops if op not in instruction_counts]
    
    if missing_ops:
        write_to_file(f"\nMissing essential operations: {missing_ops}")
        success = False
    else:
        write_to_file("\nAll essential operations present")
        success = True
    
    print_completion_status("Arithmetic and Memory", success)
    close_test_output_file()
    return success


def test_control_flow_generation():
    """Test 2: Control Flow Code Generation
    Purpose: Verify generation of conditional and loop constructs
    """
    create_test_output_file("task_4", "Control Flow Code Generation")
    
    print_test_header("Control Flow Code Generation",
                     "Tests if/else statements, while loops, and for loops with jumps")
    
    test_code = """
    let x:int = 10;
    
    // Simple if statement
    if (x > 5) {
        x = x + 1;
    }
    
    // If-else statement
    if (x > 15) {
        x = x - 5;
    } else {
        x = x + 5;
    }
    
    // While loop
    let counter:int = 0;
    while (counter < 5) {
        counter = counter + 1;
        __print counter;
    }
    
    // For loop
    for (let i:int = 0; i < 3; i = i + 1) {
        __print i;
        if (i == 1) {
            __delay 100;
        }
    }
    """
    
    write_to_file("INPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = compile_program(test_code)
    
    if error:
        write_to_file(f"\nCompilation error: {error}")
        print_completion_status("Control Flow Generation", False)
        close_test_output_file()
        return False
    
    print_ast(ast)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-" * 60)
    for i, instr in enumerate(instructions):
        write_to_file(f"{instr}")
    write_to_file("-" * 60)
    
    # Analyze control flow instructions
    write_to_file("\nCONTROL FLOW ANALYSIS:")
    jump_instructions = []
    comparison_instructions = []
    
    for i, instr in enumerate(instructions):
        if any(op in instr for op in ['jmp', 'cjmp']):
            jump_instructions.append((i, instr))
        elif any(op in instr for op in ['lt', 'gt', 'le', 'ge', 'eq']):
            comparison_instructions.append((i, instr))
    
    write_to_file(f"Jump instructions: {len(jump_instructions)}")
    for line_num, instr in jump_instructions:
        write_to_file(f"  {line_num}: {instr}")
    
    write_to_file(f"\nComparison instructions: {len(comparison_instructions)}")
    for line_num, instr in comparison_instructions:
        write_to_file(f"  {line_num}: {instr}")
    
    # Check for frame management
    frame_ops = [instr for instr in instructions if any(op in instr for op in ['oframe', 'cframe'])]
    write_to_file(f"\nFrame management operations: {len(frame_ops)}")
    
    success = len(jump_instructions) > 0 and len(comparison_instructions) > 0
    
    if success:
        write_to_file("\nControl flow generation successful")
    else:
        write_to_file("\nControl flow generation incomplete")
    
    print_completion_status("Control Flow Generation", success)
    close_test_output_file()
    return success


def test_function_calls_and_parameters():
    """Test 3: Function Calls and Parameter Passing
    Purpose: Verify function declaration, calls, and parameter/return handling
    """
    create_test_output_file("task_4", "Function Calls and Parameter Passing")
    
    print_test_header("Function Calls and Parameter Passing",
                     "Tests function definitions, calls, parameter passing, and returns")
    
    test_code = """
    
    fun multiply_and_check(a:int, b:int) -> bool {
        let result:int = a * b;
        if (result > 100) {
            return true;
        }
        return false;
    }
    
    fun complex_calculation(base:int, factor:float) -> float {
        let temp:float = base as float;
        let result:float = temp * factor;
        if (result > 50.0) {
            result = result / 2.0;
        }
        return result;
    }
    
    // Function calls in main
    let is_large:bool = multiply_and_check(12, 9);
    let calc_result:float = complex_calculation(20, 2.5);
    
    __print is_large;
    __print calc_result as int;
    """
    
    write_to_file("INPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = compile_program(test_code)
    
    if error:
        write_to_file(f"\nCompilation error: {error}")
        print_completion_status("Function Calls and Parameters", False)
        close_test_output_file()
        return False
    
    print_ast(ast, max_lines=80)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-" * 60)
    for i, instr in enumerate(instructions):
        write_to_file(f"{instr}")
    write_to_file("-" * 60)
    
    # Analyze function-related instructions
    write_to_file("\nFUNCTION ANALYSIS:")
    
    function_labels = [instr for instr in instructions if instr.startswith('.')]
    call_instructions = [instr for instr in instructions if 'call' in instr]
    return_instructions = [instr for instr in instructions if 'ret' in instr]
    alloc_instructions = [instr for instr in instructions if 'alloc' in instr]
    
    write_to_file(f"Function labels: {len(function_labels)}")
    for label in function_labels:
        write_to_file(f"  {label}")
    
    write_to_file(f"\nFunction calls: {len(call_instructions)}")
    for call in call_instructions:
        write_to_file(f"  {call}")
    
    write_to_file(f"\nReturn statements: {len(return_instructions)}")
    write_to_file(f"Memory allocations: {len(alloc_instructions)}")
    
    # Check for proper function structure
    expected_functions = 3  # add, multiply_and_check, complex_calculation
    expected_calls = 3     # calls to each function
    
    success = (len(function_labels) >= expected_functions and 
               len(call_instructions) >= expected_calls and
               len(return_instructions) >= expected_functions)
    
    if success:
        write_to_file("\nFunction call generation successful")
    else:
        write_to_file("\nFunction call generation incomplete")
    
    print_completion_status("Function Calls and Parameters", success)
    close_test_output_file()
    return success


def test_builtin_operations_generation():
    """Test 4: Built-in Operations Code Generation
    Purpose: Verify generation of built-in function calls and graphics operations
    """
    create_test_output_file("task_4", "Built-in Operations Code Generation")
    
    print_test_header("Built-in Operations Code Generation",
                     "Tests built-in functions: print, delay, write, write_box, clear, etc.")
    
    test_code = """
    // Basic built-ins with literals
    __print 42;
    __delay 1000;
    __clear #000000;
    
    // Graphics operations
    __write 10, 20, #FF0000;
    __write_box 5, 5, 10, 10, #00FF00;
    
    // Built-ins with expressions
    let x:int = 15;
    let y:int = 25;
    let color:colour = #0000FF;
    
    __write x, y, color;
    __write_box x - 5, y - 5, 20, 20, color;
    
    // Built-in expressions
    let width:int = __width;
    let height:int = __height;
    let random_num:int = __randi 100;
    let pixel_color:colour = __read 0, 0;
    
    // Complex usage
    for (let i:int = 0; i < 5; i = i + 1) {
        let rand_x:int = __randi width;
        let rand_y:int = __randi height;
        let rand_color:colour = (__randi 16777216) as colour;
        
        __write rand_x, rand_y, rand_color;
        __delay 100;
        
        if (i % 2 == 0) {
            __write_box rand_x, rand_y, 3, 3, #FFFFFF;
        }
    }
    
    __print width;
    __print height;
    __print random_num;
    """
    
    write_to_file("INPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = compile_program(test_code)
    
    if error:
        write_to_file(f"\nCompilation error: {error}")
        print_completion_status("Built-in Operations", False)
        close_test_output_file()
        return False
    
    print_ast(ast, max_lines=80)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-" * 60)
    for i, instr in enumerate(instructions):
        write_to_file(f"{instr}")
    write_to_file("-" * 60)
    
    # Analyze built-in operations
    write_to_file("\nBUILT-IN OPERATIONS ANALYSIS:")
    
    builtin_ops = {
        'print': 0, 'delay': 0, 'write': 0, 'writebox': 0, 'clear': 0,
        'width': 0, 'height': 0, 'irnd': 0, 'read': 0
    }
    
    for instr in instructions:
        for op in builtin_ops.keys():
            if op in instr:
                builtin_ops[op] += 1
    
    write_to_file("Built-in operation frequency:")
    for op, count in builtin_ops.items():
        if count > 0:
            write_to_file(f"  {op}: {count}")
    
    # Check for expected operations
    expected_builtins = ['print', 'delay', 'write', 'writebox', 'clear', 'width', 'height', 'irnd']
    found_builtins = [op for op, count in builtin_ops.items() if count > 0]
    missing_builtins = [op for op in expected_builtins if op not in found_builtins]
    
    write_to_file(f"\nExpected built-ins: {len(expected_builtins)}")
    write_to_file(f"Found built-ins: {len(found_builtins)}")
    
    if missing_builtins:
        write_to_file(f"Missing built-ins: {missing_builtins}")
        success = False
    else:
        write_to_file("All expected built-in operations found")
        success = True
    
    # Check for proper argument handling
    write_ops = [instr for instr in instructions if 'write' in instr and not 'writebox' in instr]
    writebox_ops = [instr for instr in instructions if 'writebox' in instr]
    
    write_to_file(f"\nGraphics operations:")
    write_to_file(f"  write operations: {len(write_ops)}")
    write_to_file(f"  writebox operations: {len(writebox_ops)}")
    
    if success:
        write_to_file("\nBuilt-in operations generation successful")
    else:
        write_to_file("\nBuilt-in operations generation incomplete")
    
    print_completion_status("Built-in Operations", success)
    close_test_output_file()
    return success


def run_task4_tests():
    """Run all Task 4 code generation tests"""
    reset_test_counter()
    
    print("TASK 4 - PArIR CODE GENERATION TESTS")
    print("="*80)
    
    results = []
    
    # Run all code generation tests
    results.append(("Basic Arithmetic and Memory Operations", test_basic_arithmetic_and_memory()))
    results.append(("Control Flow Code Generation", test_control_flow_generation()))
    results.append(("Function Calls and Parameter Passing", test_function_calls_and_parameters()))
    results.append(("Built-in Operations Code Generation", test_builtin_operations_generation()))
    
    # Summary
    print("\nTASK 4 SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name:<50} {status}")
    
    print("-"*80)
    print(f"Passed: {passed}/{total}")
    print("Check test_outputs/task_4/ for detailed results")
    
    return passed == total


if __name__ == "__main__":
    success = run_task4_tests()
    sys.exit(0 if success else 1)