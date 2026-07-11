"""
Intermediate Code Generator for the Compiler
Converts Abstract Syntax Tree (AST) into Three-Address Code (TAC) / Intermediate Representation (IR).
"""

from syntax_analyzer import (
    Program, Assignment, IfStatement, WhileStatement,
    ForStatement, PrintStatement, Block, BinaryOp, UnaryOp, Identifier,
    Number, String, Statement, Expression
)


class TACInstruction:
    """Represents a single Three-Address Code instruction"""
    def __init__(self, op, arg1=None, arg2=None, result=None):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result

    def __repr__(self):
        if self.op == 'LABEL':
            return f"{self.arg1}:"
        elif self.op == 'GOTO':
            return f"goto {self.arg1}"
        elif self.op == 'IF_FALSE':
            return f"ifFalse {self.arg1} goto {self.result}"
        elif self.op == 'IF_TRUE':
            return f"if {self.arg1} goto {self.result}"
        elif self.op == 'PRINT':
            return f"print {self.arg1}"
        elif self.op == '=':
            return f"{self.result} = {self.arg1}"
        elif self.op in ['+', '-', '*', '/', '<', '>', '<=', '>=', '==', '!=', '&&', '||']:
            return f"{self.result} = {self.arg1} {self.op} {self.arg2}"
        elif self.op == 'UNARY_MINUS':
            return f"{self.result} = -{self.arg1}"
        elif self.op == '!':
            return f"{self.result} = !{self.arg1}"
        else:
            return f"{self.op} {self.arg1} {self.arg2} {self.result}".strip()


class IntermediateCodeGenerator:
    """Generates Three-Address Code (TAC) from an AST"""

    def __init__(self, ast):
        self.ast = ast
        self.instructions = []
        self.temp_counter = 0
        self.label_counter = 0

    def new_temp(self):
        """Generate a new temporary variable name (t1, t2, ...)"""
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self):
        """Generate a new label name (L1, L2, ...)"""
        self.label_counter += 1
        return f"L{self.label_counter}"

    def emit(self, op, arg1=None, arg2=None, result=None):
        """Emit a new TAC instruction"""
        instruction = TACInstruction(op, arg1, arg2, result)
        self.instructions.append(instruction)
        return instruction

    def generate(self):
        """Generate TAC for the entire AST"""
        if self.ast is None:
            return []
        self.generate_program(self.ast)
        return self.instructions

    def generate_program(self, node):
        """Generate TAC for Program node"""
        if isinstance(node, Program):
            for stmt in node.statements:
                self.generate_statement(stmt)

    def generate_statement(self, stmt):
        """Generate TAC for Statement nodes"""
        if isinstance(stmt, Assignment):
            self.generate_assignment(stmt)
        elif isinstance(stmt, IfStatement):
            self.generate_if_statement(stmt)
        elif isinstance(stmt, WhileStatement):
            self.generate_while_statement(stmt)
        elif isinstance(stmt, ForStatement):
            self.generate_for_statement(stmt)
        elif isinstance(stmt, PrintStatement):
            self.generate_print_statement(stmt)
        elif isinstance(stmt, Block):
            self.generate_block(stmt)

    def generate_assignment(self, node):
        """Generate TAC for Assignment node: target = expr"""
        rhs_temp = self.generate_expression(node.expression)
        self.emit('=', rhs_temp, None, node.identifier)

    def generate_if_statement(self, node):
        """Generate TAC for IfStatement node"""
        cond_temp = self.generate_expression(node.condition)
        
        if node.else_block:
            else_label = self.new_label()
            end_label = self.new_label()
            
            self.emit('IF_FALSE', cond_temp, None, else_label)
            self.generate_statement(node.then_block)
            self.emit('GOTO', end_label)
            self.emit('LABEL', else_label)
            self.generate_statement(node.else_block)
            self.emit('LABEL', end_label)
        else:
            end_label = self.new_label()
            self.emit('IF_FALSE', cond_temp, None, end_label)
            self.generate_statement(node.then_block)
            self.emit('LABEL', end_label)

    def generate_while_statement(self, node):
        """Generate TAC for WhileStatement node"""
        start_label = self.new_label()
        end_label = self.new_label()

        self.emit('LABEL', start_label)
        cond_temp = self.generate_expression(node.condition)
        self.emit('IF_FALSE', cond_temp, None, end_label)
        self.generate_statement(node.body)
        self.emit('GOTO', start_label)
        self.emit('LABEL', end_label)

    def generate_for_statement(self, node):
        """Generate TAC for ForStatement node"""
        start_label = self.new_label()
        end_label = self.new_label()

        # Initialization
        if node.init:
            if isinstance(node.init, Statement):
                self.generate_statement(node.init)
            else:
                self.generate_expression(node.init)

        self.emit('LABEL', start_label)
        
        # Condition
        if node.condition:
            cond_temp = self.generate_expression(node.condition)
            self.emit('IF_FALSE', cond_temp, None, end_label)

        # Loop Body
        self.generate_statement(node.body)

        # Update expression/statement
        if node.update:
            if isinstance(node.update, Statement):
                self.generate_statement(node.update)
            else:
                self.generate_expression(node.update)

        self.emit('GOTO', start_label)
        self.emit('LABEL', end_label)

    def generate_print_statement(self, node):
        """Generate TAC for PrintStatement node"""
        expr_temp = self.generate_expression(node.expression)
        self.emit('PRINT', expr_temp)

    def generate_block(self, node):
        """Generate TAC for Block node"""
        for stmt in node.statements:
            self.generate_statement(stmt)

    def generate_expression(self, node):
        """Generate TAC for Expression nodes and return the location (temp/var/const) of the result"""
        if isinstance(node, Number):
            return str(node.value)
        
        elif isinstance(node, String):
            return node.value
        
        elif isinstance(node, Identifier):
            return node.name
        
        elif isinstance(node, BinaryOp):
            left_temp = self.generate_expression(node.left)
            right_temp = self.generate_expression(node.right)
            res_temp = self.new_temp()
            self.emit(node.operator, left_temp, right_temp, res_temp)
            return res_temp
        
        elif isinstance(node, UnaryOp):
            operand_temp = self.generate_expression(node.operand)
            res_temp = self.new_temp()
            op_name = 'UNARY_MINUS' if node.operator == '-' else node.operator
            self.emit(op_name, operand_temp, None, res_temp)
            return res_temp
        
        return None

    def print_code(self):
        """Print generated TAC instructions with formatting"""
        print(f"{'Line':<6} | {'Intermediate Code (TAC)':<30}")
        print("-" * 40)
        line_num = 1
        for instr in self.instructions:
            if instr.op == 'LABEL':
                print(f"{'':<6} | {str(instr)}")
            else:
                print(f"{line_num:<6} |   {str(instr)}")
                line_num += 1
