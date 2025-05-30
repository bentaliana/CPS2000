"""
Simulator Test Programs
Tests professor's provided examples that should work in the simulator
"""

import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer.lexer import FSALexer
from parser.parser import PArLParser
from semantic_analyzer.semantic_analyzer import SemanticAnalyzer
from code_generator.code_generator import PArIRGenerator


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


def test_simple_color_animation():
    """Test simple color animation from professor's examples"""
    print_test_header("Simple Color Animation",
                     "Basic color cycling animation")
    
    test_code = """
    let c:colour = 0 as colour;

    for (let i:int = 0; i < 64; i = i + 1) {
        c = (__randi 16777216) as colour;
        __clear c;
        __delay 16;
    }
    """
    
    print("\nINPUT PROGRAM:")
    print(test_code)
    
    ast, instructions, error = compile_program(test_code)
    
    if error:
        print_outcome(False, error)
        return False
    
    print_ast(ast)
    
    print("\nGENERATED PArIR:")
    print("-"*60)
    for instr in instructions:
        print(instr)
    print("-"*60)
    
    # Verify animation instructions
    required = ["irnd", "clear", "delay", "cjmp", "jmp"]
    found = {req: any(req in instr for instr in instructions) for req in required}
    
    missing = [req for req, found in found.items() if not found]
    
    if missing:
        print_outcome(False, f"Missing animation instructions: {missing}")
        return False
    else:
        print_outcome(True)
        return True


