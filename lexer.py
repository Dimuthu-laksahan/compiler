import re

class LexicalAnalyzer:
    def __init__(self):
        # Define token patterns (Order matters: keywords/multi-char ops first)
        self.token_specification = [
            ('COMMENT_MULTI', r'/\*[\s\S]*?\*/'),    # Multi-line comment
            ('COMMENT_SINGLE', r'//.*'),                 # Single-line comment
            ('STRING',        r'"[^"\n]*"'),         # String literals (closed)
            # invalid identifier like 2name
            ('INVALID_ID',    r'\d+[A-Za-z_][A-Za-z0-9_]*'),
            # malformed numbers with multiple dots like 12.3.4
            ('MALFORMED_NUMBER', r'\d+(?:\.\d+){2,}'),
            ('NUMBER',        r'\d+(?:\.\d+)?'),     # Integer or decimal
            ('KEYWORD',       r'\b(if|else|while|for|int|float|print|begin|end)\b'),
            ('ID',            r'[a-zA-Z_][a-zA-Z0-9_]*'), # Identifiers
            ('OP_REL',        r'==|!=|<=|>=|<|>'),     # Relational operators
            ('OP_LOG',        r'&&|\|\||!'),         # Logical operators
            ('OP_ASSIGN',     r'='),                   # Assignment
            ('OP_ARITH',      r'[+\-*/]'),            # Arithmetic operators
            ('DELIMITER',     r'[;,(){}]'),            # Delimiters
            ('NEWLINE',       r'\n'),                 # Line endings
            ('SKIP',          r'[ \t]+'),             # Skip spaces and tabs
            ('MISMATCH',      r'.'),                   # Any other character (Error)
        ]
        
        # Compile the master regex
        self.regex = re.compile('|'.join('(?P<%s>%s)' % pair for pair in self.token_specification))

    def _find_unterminated_string(self, code):
        # Return line number of an unterminated string if any (simple approach)
        quote_positions = [i for i, ch in enumerate(code) if ch == '"']
        if len(quote_positions) % 2 == 1:
            start_idx = quote_positions[-1]
            line = code.count('\n', 0, start_idx) + 1
            return line
        return None

    def tokenize(self, code):
        line_num = 1
        line_start = 0
        tokens = []

        errors = []

        # Pre-scan for unterminated string literal
        unterminated_line = self._find_unterminated_string(code)
        if unterminated_line is not None:
            errors.append(f"Lexical Error: Unterminated string literal at line {unterminated_line}")

        for mo in self.regex.finditer(code):
            kind = mo.lastgroup
            value = mo.group()
            column = mo.start() - line_start

            if kind == 'NEWLINE':
                line_start = mo.end()
                line_num += 1
                continue
            elif kind == 'SKIP' or kind == 'COMMENT_SINGLE' or kind == 'COMMENT_MULTI':
                if kind == 'COMMENT_MULTI':
                    line_num += value.count('\n') # Adjust line count for multi-line comments
                continue
            elif kind == 'MISMATCH':
                errors.append(f"Lexical Error: Invalid symbol '{value}' at line {line_num}")
                continue
            
            # Handle specific lexical errors detected by token categories
            if kind == 'INVALID_ID':
                errors.append(f"Lexical Error: Invalid identifier '{value}' at line {line_num}")
                continue

            if kind == 'MALFORMED_NUMBER':
                errors.append(f"Lexical Error: Malformed number '{value}' at line {line_num}")
                continue

            tokens.append((line_num, kind, value))
        
        return tokens, errors