# Assignment Overview

This project implements a lexical analyzer and parser for the SomeWMULife programming language, a simplified subset of Pascal designed for instructional use. The project was completed using the PLY (Python Lex-Yacc) library and supports:

* Tokenization (lexical analysis)

* Parsing using BNF grammar

* Construction of an Abstract Syntax Tree (AST)

* Basic semantic analysis and type checking

* Error detection

* Level-order traversal of the AST

* Automated testing and validation

## Language Features Implemented

The following features from the SomeWMULife specification are implemented:

### Data Types

* INTEGER

* FLOAT

* ARRAY [low..high] OF INTEGER

* ARRAY [low..high] OF FLOAT

* Operators

* Arithmetic: + , - , * , /

* Relational: < , <= , > , >= , = , <>

* Logical: AND , OR , NOT

* Assignment: :=

### Control Flow

* IF ... THEN ... ELSE

* WHILE ... DO

* BEGIN ... END

### Input / Output

* READ(variable)

* WRITE(expression)

* WRITE('string')

### Other Features

* One-dimensional arrays

* Scientific notation floats

* Case-sensitive identifiers

* Reserved uppercase keywords

* Comment format { ... }

### Files Included


```python lexer.py```

### How to Run (Mac / Linux)

Make sure PLY is installed:

```pip3 install ply```

### Part 1 – Lexical Analyzer

Run lexer on a single file:

```python3 lexer.py < test1_basic.sml```


### Example output:

```{"type": "token_list", "tokens": ["PROGRAM:PROGRAM", "ID:BasicTest", ...]}```

### Part 2 – Parser with AST

Run the parser on one file:

```python3 parser.py test1_basic.sml```


Output:

* Symbol table

* Level-order traversal of the AST

### Run All Tests Automatically
```python3 run_tests.py```


This script runs the parser on all .sml files and reports:

✅ Success for valid programs

❌ Errors for invalid test cases

### AST Output Format

The parse tree is displayed using level-order traversal:

Nodes on the same level are separated by:

# 


Levels are separated by two blank lines

Example:

```
Program(Sample)


VarDecl(x,y) # Compound


StandardType(INTEGER) # Assign # Write
 ```
### Semantic Analysis Summary

The following checks are performed:

✔ Duplicate declarations

✔ Undeclared variables

✔ Type-compatible assignments

✔ Array index validity

✔ Integer coercion to Float

✔ Logical operator rules

✔ Integer-only NOT operator

✔ Relational operators return integer

Errors are reported with meaningful messages:

```Type error: Undeclared identifier 'b'```

### Testing Strategy

Testing covered:

✔ Arithmetic expressions

✔ Mixed INT / FLOAT coercion

✔ IF and WHILE

✔ Arrays

✔ Logical expressions

✔ WRITE and READ

✔ Nested control flow

✔ Incorrect input programs


Typescript (Terminal Log)

### The terminal transcript is recorded in a file called:

```typescript```


This file contains:

Commands used to run the lexer

Commands used to run the parser

* All program outputs

* All error messages

* This confirms actual execution and meets assignment traceability requirements.

### Tools and Environment

Python 3

* PLY (Python Lex-Yacc)

* macOS Terminal

* Unix script utility

