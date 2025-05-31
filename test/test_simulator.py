"""
Simulator Test Programs - CORRECTED VERSION
Tests programs that should work correctly in the simulator
Each test creates its own output file with detailed results
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
                           create_parir_output_file, reset_test_counter)

if "--show-ast" in sys.argv:
    set_ast_printing(True)
else:
    set_ast_printing(False)

def compile_program(source_code):
    """Complete compilation pipeline"""
    # Lexical analysis
    lexer = FSALexer()
    tokens = lexer.tokenize(source_code.strip())
    
    # Check for lexical errors
    error_tokens = [t for t in tokens if t.type.name.startswith("ERROR")]
    if error_tokens:
        return None, None, f"Lexical errors: {error_tokens}"
    
    # Parsing
    parser = PArLParser(tokens)
    ast = parser.parse()
    
    if parser.has_errors():
        return None, None, f"Parser errors: {parser.errors}"
    
    # Semantic analysis
    analyzer = SemanticAnalyzer()
    if not analyzer.analyze(ast):
        return None, None, f"Semantic errors: {analyzer.errors}"
    
    # Code generation
    generator = PArIRGenerator()
    instructions = generator.generate(ast)
    
    return ast, instructions, None


def test_race_function():
    """Test Race function from assignment"""
    create_test_output_file("simulator", "Race Function")
    
    print_test_header("Race Function",
                     "Complete Race function with graphics output")
    
    test_code = """
    fun Race(p1_c:colour, p2_c:colour, score_max:int) -> int {
        let p1_score:int = 0;
        let p2_score:int = 0;
        
        while ((p1_score < score_max) and (p2_score < score_max)) {
            let p1_toss:int = __randi 1000;
            let p2_toss:int = __randi 1000;
            
            if (p1_toss > p2_toss) {
                p1_score = p1_score + 1;
                __write 1, p1_score, p1_c;
            } else {
                p2_score = p2_score + 1;
                __write 2, p2_score, p2_c;
            }
            
            __delay 100;
        }
        
        if (p2_score > p1_score) {
            return 2;
        }
        
        return 1;
    }
    
    // Execution starts here
    let c1:colour = #00ff00; //green
    let c2:colour = #0000ff; //blue
    let m:int = __height; //the height (y-values) of the pad
    let w:int = Race(c1, c2, m); //call function Race
    __print w; //prints value of expression to VM logs
    """
    
    write_to_file("INPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = compile_program(test_code)
    
    if error:
        write_to_file(f"\nCompilation error: {error}")
        print_completion_status("Compilation", False)
        close_test_output_file()
        return False
    
    print_ast(ast, max_lines=80)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-"*60)
    for i, instr in enumerate(instructions):
        write_to_file(f"{instr}")
    write_to_file("-"*60)
    
    write_to_file(f"\nTotal instructions: {len(instructions)}")
    
    # Save PArIR to file
    create_parir_output_file("simulator", "Race Function", instructions)
    
    write_to_file("\nRace function compiled successfully for simulator")
    write_to_file("Ready for execution in PAD2000c simulator")
    print_completion_status("Compilation", True)
    close_test_output_file()
    return True


def test_basic_color_animation():
    """Test simple animation loop from assignment"""
    create_test_output_file("simulator", "Basic Color Cycling Animation")
    
    print_test_header("Basic Color Cycling Animation",
                     "Simple animation loop suitable for simulator execution")
    
    test_code = """
    let c:colour = 0 as colour;

    for (let i:int = 0; i < 64; i = i + 1) {
        c = (__randi 16777216) as colour;
        __clear c;
        __delay 16;
    }
    """
    
    write_to_file("INPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = compile_program(test_code)
    
    if error:
        write_to_file(f"\nCompilation error: {error}")
        print_completion_status("Compilation", False)
        close_test_output_file()
        return False
    
    print_ast(ast)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-"*60)
    for i, instr in enumerate(instructions):
        write_to_file(f"{instr}")
    write_to_file("-"*60)
    
    # Save PArIR to file
    create_parir_output_file("simulator", "Basic Color Cycling Animation", instructions)
    
    write_to_file("\nBasic color animation ready for simulator")
    write_to_file("Creates a randomized color cycling display")
    print_completion_status("Compilation", True)
    close_test_output_file()
    return True


def test_max_in_array():
    """Test MaxInArray function"""
    create_test_output_file("simulator", "Max in Array Function")
    
    print_test_header("Max in Array Function",
                     "Finding maximum value in an array")
    
    test_code = """
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
        print_completion_status("Compilation", False)
        close_test_output_file()
        return False
    
    print_ast(ast, max_lines=80)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-"*60)
    for i, instr in enumerate(instructions):
        write_to_file(f"{instr}")
    write_to_file("-"*60)
    
    write_to_file(f"\nTotal instructions: {len(instructions)}")
    
    # Save PArIR to file
    create_parir_output_file("simulator", "Max in Array Function", instructions)
    
    write_to_file("\nMaxInArray function ready for simulator")
    write_to_file("Should print: 120 (maximum value from array)")
    print_completion_status("Compilation", True)
    close_test_output_file()
    return True


