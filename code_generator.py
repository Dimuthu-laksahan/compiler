"""
Assembly Target Code Generator for the Compiler
Translates Three-Address Code (TAC) / Intermediate Representation into Target Assembly Code (x86-64 Architecture).
"""

# Target Assembly code generator class. No module dependencies needed here.


class AssemblyCodeGenerator:
    """Generates x86-64 target assembly code from Three-Address Code (TAC) instructions."""

    def __init__(self, tac_instructions):
        self.tac_instructions = tac_instructions
        self.assembly_code = []
        self.data_section = []
        self.string_literals = {}
        self.string_counter = 0
        self.declared_vars = set()

    def add_data(self, line):
        if line not in self.data_section:
            self.data_section.append(line)

    def emit_asm(self, line, comment=None):
        if comment:
            self.assembly_code.append(f"    {line:<30} ; {comment}")
        else:
            self.assembly_code.append(f"    {line}")

    def emit_label(self, label):
        self.assembly_code.append(f"{label}:")

    def register_variable(self, var_name):
        """Track variables and temporaries for the .data section."""
        if not var_name:
            return
        # If it's a string literal or number literal, don't declare as scalar variable
        if var_name.startswith('"') and var_name.endswith('"'):
            if var_name not in self.string_literals:
                self.string_counter += 1
                lbl = f"str_{self.string_counter}"
                self.string_literals[var_name] = lbl
                self.add_data(f"    {lbl} db {var_name}, 0")
        elif not var_name.replace('.', '', 1).replace('-', '', 1).isdigit():
            self.declared_vars.add(var_name)

    def load_operand(self, reg, operand, comment=None):
        """Loads an operand (literal or memory variable) into a register."""
        if operand in self.string_literals:
            lbl = self.string_literals[operand]
            self.emit_asm(f"mov {reg}, {lbl}", comment or f"Load address of string literal")
        elif operand.replace('.', '', 1).replace('-', '', 1).isdigit():
            # Constant number
            self.emit_asm(f"mov {reg}, {operand}", comment or f"Load immediate constant {operand}")
        else:
            # Variable or temporary
            self.emit_asm(f"mov {reg}, [{operand}]", comment or f"Load variable {operand}")

    def store_result(self, reg, result, comment=None):
        """Stores a register value into a target memory location."""
        self.emit_asm(f"mov [{result}], {reg}", comment or f"Store result into {result}")

    def generate(self):
        """Scans TAC and produces target assembly instructions."""
        # 1. Collect all jump labels first
        labels = set()
        for instr in self.tac_instructions:
            if instr.op == 'LABEL':
                labels.add(instr.arg1)
            elif instr.op in ['GOTO', 'IF_FALSE', 'IF_TRUE']:
                if instr.arg1 and instr.arg1.startswith('L') and instr.arg1[1:].isdigit():
                    labels.add(instr.arg1)
                if instr.result and instr.result.startswith('L') and instr.result[1:].isdigit():
                    labels.add(instr.result)

        # 2. Collect variables and string literals
        for instr in self.tac_instructions:
            for item in [instr.arg1, instr.arg2, instr.result]:
                if item and item not in labels:
                    self.register_variable(item)

        # Build data section for declared variables
        for var in sorted(self.declared_vars):
            self.add_data(f"    {var} dq 0")

        # 2. Second pass: generate target assembly instructions
        self.assembly_code.append("; --- TEXT SECTION ---")
        self.assembly_code.append("section .text")
        self.assembly_code.append("global main")
        self.assembly_code.append("extern printf")
        self.assembly_code.append("")
        self.emit_label("main")
        self.emit_asm("push rbp", "Setup stack frame")
        self.emit_asm("mov rbp, rsp")
        self.assembly_code.append("")

        for instr in self.tac_instructions:
            self.generate_instruction(instr)

        self.assembly_code.append("")
        self.emit_asm("mov rax, 0", "Return status 0")
        self.emit_asm("pop rbp", "Restore stack frame")
        self.emit_asm("ret")

        return self.get_full_code()

    def generate_instruction(self, instr):
        """Translates a single TAC instruction into target assembly."""
        op = instr.op

        if op == 'LABEL':
            self.emit_label(instr.arg1)

        elif op == 'GOTO':
            self.emit_asm(f"jmp {instr.arg1}", f"Unconditional jump to {instr.arg1}")

        elif op == '=':
            self.load_operand("rax", instr.arg1, f"Read RHS '{instr.arg1}'")
            self.store_result("rax", instr.result, f"Assign to '{instr.result}'")

        elif op in ['+', '-', '*', '/']:
            self.load_operand("rax", instr.arg1)
            self.load_operand("rbx", instr.arg2)

            if op == '+':
                self.emit_asm("add rax, rbx", f"Compute {instr.arg1} + {instr.arg2}")
            elif op == '-':
                self.emit_asm("sub rax, rbx", f"Compute {instr.arg1} - {instr.arg2}")
            elif op == '*':
                self.emit_asm("imul rax, rbx", f"Compute {instr.arg1} * {instr.arg2}")
            elif op == '/':
                self.emit_asm("cqo", "Sign extend RAX into RDX:RAX")
                self.emit_asm("idiv rbx", f"Compute {instr.arg1} / {instr.arg2}")

            self.store_result("rax", instr.result)

        elif op in ['<', '>', '<=', '>=', '==', '!=']:
            self.load_operand("rax", instr.arg1)
            self.load_operand("rbx", instr.arg2)
            self.emit_asm("cmp rax, rbx", f"Compare {instr.arg1} and {instr.arg2}")

            set_cc = {
                '<': 'setl', '>': 'setg', '<=': 'setle',
                '>=': 'setge', '==': 'sete', '!=': 'setne'
            }[op]

            self.emit_asm(f"{set_cc} al", f"Set AL byte if condition '{op}' is met")
            self.emit_asm("movzx rax, al", "Zero extend AL to RAX")
            self.store_result("rax", instr.result)

        elif op in ['&&', '||']:
            self.load_operand("rax", instr.arg1)
            self.load_operand("rbx", instr.arg2)

            if op == '&&':
                self.emit_asm("and rax, rbx", f"Logical AND between {instr.arg1} and {instr.arg2}")
            elif op == '||':
                self.emit_asm("or rax, rbx", f"Logical OR between {instr.arg1} and {instr.arg2}")

            self.store_result("rax", instr.result)

        elif op in ['UNARY_MINUS', '!']:
            self.load_operand("rax", instr.arg1)
            if op == 'UNARY_MINUS':
                self.emit_asm("neg rax", f"Negate {instr.arg1}")
            elif op == '!':
                self.emit_asm("cmp rax, 0", "Check if operand is zero")
                self.emit_asm("sete al", "Set AL if zero (logical NOT)")
                self.emit_asm("movzx rax, al", "Zero extend AL to RAX")

            self.store_result("rax", instr.result)

        elif op == 'IF_FALSE':
            self.load_operand("rax", instr.arg1)
            self.emit_asm("cmp rax, 0", f"Test condition '{instr.arg1}'")
            self.emit_asm(f"je {instr.result}", f"Jump to {instr.result} if false")

        elif op == 'IF_TRUE':
            self.load_operand("rax", instr.arg1)
            self.emit_asm("cmp rax, 0", f"Test condition '{instr.arg1}'")
            self.emit_asm(f"jne {instr.result}", f"Jump to {instr.result} if true")

        elif op == 'PRINT':
            if instr.arg1 in self.string_literals:
                str_lbl = self.string_literals[instr.arg1]
                self.emit_asm(f"lea rdi, [{str_lbl}]", "Load string address for printing")
            else:
                self.load_operand("rsi", instr.arg1, f"Pass value of {instr.arg1} to print")
                self.add_data("    fmt_int db \"%d\", 10, 0")
                self.emit_asm("lea rdi, [fmt_int]", "Load integer format string")
            
            self.emit_asm("mov rax, 0", "No vector registers used for printf")
            self.emit_asm("call printf", f"Print output for {instr.arg1}")

    def get_full_code(self):
        """Returns complete assembled code as a string."""
        lines = ["; --- DATA SECTION ---", "section .data"]
        lines.extend(self.data_section)
        lines.append("")
        lines.extend(self.assembly_code)
        return "\n".join(lines)

    def print_code(self):
        """Prints generated Target Assembly code."""
        print(self.get_full_code())
