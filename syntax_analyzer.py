class Token:
    
    def __init__(self, line, category, value):
        self.line = line
        self.category = category
        self.value = value

    def __repr__(self):
        return f"Token({self.line}, {self.category}, '{self.value}')"


class ASTNode:
    
    pass


class Program(ASTNode):
    
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Program({len(self.statements)} statements)"


class Statement(ASTNode):
    pass


class Assignment(Statement):
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression

    def __repr__(self):
        return f"Assignment({self.identifier}, {self.expression})"


class IfStatement(Statement):
    def __init__(self, condition, then_block, else_block=None):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

    def __repr__(self):
        return f"IfStatement({self.condition})"


class WhileStatement(Statement):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"WhileStatement({self.condition})"


class ForStatement(Statement):
    def __init__(self, init, condition, update, body):
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

    def __repr__(self):
        return f"ForStatement()"


class PrintStatement(Statement):
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f"PrintStatement({self.expression})"


class Block(Statement):
    """Block of statements: { statements }"""
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Block({len(self.statements)} statements)"


class Expression(ASTNode):
    """Base class for expressions"""
    pass


class BinaryOp(Expression):
    """Binary operation: left op right"""
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"BinaryOp({self.left} {self.operator} {self.right})"


class UnaryOp(Expression):
    """Unary operation: op operand"""
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

    def __repr__(self):
        return f"UnaryOp({self.operator} {self.operand})"


class Identifier(Expression):
    """Variable identifier"""
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Identifier({self.name})"


class Number(Expression):
    """Numeric literal"""
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Number({self.value})"


class String(Expression):
    """String literal"""
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"String({self.value})"