def test_random_color_generation():
    """Test color generation functions"""
    create_test_output_file("simulator", "Random Color Generation and Display")
    
    print_test_header("Random Color Generation and Display",
                     "Random color generation and display")
    
    test_code = """
    fun color() -> colour {
        return (__randi 16384257 - #f9f9f9 as int) as colour;
    }

    fun cc(x:int, y:int) -> bool {
        __print x;
        __print y;

        let c:colour = color();
        let h:int = __randi __height;
        let w:int = __randi __width;
        __write w, h, c;

        return true;
    }

    let a:bool = cc(0, 0);
    __delay 1000;
    """
    
    write_to_file("INPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = compile_program(test_code)
    
    if error:
        write_to_file(f"\nCompilation error: {error}")
        print_completion_status("Compilation", False)
        close_test_output_file()
        return False
    
    print_ast(ast)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-"*60)
    for i, instr in enumerate(instructions):
        write_to_file(f"{instr}")
    write_to_file("-"*60)
    
    # Save PArIR to file
    create_parir_output_file("simulator", "Random Color Generation and Display", instructions)
    
    write_to_file("\nRandom color generation ready for simulator")
    write_to_file("Displays random colored pixels at random locations")
    print_completion_status("Compilation", True)
    close_test_output_file()
    return True


def test_random_pixel_display():
    """Test random pixel display with color generation"""
    create_test_output_file("simulator", "Random Pixel Display")
    
    print_test_header("Random Pixel Display",
                     "Random pixel display with color generation")
    
    test_code = """
    fun color() -> colour {
        return (16777215 - __randi 16777215) as colour;
    }

    fun cc(x:int, y:int) -> bool {
        __print x;
        __print y;

        let c:colour = color();
        let h:int = __randi __height;
        let w:int = __randi __width;
        __write w, h, c;

        return true;
    }

    let a:bool = cc(0, 0);
    __delay 1000;
    """
    
    write_to_file("INPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = compile_program(test_code)
    
    if error:
        write_to_file(f"\nCompilation error: {error}")
        print_completion_status("Compilation", False)
        close_test_output_file()
        return False
    
    print_ast(ast)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-"*60)
    for i, instr in enumerate(instructions):
        write_to_file(f"{instr}")
    write_to_file("-"*60)
    
    write_to_file(f"\nTotal instructions: {len(instructions)}")
    
    # Save PArIR to file
    create_parir_output_file("simulator", "Random Pixel Display", instructions)
    
    write_to_file("\nRandom pixel display ready for simulator")
    write_to_file("Creates random pixel patterns with varied colors")
    print_completion_status("Compilation", True)
    close_test_output_file()
    return True


def test_color_animation_while():
    """Test color animation with while loop"""
    create_test_output_file("simulator", "Color Animation While Loop")
    
    print_test_header("Color Animation While Loop",
                     "Animated random pixels with iteration count")
    
    test_code = """
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
    
    write_to_file("INPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = compile_program(test_code)
    
    if error:
        write_to_file(f"\nCompilation error: {error}")
        print_completion_status("Compilation", False)
        close_test_output_file()
        return False
    
    print_ast(ast, max_lines=80)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-"*60)
    for i, instr in enumerate(instructions):
        write_to_file(f"{instr}")
    write_to_file("-"*60)
    
    # Save PArIR to file
    create_parir_output_file("simulator", "Color Animation While Loop", instructions)
    
    write_to_file("\nColor animation with while loop ready for simulator")
    write_to_file("Creates intensive random pixel animation (100,000 iterations)")
    print_completion_status("Compilation", True)
    close_test_output_file()
    return True


def test_rainbow_pattern():
    """Test rainbow pattern with arrays"""
    create_test_output_file("simulator", "Rainbow Pattern")
    
    print_test_header("Rainbow Pattern",
                     "Animated rainbow pattern using color array")
    
    test_code = """
    fun draw_pattern(offset:int) -> bool {
        let colors:colour[] = [#FF0000, #FF7F00, #FFFF00, #00FF00, #0000FF, #4B0082, #9400D3];

        for (let x:int = 0; x < __width; x = x + 3) {
            for (let y:int = 0; y < __height; y = y + 3) {                        
                let colorIndex:int = (x + y + offset) % 7;
                __write_box x, y, 2, 2, colors[colorIndex];
            }
        }

        return true;
    }

    let offset:int = 0;
    let r:bool = false;

    while (true) {
        r = draw_pattern(offset);
        offset = offset + 1;
        __delay 10;
    }
    """
    
    write_to_file("INPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = compile_program(test_code)
    
    if error:
        write_to_file(f"\nCompilation error: {error}")
        print_completion_status("Compilation", False)
        close_test_output_file()
        return False
    
    print_ast(ast, max_lines=100)
    
    write_to_file("\nGENERATED PArIR:")
    write_to_file("-"*60)
    for i, instr in enumerate(instructions):
        write_to_file(f"{instr}")
    write_to_file("-"*60)
    
    write_to_file(f"\nTotal instructions: {len(instructions)}")
    
    # Save PArIR to file
    create_parir_output_file("simulator", "Rainbow Pattern", instructions)
    
    write_to_file("\nRainbow pattern ready for simulator")
    write_to_file("Creates animated rainbow pattern with color arrays")
    write_to_file("Uses infinite loop - may need manual termination in simulator")
    print_completion_status("Compilation", True)
    close_test_output_file()
    return True


def run_simulator_tests():
    """Run all simulator test programs"""
    reset_test_counter()
    
    print("SIMULATOR TEST PROGRAMS")
    print("="*80)
    
    results = []
    
    # Run the specified tests - each creates its own output file
    results.append(("Race Function", test_race_function()))
    results.append(("Basic Color Cycling Animation", test_basic_color_animation()))
    results.append(("Max in Array Function", test_max_in_array()))
    results.append(("Random Color Generation and Display", test_random_color_generation()))
    results.append(("Random Pixel Display", test_random_pixel_display()))
    results.append(("Color Animation While Loop", test_color_animation_while()))
    results.append(("Rainbow Pattern", test_rainbow_pattern()))
    
    # Summary
    print("\nSIMULATOR TESTS SUMMARY")
    print("="*80)
    
    completed = len(results)
    
    for test_name, result in results:
        status = "COMPLETED" if result else "ISSUES"
        print(f"{test_name:<40} {status}")
    
    print("-"*80)
    print(f"Total: {completed} tests processed")
    print("Check test_outputs/simulator/ for:")
    print("- Individual test result files (.txt)")
    print("- Ready-to-use PArIR files (.parir)")
    print("- Copy .parir files to simulator for execution")
    
    return True


if __name__ == "__main__":
    success = run_simulator_tests()
    sys.exit(0 if success else 1)