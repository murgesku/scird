from enum import Enum

from lexer import TokenType, Token
from parser import insignificant, binary

_tokens = ("IF_STMT",
           "CHSTATE_CALL", "DCHANGE_CALL", "DADD_CALL",
           "DTEXT_CALL", "DANSWER_CALL")

# noinspection PyArgumentList
SpecType = Enum("SpecType", _tokens)
del _tokens

_matchtok = {#"Ether": SpecType.ETHER_CALL,
             "DChange": SpecType.DCHANGE_CALL,
             "DAdd": SpecType.DADD_CALL,
             "DText": SpecType.DTEXT_CALL,
             "DAnswer": SpecType.DANSWER_CALL,
             "ChangeState": SpecType.CHSTATE_CALL}


class AnalyzeError(RuntimeError):
    def __init__(self, token, pos, message):
        self.token = token
        self.pos = pos
        self.message = message


class IfToken(Token):
    __slots__ = "tokens", "expression", "then_branch"

    def __init__(self, tokens, expression, then_branch):
        t = tokens[0]
        line, column = t.line, t.column
        super().__init__(SpecType.IF_STMT, None, None, line, column)
        self.tokens = tokens
        self.expression = expression
        self.then_branch = then_branch
        self.then_branch.append(Token(TokenType.END, "", None, -1, -1))


class CallToken(Token):
    __slots__ = "tokens", "arguments"

    def __init__(self, type, tokens, arguments):
        """
        @type type: SpecType
        @type arguments: list
        """
        t = tokens[0]
        line, column = t.line, t.column
        super().__init__(type, None, None, line, column)
        self.tokens = tokens
        self.tokens.append(Token(TokenType.END, "", None, -1, -1))
        self.arguments = arguments
        for arg in self.arguments:
            arg.append(Token(TokenType.END, "", None, -1, -1))