class SyntaxAnalyzer:
    """Parser that converts tokens into an AST"""
    
    def __init__(self, tokens):
        self.tokens = [Token(line, cat, val) for line, cat, val in tokens]
        self.pos = 0
        self.errors = []

    def current_token(self):
        """Get the current token without consuming it"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def peek_token(self, offset=1):
        """Peek ahead at a future token"""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def consume(self, expected_category=None):
        """Consume and return the current token"""
        token = self.current_token()
        if token is None:
            self.errors.append("Unexpected end of input")
            return None
        
        if expected_category and token.category != expected_category:
            self.errors.append(
                f"Syntax Error at line {token.line}: Expected {expected_category}, "
                f"got {token.category} ('{token.value}')"
            )
        
        self.pos += 1
        return token

    def parse(self):
        """Parse the token stream into an AST"""
        statements = []
        
        while self.current_token() is not None:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            else:
                # If parse_statement returned None and didn't consume token, skip it
                token = self.current_token()
                if token:
                    self.consume()
        
        if self.errors:
            return None, self.errors
        
        return Program(statements), self.errors

    def parse_statement(self):
        """Parse a single statement"""
        token = self.current_token()
        
        if token is None:
            return None
        
        if token.category == 'KEYWORD':
            if token.value == 'if':
                return self.parse_if_statement()
            elif token.value == 'while':
                return self.parse_while_statement()
            elif token.value == 'for':
                return self.parse_for_statement()
            elif token.value == 'print':
                return self.parse_print_statement()
            elif token.value == 'begin':
                return self.parse_block()
        
        elif token.category == 'ID':
            return self.parse_assignment()
        
        elif token.value == '}':
            # End of block
            return None
        
        else:
            self.errors.append(
                f"Syntax Error at line {token.line}: Unexpected token {token.category} ('{token.value}')"
            )
            self.consume()  # Skip the problematic token
            return None

    def parse_assignment(self):
        """Parse assignment: ID = expr ;"""
        id_token = self.consume('ID')
        if id_token is None:
            return None
        
        assign_token = self.current_token()
        if assign_token is None or assign_token.value != '=':
            self.errors.append(
                f"Syntax Error at line {id_token.line}: Expected '=' after identifier '{id_token.value}'"
            )
            return None
        
        self.consume('OP_ASSIGN')
        
        expr = self.parse_expression()
        if expr is None:
            return None
        
        semi_token = self.current_token()
        if semi_token is None or semi_token.value != ';':
            self.errors.append(
                f"Syntax Error at line {id_token.line}: Expected ';' at end of assignment"
            )
        else:
            self.consume('DELIMITER')
        
        return Assignment(id_token.value, expr)

    def parse_if_statement(self):
        """Parse if statement: if ( expr ) statement [else statement]"""
        self.consume('KEYWORD')  # consume 'if'
        
        if self.current_token() is None or self.current_token().value != '(':
            self.errors.append("Syntax Error: Expected '(' after 'if'")
            return None
        
        self.consume('DELIMITER')
        
        condition = self.parse_expression()
        if condition is None:
            return None
        
        if self.current_token() is None or self.current_token().value != ')':
            self.errors.append("Syntax Error: Expected ')' after if condition")
            return None
        
        self.consume('DELIMITER')
        
        then_block = self.parse_statement()
        if then_block is None:
            return None
        
        else_block = None
        if self.current_token() and self.current_token().category == 'KEYWORD' and self.current_token().value == 'else':
            self.consume('KEYWORD')
            else_block = self.parse_statement()
        
        return IfStatement(condition, then_block, else_block)

    def parse_while_statement(self):
        """Parse while statement: while ( expr ) statement"""
        self.consume('KEYWORD')  # consume 'while'
        
        if self.current_token() is None or self.current_token().value != '(':
            self.errors.append("Syntax Error: Expected '(' after 'while'")
            return None
        
        self.consume('DELIMITER')
        
        condition = self.parse_expression()
        if condition is None:
            return None
        
        if self.current_token() is None or self.current_token().value != ')':
            self.errors.append("Syntax Error: Expected ')' after while condition")
            return None
        
        self.consume('DELIMITER')
        
        body = self.parse_statement()
        if body is None:
            return None
        
        return WhileStatement(condition, body)

    def parse_for_statement(self):
        """Parse for statement: for ( expr ; expr ; expr ) statement"""
        self.consume('KEYWORD')  # consume 'for'
        
        if self.current_token() is None or self.current_token().value != '(':
            self.errors.append("Syntax Error: Expected '(' after 'for'")
            return None
        
        self.consume('DELIMITER')
        
        init = self.parse_expression()
        
        if self.current_token() is None or self.current_token().value != ';':
            self.errors.append("Syntax Error: Expected ';' after for init")
            return None
        
        self.consume('DELIMITER')
        
        condition = self.parse_expression()
        
        if self.current_token() is None or self.current_token().value != ';':
            self.errors.append("Syntax Error: Expected ';' after for condition")
            return None
        
        self.consume('DELIMITER')
        
        update = self.parse_expression()
        
        if self.current_token() is None or self.current_token().value != ')':
            self.errors.append("Syntax Error: Expected ')' after for clauses")
            return None
        
        self.consume('DELIMITER')
        
        body = self.parse_statement()
        if body is None:
            return None
        
        return ForStatement(init, condition, update, body)

    def parse_print_statement(self):
        """Parse print statement: print expr ;"""
        self.consume('KEYWORD')  # consume 'print'
        
        expr = self.parse_expression()
        if expr is None:
            return None
        
        if self.current_token() is None or self.current_token().value != ';':
            self.errors.append("Syntax Error: Expected ';' after print statement")
        else:
            self.consume('DELIMITER')
        
        return PrintStatement(expr)

    def parse_block(self):
        """Parse block: begin { statements } end"""
        self.consume('KEYWORD')  # consume 'begin'
        
        if self.current_token() is None or self.current_token().value != '{':
            self.errors.append("Syntax Error: Expected '{' after 'begin'")
            return None
        
        self.consume('DELIMITER')
        
        statements = []
        while self.current_token() and self.current_token().value != '}':
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        if self.current_token() is None or self.current_token().value != '}':
            self.errors.append("Syntax Error: Expected '}' to close block")
            return None
        
        self.consume('DELIMITER')
        
        if self.current_token() is None or self.current_token().category != 'KEYWORD' or self.current_token().value != 'end':
            self.errors.append("Syntax Error: Expected 'end' after closing '}'")
        else:
            self.consume('KEYWORD')
        
        return Block(statements)

    def parse_expression(self):
        """Parse expression: or_expr"""
        return self.parse_or_expr()

    def parse_or_expr(self):
        """Parse logical OR: and_expr [|| and_expr]*"""
        left = self.parse_and_expr()
        if left is None:
            return None
        
        while self.current_token() and self.current_token().value == '||':
            op_token = self.consume('OP_LOG')
            right = self.parse_and_expr()
            if right is None:
                return None
            left = BinaryOp(left, op_token.value, right)
        
        return left

    def parse_and_expr(self):
        """Parse logical AND: rel_expr [&& rel_expr]*"""
        left = self.parse_rel_expr()
        if left is None:
            return None
        
        while self.current_token() and self.current_token().value == '&&':
            op_token = self.consume('OP_LOG')
            right = self.parse_rel_expr()
            if right is None:
                return None
            left = BinaryOp(left, op_token.value, right)
        
        return left

    def parse_rel_expr(self):
        """Parse relational: arith_expr [(<|>|<=|>=|==|!=) arith_expr]*"""
        left = self.parse_arith_expr()
        if left is None:
            return None
        
        while self.current_token() and self.current_token().category == 'OP_REL':
            op_token = self.consume('OP_REL')
            right = self.parse_arith_expr()
            if right is None:
                return None
            left = BinaryOp(left, op_token.value, right)
        
        return left

    def parse_arith_expr(self):
        """Parse arithmetic: term [(+|-) term]*"""
        left = self.parse_term()
        if left is None:
            return None
        
        while self.current_token() and self.current_token().value in ['+', '-']:
            op_token = self.consume('OP_ARITH')
            right = self.parse_term()
            if right is None:
                return None
            left = BinaryOp(left, op_token.value, right)
        
        return left

    def parse_term(self):
        """Parse term: factor [(* |/) factor]*"""
        left = self.parse_unary()
        if left is None:
            return None
        
        while self.current_token() and self.current_token().value in ['*', '/']:
            op_token = self.consume('OP_ARITH')
            right = self.parse_unary()
            if right is None:
                return None
            left = BinaryOp(left, op_token.value, right)
        
        return left

    def parse_unary(self):
        """Parse unary: [! | -] factor"""
        token = self.current_token()
        
        if token and token.value in ['!', '-']:
            op_token = self.consume()
            operand = self.parse_unary()
            if operand is None:
                return None
            return UnaryOp(op_token.value, operand)
        
        return self.parse_primary()

    def parse_primary(self):
        """Parse primary: ID | NUMBER | STRING | ( expr )"""
        token = self.current_token()
        
        if token is None:
            self.errors.append("Syntax Error: Unexpected end of input in expression")
            return None
        
        if token.category == 'ID':
            id_token = self.consume('ID')
            return Identifier(id_token.value)
        
        elif token.category == 'NUMBER':
            num_token = self.consume('NUMBER')
            return Number(num_token.value)
        
        elif token.category == 'STRING':
            str_token = self.consume('STRING')
            return String(str_token.value)
        
        elif token.value == '(':
            self.consume('DELIMITER')
            expr = self.parse_expression()
            if expr is None:
                return None
            if self.current_token() is None or self.current_token().value != ')':
                self.errors.append("Syntax Error: Expected ')' after expression")
                return None
            self.consume('DELIMITER')
            return expr
        
        else:
            self.errors.append(
                f"Syntax Error at line {token.line}: Unexpected token {token.category} ('{token.value}') in expression"
            )
            self.consume()
            return None

    def print_ast(self, node, indent=0):
        """Pretty-print the AST"""
        prefix = "  " * indent
        
        if isinstance(node, Program):
            print(f"{prefix}Program")
            for stmt in node.statements:
                self.print_ast(stmt, indent + 1)
        
        elif isinstance(node, Assignment):
            print(f"{prefix}Assignment: {node.identifier}")
            self.print_ast(node.expression, indent + 1)
        
        elif isinstance(node, IfStatement):
            print(f"{prefix}IfStatement")
            print(f"{prefix}  Condition:")
            self.print_ast(node.condition, indent + 2)
            print(f"{prefix}  Then:")
            self.print_ast(node.then_block, indent + 2)
            if node.else_block:
                print(f"{prefix}  Else:")
                self.print_ast(node.else_block, indent + 2)
        
        elif isinstance(node, WhileStatement):
            print(f"{prefix}WhileStatement")
            print(f"{prefix}  Condition:")
            self.print_ast(node.condition, indent + 2)
            print(f"{prefix}  Body:")
            self.print_ast(node.body, indent + 2)
        
        elif isinstance(node, ForStatement):
            print(f"{prefix}ForStatement")
            print(f"{prefix}  Init:")
            if node.init:
                self.print_ast(node.init, indent + 2)
            print(f"{prefix}  Condition:")
            if node.condition:
                self.print_ast(node.condition, indent + 2)
            print(f"{prefix}  Update:")
            if node.update:
                self.print_ast(node.update, indent + 2)
            print(f"{prefix}  Body:")
            self.print_ast(node.body, indent + 2)
        
        elif isinstance(node, PrintStatement):
            print(f"{prefix}PrintStatement")
            self.print_ast(node.expression, indent + 1)
        
        elif isinstance(node, Block):
            print(f"{prefix}Block")
            for stmt in node.statements:
                self.print_ast(stmt, indent + 1)
        
        elif isinstance(node, BinaryOp):
            print(f"{prefix}BinaryOp: {node.operator}")
            print(f"{prefix}  Left:")
            self.print_ast(node.left, indent + 2)
            print(f"{prefix}  Right:")
            self.print_ast(node.right, indent + 2)
        
        elif isinstance(node, UnaryOp):
            print(f"{prefix}UnaryOp: {node.operator}")
            self.print_ast(node.operand, indent + 1)
        
        elif isinstance(node, Identifier):
            print(f"{prefix}Identifier: {node.name}")
        
        elif isinstance(node, Number):
            print(f"{prefix}Number: {node.value}")
        
        elif isinstance(node, String):
            print(f"{prefix}String: {node.value}")
