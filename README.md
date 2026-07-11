# 🛠️ Custom x86-64 Compiler Pipeline

A lightweight, multi-stage compiler written in Python that translates a custom imperative, C-like language into executable-ready **x86-64 NASM Assembly**. 

This compiler processes source code through the classic phases of compilation: lexical analysis, recursive descent parsing, semantic analysis (including type checking and scoping), intermediate code generation (Three-Address Code), and final target code generation.

---

## 📐 Compiler Architecture

The following diagram illustrates the flow of code through the different compiler stages:

<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/ec3be5a0-1d14-4314-8923-43cb39ddb48e" />


## ⚡ Features

- **Lexical Analysis**: Matches tokens using regular expressions, stripping comments (single/multi-line), and capturing syntax errors such as malformed numbers, invalid identifiers, and unterminated strings.
- **Recursive Descent Parser**: Builds a custom Abstract Syntax Tree (AST) representing statements (`if`, `while`, `for`, `print`, assignment, and blocks) and expressions (relational, arithmetic, logical, and unary operators).
- **Scope & Semantic Checking**:
  - Automatically declares variables on assignment.
  - Supports hierarchical, nested scoping (e.g., local block scopes, loop-level scopes).
  - Infers expression types (`int`, `float`, `string`) and validates compatibility (e.g., condition checks, type mismatch warnings on variable reuse).
  - Emits compilation errors for undefined variables and warnings for uninitialized uses.
- **Intermediate Representation (TAC)**: Compiles the hierarchical AST into linear Three-Address Code instructions utilizing temporary variables and labels.
- **Target Code Generation**: Translates TAC instructions into clean, human-readable **x86-64 NASM assembly code** with a standard main entry point setup, C-std `printf` integration for console printing, and full memory allocation mapping for variables in the `.data` section.

---

## 📁 Repository Structure

| File | Description |
| :--- | :--- |
| **[`compiler.py`](file:///C:/Users/MSI/Desktop/projects/compiler/compiler.py)** | The compiler driver. Coordinates all phases and handles command line flags. |
| **[`lexer.py`](file:///C:/Users/MSI/Desktop/projects/compiler/lexer.py)** | Tokenizer. Matches keywords, symbols, and literals; reports lexical errors. |
| **[`syntax_analyzer.py`](file:///C:/Users/MSI/Desktop/projects/compiler/syntax_analyzer.py)** | Parser. Translates tokens into an AST using recursive descent. |
| **[`semantic_analyzer.py`](file:///C:/Users/MSI/Desktop/projects/compiler/semantic_analyzer.py)** | Checks scope constraints, variable initialization, and infers/checks types. |
| **[`intermediate_code_generator.py`](file:///C:/Users/MSI/Desktop/projects/compiler/intermediate_code_generator.py)** | Converts AST to linear Three-Address Code (TAC) instructions. |
| **[`code_generator.py`](file:///C:/Users/MSI/Desktop/projects/compiler/code_generator.py)** | Backend compiler. Emits x86-64 NASM assembly based on TAC instructions. |
| **[`input.txt`](file:///C:/Users/MSI/Desktop/projects/compiler/input.txt)** | Sample source code program to be compiled. |
| **[`output.asm`](file:///C:/Users/MSI/Desktop/projects/compiler/output.asm)** | The compiled output containing target x86-64 assembly. |

---

## 📝 Language Syntax

The compiler supports a simple C-like imperative syntax:

```c
// Variable assignment (types are inferred)
x = 60;
y = -2.5;

// Printing strings or expressions
print("Hello World");

// Conditional statements
if (x > 5) {
    y = y + x;
}

// Loops
while (x > 0) {
    x = x - 1;
}
```

---

## 🚀 Running the Compiler

### Prerequisites
- Python 3.x
- (Optional) **NASM** (Netwide Assembler) & **GCC** to assemble and run the output.

### Compilation
To run the compiler driver and compile your code, execute:

```bash
python compiler.py input.txt -o output.asm
```

### Options
- `-o <filename>`: Specify the output assembly file (defaults to `output.asm`).
- `-v`, `--verbose`: Print verbose details during compilation, including the generated Three-Address Code (TAC) representation.

```bash
python compiler.py input.txt -o output.asm --verbose
```

### Assembling and Linking (Windows / Linux)
Once you have generated the `output.asm` file, you can assemble and link it using NASM and GCC:

**On Linux (64-bit):**
```bash
nasm -f elf64 output.asm -o output.o
gcc -no-pie output.o -o output
./output
```

**On Windows (64-bit MinGW-w64):**
```bash
nasm -f win64 output.asm -o output.obj
gcc output.obj -o output.exe
./output.exe
```

---

## 🛠️ Diagnostics & Error Handling

The compiler provides detailed error output at every phase of compilation.

1. **Lexical Errors**:
   ```text
   [ERROR] COMPILATION FAILED: Lexical Errors Detected
     Lexical Error: Malformed number '1.2.3' at line 5
   ```
2. **Syntax Errors**:
   ```text
   [ERROR] COMPILATION FAILED: Syntax Errors Detected
     Syntax Error at line 3: Expected ';', got ID ('y')
   ```
3. **Semantic Errors**:
   ```text
   [ERROR] COMPILATION FAILED: Semantic Errors Detected
     Semantic Error at line 7: Undefined variable 'z'
     Warning at line 10: Type mismatch in assignment to 'x': expected int, got float
   ```
