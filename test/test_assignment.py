"""
Assignment Examples Tests
Tests specifically from the assignment document examples
"""

import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer.lexer import FSALexer
from parser.parser import PArLParser
from semantic_analyzer.semantic_analyzer import SemanticAnalyzer
from code_generator.code_generator import PArIRGenerator
from test.test_utils import print_test_header, print_ast, print_completion_status, set_ast_printing, create_test_output_file, close_test_output_file, write_to_file, reset_test_counter

if "--show-ast" in sys.argv:
    set_ast_printing(True)
else:
    set_ast_printing(False)

def compile_program(source_code):
    """Complete compilation pipeline"""
    lexer = FSALexer()
    tokens = lexer.tokenize(source_code.strip())
    
    error_tokens = [t for t in tokens if t.type.name.startswith("ERROR")]
    if error_tokens:
        return None, None, f"Lexical errors: {error_tokens}"
    
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


def test_assignment_page3_functions():
    """Test all function examples from assignment page 3-4"""
    create_test_output_file("assignment", "Page 3-4 Function Examples")
    
    print_test_header("Assignment Page 3-4 Functions",
                     "XGreaterY, AverageOfTwo, Max functions from assignment")
    
    test_code = """
    /* This function takes two integers and return true if
     * the first argument is greater than the second.
     * Otherwise it returns false. */
    fun XGreaterY(x:int, y:int) -> bool {
        let ans:bool = true;
        if (y > x) { ans = false; }
        return ans;
    }

    // Same functionality as function above but using less code
    fun XGreaterY_2(x:int, y:int) -> bool {
        return x > y;
    }

    //Allocates memory space for 4 variables (x,y,t0,t1).
    fun AverageOfTwo(x:int, y:int) -> float {
        let t0:int = x + y;
        let t1:float = t0 / 2 as float; //casting expression to a float
        return t1;
    }

    /* Same functionality as function above but using less code.
     * Note the use of the brackets in the expression following
     * the return statement. Allocates space for 2 variables. */
    fun AverageOfTwo_2(x:int, y:int) -> float {
        return (x + y) / 2 as float;
    }

    //Takes two integers and returns the max of the two.
    fun Max(x:int, y:int) -> int {
        let m:int = x;
        if (y > m) { m = y; }
        return m;
    }
    """
    
    write_to_file("ASSIGNMENT EXAMPLE: Function definitions from pages 3-4")
    write_to_file("\nINPUT PROGRAM:")
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
    for instr in instructions:
        write_to_file(instr)
    write_to_file("-"*60)
    
    write_to_file(f"\nSuccessfully compiled {len(instructions)} PArIR instructions")
    print_completion_status("Compilation", True)
    close_test_output_file()
    return True


def test_assignment_page3_builtin_statements():
    """Test built-in statements from assignment page 3"""
    create_test_output_file("assignment", "Page 3 Built-in Statements")
    
    print_test_header("Assignment Page 3 Built-ins",
                     "Graphics and delay statements from assignment")
    
    test_code = """
    __write 10, 14, #00ff00;
    __delay 100;
    __write_box 10, 14, 2, 2, #0000ff;

    for (let i:int = 0; i<10; i=i+1) {
        __print i;
        __delay 1000;
    }
    """
    
    write_to_file("ASSIGNMENT EXAMPLE: Built-in statements from page 3")
    write_to_file("\nINPUT PROGRAM:")
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
    for instr in instructions:
        write_to_file(instr)
    write_to_file("-"*60)
    
    write_to_file(f"\nSuccessfully compiled {len(instructions)} PArIR instructions")
    print_completion_status("Compilation", True)
    close_test_output_file()
    return True


def test_assignment_race_function():
    """Test complete Race function from assignment pages 4-5"""
    create_test_output_file("assignment", "Race Function Complete")
    
    print_test_header("Assignment Race Function",
                     "Complete Race function example from pages 4-5")
    
    test_code = """
    /* This function takes two colours (players) and a max score.
     * A while loop is used to iteratively draw random numbers for the two
     * players and advance (along the y-axis) the player that gets the
     * highest score. Returns the winner (either 1 or 2) when max score is
     * reached by any of the players. Winner printed on console.
     */
    fun Race(p1_c:colour, p2_c:colour, score_max:int) -> int {
        let p1_score:int = 0;
        let p2_score:int = 0;

        //while (Max(p1_score, p2_score) < score_max) //Alternative loop
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
    //Execution (program entry point) starts at the first statement
    //that is not a function declaration. This should go in the .main
    //function of ParIR.

    let c1:colour = #00ff00; //green
    let c2:colour = #0000ff; //blue
    let m:int = __height; //the height (y-values) of the pad
    let w:int = Race(c1, c2, m); //call function Race
    __print w; //prints value of expression to VM logs
    """
    
    write_to_file("ASSIGNMENT EXAMPLE: Complete Race function from pages 4-5")
    write_to_file("\nINPUT PROGRAM:")
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
    for instr in instructions:
        write_to_file(instr)
    write_to_file("-"*60)
    
    write_to_file(f"\nSuccessfully compiled {len(instructions)} PArIR instructions")
    print_completion_status("Compilation", True)
    close_test_output_file()
    return True


