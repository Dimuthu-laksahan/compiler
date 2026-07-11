  parser = argparse.ArgumentParser(description="Compiler Driver for custom language.")
    parser.add_argument("input_file", nargs="?", default="input.txt", help="Path to the input source file (default: input.txt)")
    parser.add_argument("-o", "--output", default="output.asm", help="Path to write the target assembly code (default: output.asm)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose details (e.g. intermediate code)")
    
    args = parser.parse_args()
    
    input_path = args.input_file
    output_path = args.output