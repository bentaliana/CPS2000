"""
Test runner for PArL to PArIR Code Generator
Tests the complete compilation pipeline
"""

import sys
import os
from typing import List, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer.lexer import FSALexer
from parser.parser import PArLParser
from semantic_analyzer.semantic_analyzer import SemanticAnalyzer
from code_generator.code_generator import PArIRGenerator


class CompilerPipeline:
    """Complete compiler pipeline from PArL to PArIR"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.lexer = FSALexer()
        self.parser = None
        self.analyzer = SemanticAnalyzer()
        self.generator = PArIRGenerator(debug=debug)
    
    def compile(self, source_code: str) -> Optional[List[str]]:
        """Compile PArL source code to PArIR instructions"""
        print("=" * 60)
        print("COMPILATION PIPELINE")
        print("=" * 60)
        
        # Step 1: Lexical Analysis
        print("\n1. LEXICAL ANALYSIS")
        print("-" * 30)
        tokens = self.lexer.tokenize(source_code)
        
        # Check for lexical errors
        error_tokens = [t for t in tokens if t.type.name.startswith("ERROR")]
        if error_tokens:
            print(f"Lexical errors found: {len(error_tokens)}")
            for error in error_tokens:
                print(f"  - {error}")
            return None
        
        print(f"Tokens generated: {len(tokens)}")
        if self.debug:
            for token in tokens[:10]:  # Show first 10 tokens
                print(f"  {token}")
            if len(tokens) > 10:
                print(f"  ... and {len(tokens) - 10} more")
        
        # Step 2: Parsing
        print("\n2. PARSING")
        print("-" * 30)
        self.parser = PArLParser(tokens)
        
        try:
            ast = self.parser.parse()
            print("Parsing successful!")
            if self.debug:
                print("\nAST Structure:")
                print(str(ast)[:500] + "..." if len(str(ast)) > 500 else str(ast))
        except Exception as e:
            print(f"Parsing failed: {e}")
            return None
        
        # Step 3: Semantic Analysis
        print("\n3. SEMANTIC ANALYSIS")
        print("-" * 30)
        
        if not self.analyzer.analyze(ast):
            print(f"Semantic errors found: {len(self.analyzer.errors)}")
            for error in self.analyzer.errors:
                print(f"  - {error}")
            return None
        
        print("Semantic analysis passed!")
        
        # Step 4: Code Generation
        print("\n4. CODE GENERATION")
        print("-" * 30)
        
        try:
            instructions = self.generator.generate(ast)
            print(f"Code generation successful! {len(instructions)} instructions generated")
            return instructions
        except Exception as e:
            print(f"Code generation failed: {e}")
            if self.debug:
                import traceback
                traceback.print_exc()
            return None
    
    def compile_file(self, filename: str) -> Optional[List[str]]:
        """Compile a PArL file"""
        try:
            with open(filename, 'r') as f:
                source_code = f.read()
            return self.compile(source_code)
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            return None
        except Exception as e:
            print(f"Error reading file: {e}")
            return None


def test_simple_program():
    """Test with a simple PArL program"""
    source = """
    let c:colour = 0 as colour;

    for (let i:int = 0; i < 64; i = i + 1) {
        c = (__randi 1677216) as colour;
        __clear c;

        __delay 16;
}
    """
    
    print("\nTEST: Simple Variable Declaration and Arithmetic")
    print("Source code:")
    print(source)
    
    pipeline = CompilerPipeline(debug=False)
    instructions = pipeline.compile(source)
    
    if instructions:
        print("\nGenerated PArIR code:")
        print("-" * 40)
        for inst in instructions:
            print(inst)


def test_color_animation():
    """Test color animation with cast and built-ins"""
    source = """
    fun color() -> colour
    {
        return (__randi 16384257 - #f9f9f9 as int) as colour;
    }

    fun cc(x:int, y:int) -> bool
    {
        __print x;
        __print y;

        let c:colour = color();
        let h:int = __randi __height;
        let w:int = __randi __width;
        __write w,h,c;

        return true;
    }

    let a:bool = cc(0, 0);
    __delay 1000;

    """
    
    print("\n\nTEST: Color Animation with Cast and Built-ins")
    print("Source code:")
    print(source)
    
    pipeline = CompilerPipeline(debug=False)
    instructions = pipeline.compile(source)
    
    if instructions:
        print("\nGenerated PArIR code:")
        print("-" * 40)
        for inst in instructions:
            print(inst)


def run_all_tests():
    """Run all test cases"""
    print("RUNNING ALL PARL TO PARIR COMPILATION TESTS")
    print("=" * 80)
    
    test_functions = [
        test_simple_program,
        # test_control_flow,
        # test_for_loop,
        # test_function,
        test_color_animation # New test added here
        # test_builtin_functions,
        # test_type_casting
    ]
    
    for test_func in test_functions:
        try:
            test_func()
        except Exception as e:
            print(f"\nERROR in {test_func.__name__}: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 80)
    
    print("ALL TESTS COMPLETED")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        if test_name == "simple":
            test_simple_program()
        elif test_name == "color":
            test_color_animation()
        else:
            print(f"Unknown test: {test_name}")
            print("Available tests: simple, control, for, function, color, builtin, cast")
    else:
        # Run all tests
        run_all_tests()