import re

from rscript.lang.ast import Token, TokenType

_keywords = {"unknown": TokenType.TYPE,
             "int": TokenType.TYPE,
             "dword": TokenType.TYPE,
             "float": TokenType.TYPE,
             "str": TokenType.TYPE,
             "ref": TokenType.TYPE,
             "array": TokenType.TYPE,
             "if": TokenType.IF,
             "else": TokenType.ELSE,
             "while": TokenType.WHILE,
             "for": TokenType.FOR,
             "break": TokenType.BREAK,
             "continue": TokenType.CONTINUE,
             "exit": TokenType.EXIT,
             "function": TokenType.FUNCTION,
             "class": TokenType.CLASS,
             "try": TokenType.TRY,
             "catch": TokenType.CATCH,
             "finally": TokenType.FINALLY,
             "throw": TokenType.THROW}

_integer = r"(?P<int>\d+(?=\W))"
_float = r"(?P<float>\d+\.\d+(?:[Ee][+-]?\d+)?(?=\W))"
_bin_dword = r"(?P<bin>[01]+[Bb](?=\W))"
_hex_dword = r"(?P<hex>[0-9A-Fa-f]+[Hh](?=\W))"
_number = re.compile(r'|'.join([_hex_dword, _bin_dword, _float, _integer]))
del _integer, _float, _bin_dword, _hex_dword


def _is_alpha(c):
    return 'a' <= c <= 'z' or \
           'A' <= c <= 'Z' or \
            c == '_'


def _is_digit(c):
    return '0' <= c <= '9'


def _is_alphanum(c):
    return _is_alpha(c) or _is_digit(c)