class Analyzer:

    def __init__(self, tokens):
        self._tokens = tokens

        self._start = 0
        self._current = 0

    def analyze(self):
        while not self._at_end():
            self._statement()
        return self._tokens

    def _advance(self):
        if self._peek().type is not TokenType.END:
            self._current += 1
        return self._tokens[self._current-1]

    def _match(self, *types):
        if self._peek().type is TokenType.END:
            return False
        if self._peek().type in types:
            self._advance()
            return True
        else:
            start = self._current
            while self._peek().type in insignificant:
                self._current += 1
                if self._peek().type is TokenType.END:
                    self._current = start
                    return False
                if self._peek().type in types:
                    self._advance()
                    return True
            self._current = start
        return False

    def _consume(self, type, message):
        if self._peek().type is type:
            return self._advance()
        else:
            while self._peek().type in insignificant:
                self._current += 1
                if self._peek().type is type:
                    return self._advance()
        raise AnalyzeError(self._peek(), self._current, message)

    def _check(self, type):
        if self._peek().type is TokenType.END:
            return False
        if self._peek().type is type:
            return True
        else:
            start = self._current
            while self._peek().type in insignificant:
                self._current += 1
                if self._peek().type is TokenType.END:
                    self._current = start
                    return False
                if self._peek().type is type:
                    return True
            self._current = start
        return False

    def _peek(self):
        return self._tokens[self._current]

    def _previous(self):
        current = self._current
        while self._tokens[current - 1].type in insignificant:
            current -= 1
        return self._tokens[current - 1]

    def _at_end(self):
        if self._peek().type is TokenType.END:
            return True
        else:
            start = self._current
            while self._peek().type in insignificant:
                self._current += 1
                if self._peek().type is TokenType.END:
                    return True
            self._current = start
        return False

    def _expression(self):
        begin = self._current
        self._assignment()
        end = self._current
        while self._tokens[end].type is not TokenType.NEWLINE \
          and self._tokens[end].type in insignificant:
            end += 1
        return self._tokens[begin:end]

    def _statement(self):
        begin = self._current
        if self._match(TokenType.IF):
            self._if_stmt()
        elif self._match(TokenType.WHILE):
            self._while_stmt()
        elif self._match(TokenType.FOR):
            self._for_stmt()
        elif self._match(TokenType.FUNCTION):
            self._function()
        elif self._match(TokenType.CLASS):
            self._class()
        elif self._match(TokenType.TYPE):
            self._var_decl_stmt()
        elif self._match(TokenType.BREAK, TokenType.CONTINUE, TokenType.EXIT):
            self._keyword()
        elif self._match(TokenType.TRY):
            self._try_stmt()
        elif self._match(TokenType.THROW):
            self._throw_stmt()
        # elif self._match(TokenType.INCLUDE, TokenType.INSERT):
        #     return self._directive()
        elif self._match(TokenType.LBRACE):
            self._block()
        else:
            self._expr_stmt()
        end = self._current
        while self._tokens[end].type is not TokenType.NEWLINE \
          and self._tokens[end].type in insignificant:
            end += 1
        return self._tokens[begin:end]

    def _keyword(self):
        self._consume(TokenType.SEMICOLON,
                      "Expect ';' after statement.")

    # def _directive(self):
    #     pass

    def _throw_stmt(self):
        if not self._check(TokenType.SEMICOLON):
            self._expression()
        self._consume(TokenType.SEMICOLON,
                      "Expect ';' after 'throw' statement.")

    def _try_stmt(self):
        self._consume(TokenType.LBRACE,
                      "Expect '{' after 'try'.")
        if self._match(TokenType.CATCH):
            if self._match(TokenType.LPAREN):
                self._consume(TokenType.IDENTIFIER,
                              "Expect exception name.")
            self._consume(TokenType.RPAREN,
                          "Expect ')'.")
            self._consume(TokenType.LBRACE,
                          "Expect '{' after 'catch'.")
            self._block()
        elif self._match(TokenType.FINALLY):
            self._consume(TokenType.LBRACE,
                          "Expect '{' after 'finally'.")
            self._block()

    def _var_decl_stmt(self):
        while True:
            self._consume(TokenType.IDENTIFIER,
                          "Expect variable name.")
            if self._match(TokenType.ASSIGN):
                self._expression()

            if not self._match(TokenType.COMMA):
                break

        self._consume(TokenType.SEMICOLON,
                      "Expect ';' after variable declaration.")

    def _for_stmt(self):
        self._consume(TokenType.LPAREN,
                      "Expect '(' after 'for'.")

        if not self._check(TokenType.SEMICOLON):
            if self._match(TokenType.TYPE):
                self._var_decl_expr()
            else:
                while True:
                    self._expression()
                    if not self._match(TokenType.COMMA):
                        break
        self._consume(TokenType.SEMICOLON,
                      "Expect ';' after loop initializer.")

        if not self._check(TokenType.SEMICOLON):
            self._expression()
        self._consume(TokenType.SEMICOLON,
                      "Expect ';' after loop condition.")

        if not self._check(TokenType.RPAREN):
            while True:
                self._expression()
                if not self._match(TokenType.COMMA):
                    break
        self._consume(TokenType.RPAREN,
                      "Expect ')' after 'for' clauses.")

        if not self._match(TokenType.SEMICOLON):
            self._statement()

    def _while_stmt(self):
        self._consume(TokenType.LPAREN,
                      "Expect '(' after 'while'.")
        self._expression()
        self._consume(TokenType.RPAREN,
                      "Expect ')' after condition.")
        if not self._match(TokenType.SEMICOLON):
            self._statement()

    def _if_stmt(self):
        begin = self._current - 1
        while self._tokens[begin - 1].type is not TokenType.NEWLINE \
          and self._tokens[begin - 1].type in insignificant:
            begin -= 1

        self._consume(TokenType.LPAREN,
                      "Expect '(' after 'if'.")
        condition = self._expression()
        self._consume(TokenType.RPAREN,
                      "Expect ')' after condition.")

        then_branch = []
        if not self._match(TokenType.SEMICOLON):
            then_branch = self._statement()

        if self._match(TokenType.ELSE):
            self._statement()
        else:
            end = self._current
            while self._tokens[end].type is not TokenType.NEWLINE \
              and self._tokens[end].type in insignificant:
                end += 1

            self._tokens[begin:end] = [IfToken(self._tokens[begin:end],
                                               condition,
                                               then_branch)]
            self._current = begin + 1

    def _class(self):
        self._consume(TokenType.IDENTIFIER,
                      "Expect class name.")

        if self._match(TokenType.COLON):
            while True:
                self._consume(TokenType.IDENTIFIER,
                              "Expect superclass name.")
                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.LBRACE,
                      "Expect '{' before class body.")
        self._block()

    def _function(self):
        self._consume(TokenType.IDENTIFIER,
                      "Expect function name.")

        self._consume(TokenType.LPAREN,
                      "Expect '(' after function name.")

        if not self._check(TokenType.RPAREN):
            while True:
                if self._match(TokenType.TYPE):
                    pass

                self._consume(TokenType.IDENTIFIER,
                              "Expect parameter name.")
                if self._match(TokenType.ASSIGN):
                    if self._match(TokenType.STRING, TokenType.NUMBER):
                        pass

                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RPAREN,
                      "Expect ')' after parameters.")

        self._consume(TokenType.LBRACE,
                      "Expect '{' before function body.")
        self._block()

    def _block(self):
        while not self._check(TokenType.RBRACE):
            self._statement()
        self._consume(TokenType.RBRACE,
                      "Expect '}' after block.")

    def _expr_stmt(self):
        self._expression()
        self._consume(TokenType.SEMICOLON,
                      "Expect ';' after expression.")

    def _var_decl_expr(self):
        while True:
            self._consume(TokenType.IDENTIFIER,
                          "Expect variable name.")
            if self._match(TokenType.ASSIGN):
                self._expression()

            if not self._match(TokenType.COMMA):
                break

    def _assignment(self):
        self._binary()
        if self._match(TokenType.ASSIGN):
            self._assignment()

    def _binary(self):
        self._unary()
        while self._match(*binary):
            self._unary()

    def _unary(self):
        if self._match(TokenType.MINUS, TokenType.BIT_NOT, TokenType.NOT):
            self._unary()
        self._operand()

    def _array(self):
        if not self._check(TokenType.RSQUARE):
            while True:
                self._expression()
                if not self._match(TokenType.COMMA):
                    break
        self._consume(TokenType.RSQUARE,
                      "Expect bracket after indices.")

    def _call(self, tok):
        if tok.lexeme in _matchtok.keys():
            begin = self._tokens.index(tok)
            while self._tokens[begin - 1].type is not TokenType.NEWLINE \
              and self._tokens[begin - 1].type in insignificant:
                begin -= 1

        arguments = []
        if not self._check(TokenType.RPAREN):
            while True:
                arguments.append(self._expression())
                if not self._match(TokenType.COMMA):
                    break
        self._consume(TokenType.RPAREN,
                      "Expect bracket after arguments.")

        if tok.lexeme in _matchtok.keys():
            end = self._current
            while self._tokens[end].type is not TokenType.NEWLINE \
              and self._tokens[end].type in insignificant:
                end += 1

            # noinspection PyUnboundLocalVariable
            self._tokens[begin:end] = [CallToken(_matchtok[tok.lexeme],
                                                 self._tokens[begin:end],
                                                 arguments)]
            self._current = begin + 1

    def _typecast(self):
        self._consume(TokenType.LPAREN,
                      "Expect bracket after typecast operator.")
        if not self._check(TokenType.RPAREN):
            self._expression()
        self._consume(TokenType.RPAREN,
                      "Expect bracket after typecast argument.")

    def _variable(self):
        tok = self._previous()

        # while self._match(TokenType.DOT):
        #     self._consume(TokenType.IDENTIFIER,
        #                   "Expect property name after '.'.")

        if self._match(TokenType.LPAREN):
            self._call(tok)
        elif self._match(TokenType.LSQUARE):
            self._array()

    def _operand(self):
        if self._match(TokenType.STRING, TokenType.NUMBER):
            return
        if self._match(TokenType.IDENTIFIER):
            return self._variable()
        if self._match(TokenType.TYPE):
            return self._typecast()
        if self._match(TokenType.LPAREN):
            self._expression()
            self._consume(TokenType.RPAREN,
                          "Expect ')' after expression.")
