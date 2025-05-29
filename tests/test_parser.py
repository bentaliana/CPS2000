"""
Simple Parser Test Script - Just Parse and Visualize
Tests parser and shows AST using __str__ methods
"""

from lexer import FSALexer
from parser import PArLParser


def main():
    """Run parser tests with new __str__-based AST printing"""

    print("PArL Parser Test - Task 2")
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
            
            "name": "Function Declaration",
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
            "name": "Built-in Functions",
            "code": '''
                __write 10, 14, #00ff00;
                __delay 100;
                __write_box 10, 14, 2, 2, #0000ff;
            '''
        },
        {
            "name": "For Loop",
            "code": '''
                for (let i:int = 0; i < 10; i = i + 1) {
                    __print i;
                    __delay 1000;
                }
            '''
        },
        {
            "name": "Complex Program - Race Function",
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
            "name": "Missing Semicolon",
            "code": "let x:int = 5"
        },
        {
            "name": "Missing Expression", 
            "code": "let x:int = ;"
        },
        {
            "name": "Invalid Assignment",
            "code": "5 = x;"
        },
        {
            "name": "Invalid Float",
            "code": "let x:float = 123.;"
        },
        {
            "name": "Operator Precedence",
            "code": "let x:int = 1 + 2 * 3;"
        },
        {
            "name": "Parentheses Override", 
            "code": "let x:int = (1 + 2) * 3;"
        },
        {
            "name": "Cast Precedence",
            "code": "let x:float = a + b as float;"
        },
        {
            "name": "XGreaterY_2 Function",
            "code": '''
                fun XGreaterY_2(x:int, y:int) -> bool {
                    return x > y;
                }
            '''
        },
        {
            "name": "AverageOfTwo Function",
            "code": '''
                fun AverageOfTwo(x:int, y:int) -> float {
                    let t0:int = x + y;
                    let t1:float = t0 / 2 as float;
                    return t1;
                }
            '''
        },
        {
            "name": "Max Function",
            "code": '''
                fun Max(x:int, y:int) -> int {
                    let m:int = x;
                    if (y > m) { m = y; }
                    return m;
                }
            '''
        },
        {
            "name": "All Built-ins",
            "code": '''
                let w:int = __width;
                let h:int = __height;
                let r:int = __randi 100;
                __clear #ff0000;
            '''
        },
        {
            "name": "Unary Operators",
            "code": '''
                let x:int = -5;
                let y:bool = not true;
                let z:int = -(-3);
                let w:bool = not (5 > 3);
            '''
        },
        {
            "name": "Complex Expression Precedence", 
            "code": '''
                let result:bool = 5 > 3 and 2 < 4 or not false;
                let math:int = -2 * 3 + 4 / 2;
                let comp:bool = not 5 == 3 and 7 >= 2;
            '''
        },
        {
            "name": "Nested Function Calls",
            "code": '''
                fun Add(a:int, b:int) -> int { return a + b; }
                fun Multiply(a:int, b:int) -> int { return a * b; }
                let result:int = Add(Multiply(2, 3), Add(1, 1));
            '''
        },
        {
            "name": "Empty Function Parameters",
            "code": '''
                fun GetZero() -> int { return 0; }
                let x:int = GetZero();
            '''
        },
        {
            "name": "All Cast Types",
            "code": '''
                let a:float = 5 as float;
                let b:colour = 255 as colour;
                let c:int = (3.14 + 2.86) as int;
            '''
        },
        {
            "name": "Deeply Nested Blocks",
            "code": '''
                if (true) {
                    if (false) {
                        { 
                            let x:int = 1;
                            { 
                                let y:int = 2;
                                __print y;
                            }
                        }
                    } else {
                        let z:int = 3;
                    }
                }
            '''
        },
        {
            "name": "Invalid Function Call Statement",
            "code": "someUndefinedFunc(1, 2, 3);"
        },
        {
            "name": "Missing Function Body", 
            "code": "fun Test() -> int"
        },
        {
            "name": "Invalid Cast Target",
            "code": "let x:string = 5 as string;"
        },
        {
            "name": "Malformed For Loop",
            "code": "for (let i:int = 0 i < 10; i = i + 1) { }"
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {test_case['name']}")
        print(f"{'='*60}")
        
        lexer = FSALexer()
        tokens = lexer.tokenize(test_case['code'].strip())
        
        if not lexer.report_errors(tokens):
            print("Lexical analysis failed")
            continue
        
        parser = PArLParser(tokens)
        try:
            ast = parser.parse()
        except Exception as e:
            print(f"Parser error: {e}")
            continue
        
        if not parser.report_errors():
            print("Parsing failed")
            continue

        print("Parsing successful!\n")
        print("AST Output:")
        print("-" * 40)
        try:
            print(ast)
        except Exception as e:
            print(f"AST print error: {e}")
        
        if i < len(test_cases):
            input("\nPress Enter to continue to next test...")

    print(f"\n{'='*60}")
    print("All tests completed!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