def test_max_in_array():
    """Test MaxInArray function from professor's examples"""
    print_test_header("MaxInArray Function",
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
    
    print("\nINPUT PROGRAM:")
    print(test_code)
    
    ast, instructions, error = compile_program(test_code)
    
    if error:
        print_outcome(False, error)
        return False
    
    print_ast(ast, max_lines=80)
    
    print("\nGENERATED PArIR (first 100 instructions):")
    print("-"*60)
    for i, instr in enumerate(instructions[:100]):
        print(instr)
    if len(instructions) > 100:
        print(f"... ({len(instructions) - 100} more instructions)")
    print("-"*60)
    
    print(f"\nTotal instructions: {len(instructions)}")
    
    # Verify array operations
    required = [".MaxInArray", "pusha", "push +[", "call", "print"]
    found = {req: any(req in instr for instr in instructions) for req in required}
    
    missing = [req for req, found in found.items() if not found]
    
    if missing:
        print_outcome(False, f"Missing required operations: {missing}")
        return False
    else:
        print_outcome(True)
        return True


def test_color_functions():
    """Test color generation functions from professor's examples"""
    print_test_header("Color Functions",
                     "Random color generation and display")
    
    test_code = """
    fun color() -> colour {
        return (__randi 16777216 - #f9f9f9 as int) as colour;
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
    
    print("\nINPUT PROGRAM:")
    print(test_code)
    
    ast, instructions, error = compile_program(test_code)
    
    if error:
        print_outcome(False, error)
        return False
    
    print_ast(ast)
    
    print("\nGENERATED PArIR:")
    print("-"*60)
    for instr in instructions:
        print(instr)
    print("-"*60)
    
    # Verify function and graphics operations
    required = [".color", ".cc", "call", "write", "width", "height", "irnd", "delay"]
    found = {req: any(req in instr for instr in instructions) for req in required}
    
    missing = [req for req, found in found.items() if not found]
    
    if missing:
        print_outcome(False, f"Missing required operations: {missing}")
        return False
    else:
        print_outcome(True)
        return True


def test_color_animation_while():
    """Test color animation with while loop"""
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
    
    print("\nINPUT PROGRAM:")
    print(test_code)
    
    ast, instructions, error = compile_program(test_code)
    
    if error:
        print_outcome(False, error)
        return False
    
    print_ast(ast, max_lines=80)
    
    print("\nGENERATED PArIR (first 100 instructions):")
    print("-"*60)
    for i, instr in enumerate(instructions[:100]):
        print(instr)
    if len(instructions) > 100:
        print(f"... ({len(instructions) - 100} more instructions)")
    print("-"*60)
    
    # Verify while loop and graphics
    required = ["cjmp", "jmp", "#PC", "write", "irnd"]
    found = {req: any(req in instr for instr in instructions) for req in required}
    
    missing = [req for req, found in found.items() if not found]
    
    if missing:
        print_outcome(False, f"Missing required operations: {missing}")
        return False
    else:
        print_outcome(True)
        return True


def test_rainbow_pattern():
    """Test rainbow pattern with arrays"""
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
    
    print("\nINPUT PROGRAM:")
    print(test_code)
    
    ast, instructions, error = compile_program(test_code)
    
    if error:
        print_outcome(False, error)
        return False
    
    print_ast(ast, max_lines=100)
    
    print("\nGENERATED PArIR (first 150 instructions):")
    print("-"*60)
    for i, instr in enumerate(instructions[:150]):
        print(instr)
    if len(instructions) > 150:
        print(f"... ({len(instructions) - 150} more instructions)")
    print("-"*60)
    
    print(f"\nTotal instructions: {len(instructions)}")
    
    # Verify array and graphics operations
    required = ["pusha", "push +[", "writebox", "mod", "width", "height"]
    found = {req: any(req in instr for instr in instructions) for req in required}
    
    missing = [req for req, found in found.items() if not found]
    
    if missing:
        print_outcome(False, f"Missing required operations: {missing}")
        return False
    else:
        print_outcome(True)
        return True


def test_screen_operations():
    """Test various screen operations"""
    print_test_header("Screen Operations",
                     "Testing all screen-related built-in functions")
    
    test_code = """
    // Get screen dimensions
    let w:int = __width;
    let h:int = __height;
    
    __print w;
    __print h;
    
    // Clear screen with blue
    __clear #0000FF;
    __delay 500;
    
    // Draw some pixels
    for (let i:int = 0; i < 10; i = i + 1) {
        let x:int = i * 10;
        let y:int = i * 10;
        let color:colour = (i * 1000000) as colour;
        __write x, y, color;
    }
    
    // Draw boxes
    __write_box 50, 50, 20, 20, #FF0000;
    __write_box 100, 50, 20, 20, #00FF00;
    __write_box 150, 50, 20, 20, #0000FF;
    
    // Read a pixel
    let pixel:colour = __read 60, 60;
    let pixel_int:int = pixel as int;
    __print pixel_int;
    
    __delay 1000;
    """
    
    print("\nINPUT PROGRAM:")
    print(test_code)
    
    ast, instructions, error = compile_program(test_code)
    
    if error:
        print_outcome(False, error)
        return False
    
    print_ast(ast)
    
    print("\nGENERATED PArIR:")
    print("-"*60)
    for instr in instructions:
        print(instr)
    print("-"*60)
    
    # Verify all screen operations
    required = ["width", "height", "clear", "write", "writebox", "read", "delay", "print"]
    found = {req: any(req in instr for instr in instructions) for req in required}
    
    missing = [req for req, found in found.items() if not found]
    
    if missing:
        print_outcome(False, f"Missing screen operations: {missing}")
        return False
    else:
        print("\nAll screen operations found:")
        for req in required:
            print(f"  {req}: YES")
        print_outcome(True)
        return True


def test_modulo_patterns():
    """Test patterns using modulo operator"""
    print_test_header("Modulo Patterns",
                     "Creating patterns using modulo operator")
    
    test_code = """
    fun draw_checkerboard() -> int {
        let count:int = 0;
        
        for (let x:int = 0; x < __width; x = x + 10) {
            for (let y:int = 0; y < __height; y = y + 10) {
                if ((x / 10 + y / 10) % 2 == 0) {
                    __write_box x, y, 10, 10, #FFFFFF;
                } else {
                    __write_box x, y, 10, 10, #000000;
                }
                count = count + 1;
            }
        }
        
        return count;
    }
    
    fun draw_stripes(width:int) -> bool {
        for (let x:int = 0; x < __width; x = x + 1) {
            let stripe:int = x / width;
            if (stripe % 2 == 0) {
                for (let y:int = 0; y < __height; y = y + 1) {
                    __write x, y, #FF0000;
                }
            }
        }
        return true;
    }
    
    // Clear and draw checkerboard
    __clear #808080;
    let squares:int = draw_checkerboard();
    __print squares;
    __delay 2000;
    
    // Clear and draw stripes
    __clear #0000FF;
    let done:bool = draw_stripes(20);
    __delay 2000;
    """
    
    print("\nINPUT PROGRAM:")
    print(test_code)
    
    ast, instructions, error = compile_program(test_code)
    
    if error:
        print_outcome(False, error)
        return False
    
    print_ast(ast, max_lines=100)
    
    print("\nGENERATED PArIR (partial):")
    print("-"*60)
    for i, instr in enumerate(instructions[:120]):
        print(instr)
    if len(instructions) > 120:
        print(f"... ({len(instructions) - 120} more instructions)")
    print("-"*60)
    
    # Count modulo operations
    mod_count = sum(1 for instr in instructions if "mod" in instr)
    print(f"\nModulo operations found: {mod_count}")
    
    if mod_count < 3:
        print_outcome(False, f"Expected at least 3 modulo operations, found {mod_count}")
        return False
    else:
        print_outcome(True)
        return True


def test_array_graphics():
    """Test graphics using arrays"""
    print_test_header("Array Graphics",
                     "Using arrays to store and display graphics data")
    
    test_code = """
    fun draw_from_array(pixels:colour[100], startX:int, startY:int) -> bool {
        for (let i:int = 0; i < 100; i = i + 1) {
            let x:int = startX + (i % 10) * 5;
            let y:int = startY + (i / 10) * 5;
            __write_box x, y, 4, 4, pixels[i];
        }
        return true;
    }
    
    // Create gradient array
    let gradient:colour[] = [
        #000000, #111111, #222222, #333333, #444444,
        #555555, #666666, #777777, #888888, #999999
    ];
    
    // Create pattern
    let pattern:colour[100];
    for (let i:int = 0; i < 100; i = i + 1) {
        pattern[i] = gradient[i % 10];
    }
    
    // Draw the pattern
    __clear #FFFFFF;
    let success:bool = draw_from_array(pattern, 50, 50);
    
    __delay 2000;
    """
    
    print("\nINPUT PROGRAM:")
    print(test_code)
    
    ast, instructions, error = compile_program(test_code)
    
    if error:
        print_outcome(False, error)
        return False
    
    print_ast(ast, max_lines=100)
    
    print(f"\nGenerated {len(instructions)} instructions")
    
    # Verify array and graphics operations
    required = ["pusha", "sta", "push +[", "writebox", "clear"]
    found = {req: any(req in instr for instr in instructions) for req in required}
    
    missing = [req for req, found in found.items() if not found]
    
    if missing:
        print_outcome(False, f"Missing required operations: {missing}")
        return False
    else:
        print_outcome(True)
        return True


def test_complex_animation():
    """Test complex animation combining multiple features"""
    print_test_header("Complex Animation",
                     "Animation using functions, arrays, and all graphics features")
    
    test_code = """
    fun hsv_to_colour(h:int, s:int, v:int) -> colour {
        // Simplified HSV to RGB (h: 0-360, s: 0-100, v: 0-100)
        let region:int = h / 60;
        let remainder:int = h % 60;
        
        let r:int = 0;
        let g:int = 0;
        let b:int = 0;
        
        if (region == 0) {
            r = v; g = remainder * v / 60; b = 0;
        } else {
            if (region == 1) {
                r = (60 - remainder) * v / 60; g = v; b = 0;
            } else {
                r = 0; g = v; b = remainder * v / 60;
            }
        }
        
        return (r * 65536 + g * 256 + b) as colour;
    }
    
    fun animate_frame(frame:int) -> bool {
        for (let x:int = 0; x < __width; x = x + 5) {
            for (let y:int = 0; y < __height; y = y + 5) {
                let h:int = (x + y + frame) % 360;
                let color:colour = hsv_to_colour(h, 100, 100);
                __write_box x, y, 4, 4, color;
            }
        }
        return true;
    }
    
    // Animation loop
    for (let frame:int = 0; frame < 60; frame = frame + 1) {
        let success:bool = animate_frame(frame * 6);
        __delay 16;  // ~60 FPS
    }
    """
    
    print("\nINPUT PROGRAM:")
    print(test_code)
    
    ast, instructions, error = compile_program(test_code)
    
    if error:
        print_outcome(False, error)
        return False
    
    print_ast(ast, max_lines=150)
    
    print(f"\nGenerated {len(instructions)} instructions")
    
    # This is a complex program, just verify it compiles
    print_outcome(True)
    return True


def run_simulator_tests():
    """Run all simulator test programs"""
    print("SIMULATOR TEST PROGRAMS")
    print("="*80)
    print("Testing programs that should work correctly in the PArL simulator")
    
    results = []
    
    # Run all tests
    results.append(("Simple Color Animation", test_simple_color_animation()))
    results.append(("MaxInArray Function", test_max_in_array()))
    results.append(("Color Functions", test_color_functions()))
    results.append(("Color Animation While", test_color_animation_while()))
    results.append(("Rainbow Pattern", test_rainbow_pattern()))
    results.append(("Screen Operations", test_screen_operations()))
    results.append(("Modulo Patterns", test_modulo_patterns()))
    results.append(("Array Graphics", test_array_graphics()))
    results.append(("Complex Animation", test_complex_animation()))
    
    # Summary
    print("\n" + "="*80)
    print("SIMULATOR TESTS SUMMARY")
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
    success = run_simulator_tests()
    sys.exit(0 if success else 1)