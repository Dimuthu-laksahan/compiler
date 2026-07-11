import os
import sys
import argparse

from lexer import LexicalAnalyzer
from syntax_analyzer import SyntaxAnalyzer
from semantic_analyzer import SemanticAnalyzer
from intermediate_code_generator import IntermediateCodeGenerator
from code_generator import AssemblyCodeGenerator

def compile_source(source_code, output_file, verbose=False):
    print("------- Compilation Started -------")
    
    # 1. Lexical Analysis
    print("1. Running Lexical Analyxer...")
    lexer = LexicalAnalyzer()
    tokens, lex_errors = lexer.tokenize(source_code)
    
    if lex_errors:
        print("\n[ERROR] COMPILATION FAILED: Lexical Errors Detected", file=sys.stderr)
        for err in lex_errors:
            print(f"  {err}", file=sys.stderr)
        return False

    print(" ------ Lexical Analysis passed.")

    # 2. Syntax Analysis
    print("2. Running Syntax Analysis...")
    parser = SyntaxAnalyzer(tokens)
    ast, parse_errors = parser.parse()
    
    if parse_errors:
        print("\n[ERROR] COMPILATION FAILED: Syntax Errors Detected", file=sys.stderr)
        for err in parse_errors:
            print(f"  {err}", file=sys.stderr)
        return False

    print(" ------ Syntax Analysis passed.")

    # 3. Semantic Analysis
    print("3. Running Semantic Analysis...")
    semantic_analyzer = SemanticAnalyzer(ast)
    success = semantic_analyzer.analyze()
    
 
    if semantic_analyzer.warnings:
        print("\n[WARNING] Semantic Warnings:", file=sys.stderr)
        for warn in semantic_analyzer.warnings:
            print(f"  {warn}", file=sys.stderr)
            
    if not success or semantic_analyzer.errors:
        print("\n[ERROR] COMPILATION FAILED: Semantic Errors Detected", file=sys.stderr)
        for err in semantic_analyzer.errors:
            print(f"  {err}", file=sys.stderr)
        return False

    print(" ------ Semantic Analysis passed.")

    # 4. Intermediate Code Generation (TAC)
    print("4. Generating Intermediate Code (TAC)...")
    icg = IntermediateCodeGenerator(ast)
    tac_instructions = icg.generate()
    if verbose:
        print("\n--- Three-Address Code (TAC) ---")
        icg.print_code()
        print("-" * 32)
    print(" ------ Intermediate Code generated successfully.")

    # 5. Target Code Generation (Assembly)
    print("5. Generating Target Assembly Code (x86-64)...")
    asm_gen = AssemblyCodeGenerator(tac_instructions)
    assembly_code = asm_gen.generate()
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(assembly_code)
        print(f" ------ Assembly code written to '{output_file}'.")
    except Exception as e:
        print(f"\n[ERROR] Error writing assembly file: {e}", file=sys.stderr)
        return False

    print("\n[SUCCESS] COMPILATION SUCCESSFUL!")
    return True

def main():
    parser = argparse.ArgumentParser(description="Compiler Driver for custom language.")
    parser.add_argument("input_file", nargs="?", default="input.txt", help="Path to the input source file (default: input.txt)")
    parser.add_argument("-o", "--output", default="output.asm", help="Path to write the target assembly code (default: output.asm)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose details (e.g. intermediate code)")
    
    args = parser.parse_args()
    
    input_path = args.input_file
    output_path = args.output
    
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)
        
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except Exception as e:
        print(f"Error: Could not read input file '{input_path}': {e}", file=sys.stderr)
        sys.exit(1)
        
    success = compile_source(source_code, output_path, args.verbose)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
