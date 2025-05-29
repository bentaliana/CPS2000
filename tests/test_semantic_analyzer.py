"""
Semantic Analyzer Test Script - Task 3
Tests semantic analyzer and shows detailed error reporting
"""

from lexer import FSALexer
from parser import PArLParser
from semantic_analyzer import SemanticAnalyzer


def main():
    """Run semantic analyzer tests"""

    print("PArL Semantic Analyzer Test - Task 3")
    print("=" * 50)

    test_cases = [
         {
            "name": "Example 1",
            "code": '''
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

            '''
        },
           {
            "name": "Example 2",
            "code": '''
               let c:colour = 0 as colour;

                for (let i:int = 0; i < 64; i = i + 1) {
                    c = (__randi 1677216) as colour;
                    __clear c;

                    __delay 16;
                }

            '''
        },
        {
            "name": "Valid Function Declaration",
            "code": '''
                fun XGreaterY(x:int, y:int) -> bool {
                    let ans:bool = true;
                    if (y > x) { 
                        ans = false; 
                    }
                    return ans;
                }
            '''
        },
        {
            "name": "Valid Built-in Usage",
            "code": '''
                let w:int = __width;
                let h:int = __height;
                let color:colour = #00ff00;
                __write 10, 14, color;
                __delay 100;
                __write_box 10, 14, 2, 2, #0000ff;
                __clear color;
            '''
        },
        {
            "name": "Valid Complex Program",
            "code": '''
                fun Max(x:int, y:int) -> int {
                    let result:int = x;
                    if (y > x) {
                        result = y;
                    }
                    return result;
                }
                
                let a:int = 10;
                let b:int = 20;
                let max_val:int = Max(a, b);
                __print max_val;
            '''
        },
        {
            "name": "Valid For Loop with Scope",
            "code": '''
                for (let i:int = 0; i < 10; i = i + 1) {
                    let temp:int = i * 2;
                    __print temp;
                }
                let i:int = 100;  // Valid: different scope
            '''
        },
        {
            "name": "Valid Type Casting",
            "code": '''
                let x:int = 5;
                let y:float = x as float;
                let z:colour = 255 as colour;
                let w:bool = 1 as bool;
            '''
        },
        {
            "name": "ERROR: Variable Redeclaration",
            "code": '''
                let x:int = 5;
                let x:float = 3.14;  // Error: redeclared in same scope
            '''
        },
        {
            "name": "ERROR: Function Redeclaration",
            "code": '''
                fun Test(x:int) -> int { return x; }
                fun Test(y:float) -> float { return y; }  // Error: redeclared
            '''
        },
        {
            "name": "ERROR: Type Mismatch in Assignment",
            "code": '''
                let x:int = 5;
                let y:bool = true;
                x = y;  // Error: cannot assign bool to int
            '''
        },
        {
            "name": "ERROR: Type Mismatch in Variable Declaration",
            "code": '''
                let x:int = true;  // Error: cannot initialize int with bool
                let y:bool = 3.14;  // Error: cannot initialize bool with float
            '''
        },
        {
            "name": "ERROR: Undeclared Variable",
            "code": '''
                let x:int = undeclared_var + 5;  // Error: undeclared_var not declared
                y = 10;  // Error: y not declared
            '''
        },
        {
            "name": "ERROR: Undeclared Function",
            "code": '''
                let result:int = UndeclaredFunc(5, 10);  // Error: function not declared
            '''
        },
        {
            "name": "ERROR: Function Missing Return",
            "code": '''
                fun ShouldReturnInt(x:int) -> int {
                    let y:int = x + 1;
                    // Error: missing return statement
                }
            '''
        },
        {
            "name": "ERROR: Wrong Return Type",
            "code": '''
                fun ShouldReturnBool(x:int) -> bool {
                    return x + 1;  // Error: returning int instead of bool
                }
            '''
        },
        {
            "name": "ERROR: Return Outside Function",
            "code": '''
                let x:int = 5;
                return x;  // Error: return statement outside function
            '''
        },
        {
            "name": "ERROR: Invalid Binary Operation",
            "code": '''
                let x:int = 5;
                let y:bool = true;
                let z:int = x + y;  // Error: cannot add int and bool
            '''
        },
        {
            "name": "ERROR: Invalid Unary Operation",
            "code": '''
                let x:colour = #ff0000;
                let y:colour = -x;  // Error: cannot negate colour
                let z:int = not 5;  // Error: cannot apply not to int
            '''
        },
        {
            "name": "ERROR: Invalid Cast",
            "code": '''
                let x:bool = true;
                let y:float = x as float;  // Error: cannot cast bool to float
            '''
        },
        {
            "name": "ERROR: Function Argument Count Mismatch",
            "code": '''
                fun Add(x:int, y:int) -> int { return x + y; }
                let result:int = Add(5);  // Error: expects 2 arguments, got 1
            '''
        },
        {
            "name": "ERROR: Function Argument Type Mismatch",
            "code": '''
                fun Add(x:int, y:int) -> int { return x + y; }
                let result:int = Add(5, true);  // Error: second arg should be int, got bool
            '''
        },
        {
            "name": "ERROR: Invalid Built-in Arguments",
            "code": '''
                let x:bool = true;
                __write x, 10, #ff0000;  // Error: x coord must be int, got bool
                __delay #ff0000;  // Error: delay expects int, got colour
                __clear 42;  // Error: clear expects colour, got int
            '''
        },
        {
            "name": "ERROR: Non-Boolean Condition",
            "code": '''
                let x:int = 5;
                if (x) {  // Error: condition must be bool, got int
                    __print x;
                }
                while (x + 1) {  // Error: condition must be bool, got int
                    x = x - 1;
                }
            '''
        },
        {
            "name": "ERROR: Invalid For Loop Condition",
            "code": '''
                for (let i:int = 0; i; i = i + 1) {  // Error: condition must be bool, got int
                    __print i;
                }
            '''
        },
        {
            "name": "Complex Valid Program - Race Function",
            "code": '''
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

                let c1:colour = #00ff00;
                let c2:colour = #0000ff;
                let m:int = __height;
                let w:int = Race(c1, c2, m);
                __print w;
            '''
        },
        {
            "name": "Nested Scopes and Variable Shadowing",
            "code": '''
                let x:int = 10;
                if (true) {
                    let x:int = 20;  // Valid: different scope
                    if (true) {
                        let x:int = 30;  // Valid: different scope
                        __print x;  // prints 30
                    }
                    __print x;  // prints 20
                }
                __print x;  // prints 10
            '''
        },
        {
            "name": "Function Parameters and Local Variables",
            "code": '''
                fun TestScope(param:int) -> int {
                    let local:int = param * 2;
                    if (param > 0) {
                        let nested:int = local + param;
                        return nested;
                    }
                    return local;
                }
                
                let result:int = TestScope(5);
            '''
        },
        {
            "name": "All Operator Types",
            "code": '''
                let a:int = 5;
                let b:int = 3;
                let c:float = 2.5;
                let d:float = 1.5;
                let flag1:bool = true;
                let flag2:bool = false;
                
                // Arithmetic
                let sum:int = a + b;
                let diff:int = a - b;
                let prod:int = a * b;
                let quot:int = a / b;
                
                let fsum:float = c + d;
                let fdiff:float = c - d;
                let fprod:float = c * d;
                let fquot:float = c / d;
                
                // Comparison
                let cmp1:bool = a > b;
                let cmp2:bool = a < b;
                let cmp3:bool = a >= b;
                let cmp4:bool = a <= b;
                let cmp5:bool = a == b;
                let cmp6:bool = a != b;
                
                // Logical
                let and_result:bool = flag1 and flag2;
                let or_result:bool = flag1 or flag2;
                
                // Unary
                let neg:int = -a;
                let not_flag:bool = not flag1;
            '''
        },
        {
            "name": "ERROR: Parameter Redeclaration",
            "code": '''
                fun Test(x:int, x:float) -> int {  // Error: parameter x redeclared
                    return 0;
                }
            '''
        },
        {
            "name": "ERROR: Parameter Name Conflict with Local",
            "code": '''
                fun MoreThan50(x:int) -> bool {
                    let x:int = 23; //syntax ok, but this should not be allowed!!
                    if (x <= 50) {
                        return false;
                    }
                return true;
                }
            '''
        }
    ]

    passed = 0
    failed = 0

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {test_case['name']}")
        print(f"{'='*60}")
        
        # Lexical analysis
        lexer = FSALexer()
        tokens = lexer.tokenize(test_case['code'].strip())
        
        if not lexer.report_errors(tokens):
            print("Lexical analysis failed")
            failed += 1
            continue
        
        # Parsing
        parser = PArLParser(tokens)
        try:
            ast = parser.parse()
        except Exception as e:
            print(f"Parser error: {e}")
            failed += 1
            continue
        
        if not parser.report_errors():
            print("Parsing failed")
            failed += 1
            continue

        # Semantic analysis
        analyzer = SemanticAnalyzer()
        success = analyzer.analyze(ast)
        
        # Determine expected outcome
        is_error_test = test_case['name'].startswith("ERROR:")
        
        if is_error_test:
            # Error test - should fail semantic analysis
            if not success:
                print("Semantic analysis correctly detected errors:")
                analyzer.report_errors()
                passed += 1
            else:
                print("Expected semantic errors but analysis passed!")
                failed += 1
        else:
            # Valid test - should pass semantic analysis
            if success:
                print("Semantic analysis passed!")
                print("Symbol table and types verified successfully.")
                passed += 1
            else:
                print("Unexpected semantic analysis failure:")
                analyzer.report_errors()
                failed += 1
        
        if i < len(test_cases):
            input("\nPress Enter to continue to next test...")

    print(f"\n{'='*60}")
    print("SEMANTIC ANALYSIS TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total tests: {len(test_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("All tests passed! Semantic analyzer is working perfectly!")
    else:
        print(f"{failed} tests failed. Check implementation.")
    
    print(f"{'='*60}")


def test_symbol_table():
    """Test symbol table functionality separately"""
    print(f"\n{'='*60}")
    print("SYMBOL TABLE FUNCTIONALITY TEST")
    print(f"{'='*60}")
    
    code = '''
        fun TestFunc(param1:int, param2:bool) -> float {
            let local1:int = param1 + 1;
            if (param2) {
                let local2:float = local1 as float;
                return local2;
            }
            return 0.0 as float;
        }
        
        let global1:int = 42;
        let global2:colour = #ff0000;
    '''
    
    lexer = FSALexer()
    tokens = lexer.tokenize(code)
    
    if not lexer.report_errors(tokens):
        print("Lexical analysis failed")
        return
    
    parser = PArLParser(tokens)
    try:
        ast = parser.parse()
    except Exception as e:
        print(f"Parser error: {e}")
        return
    
    if not parser.report_errors():
        print("Parsing failed")
        return
    
    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(ast)
    
    if success:
        print("Symbol table test passed!")
        print("\nFunctions in symbol table:")
        for name, symbol in analyzer.symbol_table.functions.items():
            if not name.startswith("__"):  # Skip built-ins for cleaner output
                print(f"  {symbol}")
        
        print("\nBuilt-in functions available:")
        builtin_count = sum(1 for name in analyzer.symbol_table.functions.keys() if name.startswith("__"))
        print(f"  {builtin_count} built-in functions registered")
    else:
        print("Symbol table test failed:")
        analyzer.report_errors()


if __name__ == "__main__":
    """Run comprehensive tests of the semantic analyzer"""
    main()
    test_symbol_table()