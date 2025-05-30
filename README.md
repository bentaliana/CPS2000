# PArL Language Compiler

A complete compiler implementation for the PArL (Programming and Rendering Language) programming language, built as part of the CPS2000 Assignment. This compiler translates PArL source code into PArIR (PArL Intermediate Representation) instructions.

## Project Structure

```
├── README.md
├── lexer/
│   ├── __init__.py
│   ├── lexer.py              # FSA-based lexical analyzer
│   └── __pycache__/
├── parser/
│   ├── __init__.py
│   ├── ast_nodes.py          # Abstract Syntax Tree node definitions
│   ├── parser.py             # Recursive descent parser
│   ├── parser_errors.py      # Parser error handling
│   ├── token_stream.py       # Token stream management
│   └── __pycache__/
├── semantic_analyzer/
│   ├── __init__.py
│   ├── semantic_analyzer.py  # Type checking and semantic analysis
│   └── __pycache__/
├── code_generator/
│   ├── __init__.py
│   ├── code_generator.py     # PArIR code generation
│   └── __pycache__/
├── test/
│   ├── __init__.py
│   ├── run_all_tests.py      # Test runner for all tasks
│   ├── test_simulator.py     # Simulator tests
│   ├── test_task1.py         # Lexer tests
│   ├── test_task2.py         # Parser tests
│   ├── test_task3.py         # Semantic analyzer tests
│   ├── test_task4.py         # Code generator tests
│   ├── test_task5.py         # Integration tests
│   └── __pycache__/
└── tests/
    ├── __init__.py
    ├── test_codegen.py       # Code generation test cases
    ├── test_lexer.py         # Lexical analysis test cases
    ├── test_parser.py        # Parser test cases
    ├── test_arrays.py        # Array handling test cases
    ├── test2.py              # Debug compilation pipeline
    └── ...
```
