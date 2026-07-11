"""
Semantic Analyzer for the Compiler
Performs type checking, scope analysis, and semantic validation
"""

from syntax_analyzer import (
    Program, Assignment, IfStatement, WhileStatement,
    ForStatement, PrintStatement, Block, BinaryOp, UnaryOp, Identifier,
    Number, String
)


class Symbol:
    """Represents a symbol in the symbol table"""
    def __init__(self, name, var_type, line):
        self.name = name
        self.var_type = var_type  # 'int', 'float', 'string', or 'unknown'
        self.line = line
        self.initialized = False

    def __repr__(self):
        return f"Symbol({self.name}, {self.var_type}, initialized={self.initialized})"


class Scope:
    """Represents a scope with symbol table"""
    def __init__(self, parent=None):
        self.parent = parent
        self.symbols = {}

    def define(self, name, var_type, line):
        """Define a symbol in this scope"""
        if name in self.symbols:
            return False  # Already defined
        self.symbols[name] = Symbol(name, var_type, line)
        return True

    def lookup(self, name):
        """Look up a symbol in this scope and parent scopes"""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def set_initialized(self, name):
        """Mark a symbol as initialized"""
        if name in self.symbols:
            self.symbols[name].initialized = True
            return True
        if self.parent:
            return self.parent.set_initialized(name)
        return False