class Lexer:

    def __init__(self, source):
        self._source = source.replace('\x09', 4*'\x20')
        self._tokens = list()

        self._start = 0
        self._current = 0
        self._line_start = 0
        self._line_no = 1

        self._indent_lexeme = ""

    def tokenize(self):
        while not self._at_and():
            self._start = self._current
            self._scan_token()
        self._tokens.append(Token(TokenType.END, "", None, self._line_no,
                                  self._start-self._line_start))
        return self._tokens

    def _scan_token(self):
        c = self._advance()

        if self._current == (self._line_start + 1) and (c == '\x20'):
            self._indent(c)
            return

        if c == '(': self._add_token(TokenType.LPAREN)
        elif c == ')': self._add_token(TokenType.RPAREN)
        elif c == '{': self._add_token(TokenType.LBRACE)
        elif c == '}': self._add_token(TokenType.RBRACE)
        elif c == '[': self._add_token(TokenType.LSQUARE)
        elif c == ']': self._add_token(TokenType.RSQUARE)
        elif c == ',': self._add_token(TokenType.COMMA)
        elif c == '.': self._add_token(TokenType.DOT)
        elif c == '+': self._add_token(TokenType.PLUS)
        elif c == '*': self._add_token(TokenType.MUL)
        elif c == '%': self._add_token(TokenType.MOD)
        elif c == ':': self._add_token(TokenType.COLON)
        elif c == ';': self._add_token(TokenType.SEMICOLON)
        elif c == '^': self._add_token(TokenType.BIT_XOR)
        elif c == '~': self._add_token(TokenType.BIT_NOT)
        elif c == '-':
            if self._match('>'): self._add_token(TokenType.POINTER)
            else: self._add_token(TokenType.MINUS)
        elif c == '=':
            if self._match('='): self._add_token(TokenType.EQUAL)
            else: self._add_token(TokenType.ASSIGN)
        elif c == '!':
            if self._match('='): self._add_token(TokenType.NOT_EQUAL)
            else: self._add_token(TokenType.NOT)
        elif c == '<':
            if self._match('='): self._add_token(TokenType.LESS_EQUAL)
            elif self._match('<'): self._add_token(TokenType.SHL)
            else: self._add_token(TokenType.LESS)
        elif c == '>':
            if self._match('='): self._add_token(TokenType.MORE_EQUAL)
            elif self._match('>'): self._add_token(TokenType.SHR)
            else: self._add_token(TokenType.MORE)
        elif c == '&':
            if self._match('&'): self._add_token(TokenType.AND)
            else: self._add_token(TokenType.BIT_AND)
        elif c == '|':
            if self._match('|'): self._add_token(TokenType.OR)
            else: self._add_token(TokenType.BIT_OR)
        elif c == '/':
            if self._match('/'):
                self._comment()
            elif self._match('*'):
                self._block_comment()
            else: self._add_token(TokenType.DIV)
        # elif c == '#': self._directive()
        elif c in '\"\'': self._string()
        elif _is_alphanum(c): self._number()
        elif c == '\x09': self._add_token(TokenType.TAB)
        elif c == '\x20': self._add_token(TokenType.SPACE)
        elif c == '\x0d':
            if self._match('\x0a'):
                self._add_token(TokenType.NEWLINE)
                self._line_no += 1
                self._line_start = self._current
        else:
            pass

    def _advance(self):
        self._current += 1
        return self._source[self._current-1]

    def _match(self, expected):
        if self._at_and():
            return False
        if self._source[self._current] != expected:
            return False
        self._current += 1
        return True

    def _peek(self):
        if self._at_and():
            return '\x00'
        return self._source[self._current]

    def _peek_next(self):
        if self._current + 1 > len(self._source):
            return '\x00'
        return self._source[self._current+1]

    def _add_token(self, type, literal=None):
        text = self._source[self._start:self._current]
        self._tokens.append(Token(type, text, literal, self._line_no,
                            self._start-self._line_start))

    def _at_and(self):
        return self._current >= len(self._source)

    def _indent(self, indent_sym):
        indent_len = 1
        if self._indent_lexeme:
            while self._peek() == indent_sym \
              and indent_len < len(self._indent_lexeme):
                indent_len += 1
                self._advance()
            self._add_token(TokenType.INDENT)
            if self._peek() == indent_sym:
                self._start = self._current
                self._advance()
                self._indent(indent_sym)
        else:
            while self._peek() == indent_sym:
                indent_len += 1
                self._advance()
            self._indent_lexeme = self._source[self._start:self._current]
            self._add_token(TokenType.INDENT)

    def _comment(self):
        while self._peek() != '\x0d' and not self._at_and():
            self._advance()

        self._add_token(TokenType.COMMENT)

    def _block_comment(self):
        level = 1
        # c = self._peek()
        while not self._at_and():
            if self._peek() == '\x0d' and self._peek_next() == '\x0a':
                self._current += 2
                self._line_no += 1
                self._line_start = self._current
            if self._peek() == '/' and self._peek_next() == '*':
                self._current += 2
                level += 1
                continue
            if self._peek() == '*' and self._peek_next() == '/':
                self._current += 2
                level -= 1
                if level == 0:
                    break
                continue
            self._advance()
        else:
            return

        self._add_token(TokenType.BLOCK_COMMENT)

    def _string(self):
        c = self._peek()
        while not self._at_and() and c.isprintable():
            if self._peek() == '\\' and self._peek_next() in '\"\'':
                self._current += 2
                continue
            if self._peek() in '\"\'':
                self._current += 1
                break
            self._advance()
        else:
            return

        text = self._source[self._start+1:self._current-1]
        self._add_token(TokenType.STRING, text)

    def _number(self):
        source = self._source[self._start:]
        match = _number.match(source)
        if match:
            group = match.lastgroup
            value = match[group]
            self._current += len(value) - 1
            if group == 'int':
                self._add_token(TokenType.NUMBER, int(value))
            elif group == 'float':
                self._add_token(TokenType.NUMBER, float(value))
            elif group == 'bin':
                self._add_token(TokenType.NUMBER, int(value[:-1], base=2))
            elif group == 'hex':
                self._add_token(TokenType.NUMBER, int(value[:-1], base=16))
            return

        self._identifier()

    def _identifier(self):
        while _is_alphanum(self._peek()):
            self._advance()
        text = self._source[self._start:self._current]
        if text in _keywords:
            type = _keywords[text]
        else:
            type = TokenType.IDENTIFIER
        self._add_token(type)

    def _directive(self):
        while _is_alpha(self._peek()):
            self._advance()
        text = self._source[self._start:self._current]
        if text == '#include':
            self._add_token(TokenType.INCLUDE)
        elif text == '#insert':
            self._add_token(TokenType.INSERT)
        else:
            pass