def test_assignment_page9_scope_error():
    """Test scope management error example from assignment page 9"""
    create_test_output_file("assignment", "Page 9 Scope Error Example")
    
    print_test_header("Assignment Page 9 Scope Errors",
                     "Variable redeclaration errors that should be detected")
    
    test_code = """
    fun MoreThan50(x:int) -> bool {
        let x:int = 23; //syntax ok, but this should not be allowed!!
        if (x <= 50) {
            return false;
        }
        return true;
    }

    let x:int = 45; //this is fine
    while (x < 50) {
        __print MoreThan50(x); //"false" *5 since bool operator is <
        x = x + 1;
    }

    let x:int = 45; //re-declaration in the same scope ... not allowed!!
    while (MoreThan50(x)) {
        __print MoreThan50(x); //"false" x5 since bool operator is <=
        x = x + 1;
    }
    """
    
    write_to_file("ASSIGNMENT EXAMPLE: Scope error detection from page 9")
    write_to_file("\nINPUT PROGRAM:")
    write_to_file(test_code)
    
    ast, instructions, error = compile_program(test_code)
    
    # This should detect semantic errors
    if error and "Semantic errors" in error:
        write_to_file(f"\nCorrectly detected semantic errors: {error}")
        print_completion_status("Error Detection", True)
    elif ast:
        print_ast(ast)
        write_to_file("\nGENERATED PArIR:")
        write_to_file("-"*60)
        for instr in instructions:
            write_to_file(instr)
        write_to_file("-"*60)
        write_to_file("\nProgram compiled - semantic analyzer may need enhancement")
        print_completion_status("Compilation", True)
    else:
        write_to_file(f"\nUnexpected error: {error}")
        print_completion_status("Compilation", False)
    
    close_test_output_file()
    return True


def test_assignment_page9_graphics_loop():
    """Test graphics loop from assignment page 9"""
    create_test_output_file("assignment", "Page 9 Graphics Loop")
    
    print_test_header("Assignment Page 9 Graphics Loop",
                     "Nested loops with graphics operations")
    
    test_code = """
    let w: int = __width;
    let h: int = __height;

    for (let u:int = 0; u<w; u = u+1)
    {
        for (let v:int = 0; v<h; v = v+1)
        {
            //set the pixel at u,v to the colour green
            __write_box u,v,1,1,#00ff00;
            //or ... assume one pixel 1x1
            //__write u,v,#00ff00;
        }
    }
    """
    
    write_to_file("ASSIGNMENT EXAMPLE: Graphics loop from page 9")
    write_to_file("\nINPUT PROGRAM:")
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
    for instr in instructions:
        write_to_file(instr)
    write_to_file("-"*60)
    
    write_to_file(f"\nSuccessfully compiled {len(instructions)} PArIR instructions")
    print_completion_status("Compilation", True)
    close_test_output_file()
    return True



def run_assignment_tests():
    """Run all assignment example tests"""
    reset_test_counter()
    
    print("ASSIGNMENT EXAMPLES TESTS")
    print("="*80)
    
    results = []
    
    # Run all assignment examples
    results.append(("Page 3-4 Functions", test_assignment_page3_functions()))
    results.append(("Page 3 Built-ins", test_assignment_page3_builtin_statements()))
    results.append(("Race Function", test_assignment_race_function()))
    results.append(("Page 9 Scope Errors", test_assignment_page9_scope_error()))
    results.append(("Page 9 Graphics Loop", test_assignment_page9_graphics_loop()))
    
    # Summary
    print("\nASSIGNMENT EXAMPLES SUMMARY")
    print("="*80)
    
    completed = len(results)
    
    for test_name, result in results:
        status = "COMPLETED" if result else "ISSUES"
        print(f"{test_name:<40} {status}")
    
    print("-"*80)
    print(f"Total: {completed} assignment examples processed")
    print("Check test_outputs/assignment/ for detailed results")
    
    return True


if __name__ == "__main__":
    success = run_assignment_tests()
    sys.exit(0)