class SemanticAnalyzer:
    """Performs semantic analysis on the AST"""
    
    def __init__(self, ast):
        self.ast = ast
        self.errors = []
        self.warnings = []
        self.global_scope = Scope()
        self.current_scope = self.global_scope
        self.type_map = {}  # Maps expressions to their inferred types

    def analyze(self):
        """Perform semantic analysis"""
        if self.ast is None:
            return False
        
        self.visit_program(self.ast)
        return len(self.errors) == 0

    def add_error(self, message, line=None):
        """Record a semantic error"""
        if line:
            self.errors.append(f"Semantic Error at line {line}: {message}")
        else:
            self.errors.append(f"Semantic Error: {message}")

    def add_warning(self, message, line=None):
        """Record a semantic warning"""
        if line:
            self.warnings.append(f"Warning at line {line}: {message}")
        else:
            self.warnings.append(f"Warning: {message}")

    def infer_type(self, expr):
        """Infer the type of an expression"""
        if isinstance(expr, Number):
            if '.' in expr.value:
                return 'float'
            return 'int'
        
        elif isinstance(expr, String):
            return 'string'
        
        elif isinstance(expr, Identifier):
            symbol = self.current_scope.lookup(expr.name)
            if symbol:
                return symbol.var_type
            return 'unknown'
        
        elif isinstance(expr, BinaryOp):
            left_type = self.infer_type(expr.left)
            right_type = self.infer_type(expr.right)
            
            # Logical operators return boolean-like (int)
            if expr.operator in ['&&', '||']:
                return 'int'
            
            # Relational operators return boolean-like (int)
            if expr.operator in ['<', '>', '<=', '>=', '==', '!=']:
                return 'int'
            
            # Arithmetic operators
            if expr.operator in ['+', '-', '*', '/']:
                if left_type == 'float' or right_type == 'float':
                    return 'float'
                elif left_type == 'int' and right_type == 'int':
                    return 'int'
                else:
                    return 'unknown'
            
            return 'unknown'
        
        elif isinstance(expr, UnaryOp):
            if expr.operator == '!':
                return 'int'  # Logical NOT returns int
            elif expr.operator == '-':
                return self.infer_type(expr.operand)
            return 'unknown'
        
        return 'unknown'

    def visit_program(self, node):
        """Visit Program node"""
        for stmt in node.statements:
            self.visit_statement(stmt)

    def visit_statement(self, stmt):
        """Visit Statement node"""
        if isinstance(stmt, Assignment):
            self.visit_assignment(stmt)
        elif isinstance(stmt, IfStatement):
            self.visit_if_statement(stmt)
        elif isinstance(stmt, WhileStatement):
            self.visit_while_statement(stmt)
        elif isinstance(stmt, ForStatement):
            self.visit_for_statement(stmt)
        elif isinstance(stmt, PrintStatement):
            self.visit_print_statement(stmt)
        elif isinstance(stmt, Block):
            self.visit_block(stmt)

    def visit_assignment(self, node):
        """Visit Assignment node"""
        # Validate the expression (check for undefined variables, etc.)
        self.visit_expression(node.expression)
        
        # Check if variable exists
        symbol = self.current_scope.lookup(node.identifier)
        
        # Infer type of right-hand side
        rhs_type = self.infer_type(node.expression)
        
        if symbol is None:
            # Auto-declare variable with inferred type
            if rhs_type == 'unknown':
                inferred_type = 'int'  # Default to int
                self.add_warning(f"Cannot infer type for '{node.identifier}', defaulting to 'int'")
            else:
                inferred_type = rhs_type
            
            self.current_scope.define(node.identifier, inferred_type, 0)
            symbol = self.current_scope.lookup(node.identifier)
        
        # Mark as initialized
        self.current_scope.set_initialized(node.identifier)
        
        # Type checking
        if rhs_type != 'unknown' and symbol.var_type != 'unknown':
            if rhs_type != symbol.var_type:
                self.add_warning(
                    f"Type mismatch in assignment to '{node.identifier}': "
                    f"expected {symbol.var_type}, got {rhs_type}"
                )
        
        self.type_map[id(node.expression)] = rhs_type

    def visit_if_statement(self, node):
        """Visit IfStatement node"""
        # Validate condition expression
        self.visit_expression(node.condition)
        
        # Check condition type
        cond_type = self.infer_type(node.condition)
        self.type_map[id(node.condition)] = cond_type
        
        # Visit then block
        self.visit_statement(node.then_block)
        
        # Visit else block if present
        if node.else_block:
            self.visit_statement(node.else_block)

    def visit_while_statement(self, node):
        """Visit WhileStatement node"""
        # Validate condition expression
        self.visit_expression(node.condition)
        
        # Check condition type
        cond_type = self.infer_type(node.condition)
        self.type_map[id(node.condition)] = cond_type
        
        # Visit body
        self.visit_statement(node.body)

    def visit_for_statement(self, node):
        """Visit ForStatement node"""
        # Create new scope for loop
        new_scope = Scope(self.current_scope)
        old_scope = self.current_scope
        self.current_scope = new_scope
        
        # Process init
        if node.init:
            self.visit_expression(node.init)
        
        # Check condition type
        if node.condition:
            cond_type = self.infer_type(node.condition)
            self.type_map[id(node.condition)] = cond_type
        
        # Process update
        if node.update:
            self.visit_expression(node.update)
        
        # Visit body
        self.visit_statement(node.body)
        
        # Restore scope
        self.current_scope = old_scope

    def visit_print_statement(self, node):
        """Visit PrintStatement node"""
        # Validate the expression
        self.visit_expression(node.expression)
        
        expr_type = self.infer_type(node.expression)
        self.type_map[id(node.expression)] = expr_type

    def visit_block(self, node):
        """Visit Block node"""
        # Create new scope for block
        new_scope = Scope(self.current_scope)
        old_scope = self.current_scope
        self.current_scope = new_scope
        
        # Visit all statements in block
        for stmt in node.statements:
            self.visit_statement(stmt)
        
        # Restore scope
        self.current_scope = old_scope

    def visit_expression(self, expr):
        """Visit Expression node"""
        if isinstance(expr, BinaryOp):
            self.visit_expression(expr.left)
            self.visit_expression(expr.right)
        elif isinstance(expr, UnaryOp):
            self.visit_expression(expr.operand)
        elif isinstance(expr, Identifier):
            symbol = self.current_scope.lookup(expr.name)
            if symbol is None:
                self.add_error(f"Undefined variable '{expr.name}'")
            elif not symbol.initialized:
                self.add_warning(f"Variable '{expr.name}' may not be initialized")

    def print_symbol_table(self):
        """Print the global symbol table"""
        print("\n--- SYMBOL TABLE ---")
        if self.global_scope.symbols:
            print(f"{'Name':<20}{'Type':<15}{'Initialized'}")
            print("-" * 50)
            for name, symbol in self.global_scope.symbols.items():
                print(f"{name:<20}{symbol.var_type:<15}{symbol.initialized}")
        else:
            print("(empty)")

    def print_type_info(self, node, indent=0):
        """Print type information for expressions"""
        prefix = "  " * indent
        
        if isinstance(node, Program):
            for stmt in node.statements:
                self.print_type_info(stmt, indent)
        
        elif isinstance(node, Assignment):
            expr_type = self.type_map.get(id(node.expression), 'unknown')
            print(f"{prefix}Assignment '{node.identifier}': {expr_type}")
            self.print_type_info(node.expression, indent + 1)
        
        elif isinstance(node, IfStatement):
            print(f"{prefix}If")
            cond_type = self.type_map.get(id(node.condition), 'unknown')
            print(f"{prefix}  Condition: {cond_type}")
            self.print_type_info(node.condition, indent + 2)
            print(f"{prefix}  Then:")
            self.print_type_info(node.then_block, indent + 2)
            if node.else_block:
                print(f"{prefix}  Else:")
                self.print_type_info(node.else_block, indent + 2)
        
        elif isinstance(node, WhileStatement):
            print(f"{prefix}While")
            cond_type = self.type_map.get(id(node.condition), 'unknown')
            print(f"{prefix}  Condition: {cond_type}")
            self.print_type_info(node.body, indent + 1)
        
        elif isinstance(node, ForStatement):
            print(f"{prefix}For")
            if node.init:
                self.print_type_info(node.init, indent + 1)
            if node.condition:
                cond_type = self.type_map.get(id(node.condition), 'unknown')
                print(f"{prefix}  Condition: {cond_type}")
            if node.update:
                self.print_type_info(node.update, indent + 1)
            self.print_type_info(node.body, indent + 1)
        
        elif isinstance(node, PrintStatement):
            expr_type = self.type_map.get(id(node.expression), 'unknown')
            print(f"{prefix}Print: {expr_type}")
            self.print_type_info(node.expression, indent + 1)
        
        elif isinstance(node, Block):
            print(f"{prefix}Block")
            for stmt in node.statements:
                self.print_type_info(stmt, indent + 1)
        
        elif isinstance(node, BinaryOp):
            result_type = self.type_map.get(id(node), 'unknown')
            print(f"{prefix}BinaryOp '{node.operator}': {result_type}")
            self.print_type_info(node.left, indent + 1)
            self.print_type_info(node.right, indent + 1)
        
        elif isinstance(node, UnaryOp):
            result_type = self.type_map.get(id(node), 'unknown')
            print(f"{prefix}UnaryOp '{node.operator}': {result_type}")
            self.print_type_info(node.operand, indent + 1)
        
        elif isinstance(node, Identifier):
            symbol = self.current_scope.lookup(node.name)
            symbol_type = symbol.var_type if symbol else 'undefined'
            print(f"{prefix}Identifier '{node.name}': {symbol_type}")
        
        elif isinstance(node, Number):
            num_type = 'float' if '.' in node.value else 'int'
            print(f"{prefix}Number {node.value}: {num_type}")
        
        elif isinstance(node, String):
            print(f"{prefix}String: string")
