# PArL Compiler Implementation
A complete compiler for the Pixel Art Language (PArL), translating high-level graphics programming code into PArIR (Pixel Art Intermediate Representation) instructions for the PAD2000c display device.

## Overview
This project implements a full compilation pipeline for PArL, a strongly-typed, expression-based language with C-style syntax designed for programming pixel art displays. The compiler features:

Table-driven FSA-based lexical analyzer with comprehensive error detection
Hand-crafted recursive descent LL(k) parser generating abstract syntax trees (ASTs)
Semantic analyzer with visitor pattern implementation for type checking and validation
Stack-based code generator producing optimized PArIR instructions
Full array support with compile-time size verification

## Features

### Language Support:

Four primitive types: int, float, bool, and colour
Function declarations with typed parameters and return values
Control flow constructs (if-else, while, for loops)
Built-in functions for display manipulation (__write, __write_box, etc.)
Type casting with the as operator
Fixed-size arrays with element access and function passing


### Compiler Features:

Comprehensive error reporting with line/column information
Error recovery for continued compilation after syntax errors
Type safety with no implicit conversions
Forward function references and mutual recursion support
Modulo operator (%) support for integer operations



### Project Structure
<pre>
Assignment/
├── lexer/              # FSA-based tokenizer
├── parser/             # Recursive descent parser & AST nodes
├── semantic_analyzer/  # Type checking and semantic validation
├── code_generator/     # PArIR instruction generation
├── test/              # Comprehensive test suite
└── test_outputs/      # Test results and generated code
</pre>

## Installation & Usage
### Prerequisites

Python 3.8 or higher
No external dependencies required (uses only Python standard library)

## Running Tests
### Run all tests:
<pre>
python -m test.run_all_tests
</pre>
### Run specific test suite:
<pre>
python -m test.test_task1  # Lexer tests
python -m test.test_task2  # Parser tests
python -m test.test_task3  # Semantic analysis tests
python -m test.test_task4  # Code generation tests
python -m test.test_task5  # Array support tests
</pre>
