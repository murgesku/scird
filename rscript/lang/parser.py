from rscript.lang.ast import *


class ParseError(RuntimeError):
    def __init__(self, token, message):
        self.token = token
        self.message = message


class Parser:
    """
    :type _tokens: list[Token|Expr|Stmt]
    :type _start: int
    :type _current: int
    """
    def __init__(self, tokens):
        """
        :type tokens: list[Token]
        """
        self._tokens = tokens.copy()
        self._start = 0
        self._current = 0

    def parse(self):
        while not self._at_end():
            self._statement()
        return self._tokens

    # def parse_expression(self):
    #     return self._expression()

    def _advance(self):
        """
        :rtype: Token
        """
        if self._peek().type is not TokenType.END:
            self._current += 1
        return self._tokens[self._current - 1]

    def _match(self, *types):
        """
        :type types: list[Token]
        :rtype: bool
        """
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
        """
        :type type: TokenType
        :type message: str
        :rtype: Token
        """
        if self._peek().type is type:
            return self._advance()
        else:
            while self._peek().type in insignificant:
                self._current += 1
                if self._peek().type is type:
                    return self._advance()
        raise ParseError(self._peek(), message)

    def _check(self, type):
        """
        :type type: TokenType
        :rtype: bool
        """
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
        """
        :rtype: Token
        """
        return self._tokens[self._current]

    def _previous(self):
        """
        :rtype: Token
        """
        current = self._current
        while self._tokens[current - 1].type in insignificant:
            current -= 1
        return self._tokens[current - 1]

    def _at_end(self):
        """
        :rtype: bool
        """
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

    def _statement(self):
        if self._match(TokenType.IF):
            return self._if_stmt()
        elif self._match(TokenType.WHILE):
            return self._while_stmt()
        elif self._match(TokenType.FOR):
            return self._for_stmt()
        elif self._match(TokenType.FUNCTION):
            return self._function()
        elif self._match(TokenType.CLASS):
            return self._class()
        elif self._match(TokenType.TYPE):
            return self._var_decl_stmt()
        elif self._match(TokenType.BREAK, TokenType.CONTINUE, TokenType.EXIT):
            return self._keyword()
        elif self._match(TokenType.TRY):
            return self._try_stmt()
        elif self._match(TokenType.THROW):
            return self._throw_stmt()
        # elif self._match(TokenType.INCLUDE, TokenType.INSERT):
        #     return self._directive()
        elif self._match(TokenType.LBRACE):
            return self._block()
        else:
            return self._expr_stmt()

    def _keyword(self):
        begin = self._current - 1
        if type == TokenType.BREAK:
            self._consume(TokenType.SEMICOLON,
                          "Expect ';' after 'brake' statement.")
        elif type == TokenType.CONTINUE:
            self._consume(TokenType.SEMICOLON,
                          "Expect ';' after 'continue' statement.")
        elif type == TokenType.EXIT:
            self._consume(TokenType.SEMICOLON,
                          "Expect ';' after 'exit' statement.")
        else:
            return
        end = self._current
        unit = KeywordStmt(self._tokens[begin:end], 0)
        self._tokens[begin:end] = (unit,)
        self._current = begin + 1

    # def _directive(self):
    #     self._consume(TokenType.STRING,
    #                   "Expect path after directive.")
    #     return

    def _throw_stmt(self):
        begin = self._current - 1
        expression = -1
        if not self._check(TokenType.SEMICOLON):
            self._expression()
            expression = self._current - begin - 1
        self._consume(TokenType.SEMICOLON,
                      "Expect ';' after 'throw' statement.")
        end = self._current
        unit = ThrowStmt(self._tokens[begin:end], expression)
        self._tokens[begin:end] = (unit,)
        self._current = begin + 1

    def _try_stmt(self):
        begin = self._current - 1
        self._consume(TokenType.LBRACE,
                      "Expect '{' after 'try'.")
        self._block()
        try_branch = self._current - begin - 1

        exception = -1
        catch_branch = -1
        finally_branch = -1
        if self._match(TokenType.CATCH):
            if self._match(TokenType.LPAREN):
                self._consume(TokenType.IDENTIFIER,
                              "Expect exception name.")
                exception = self._current - begin - 1
            self._consume(TokenType.RPAREN,
                          "Expect ')'.")
            self._consume(TokenType.LBRACE,
                          "Expect '{' after 'catch'.")
            self._block()
            catch_branch = self._current - begin - 1
        elif self._match(TokenType.FINALLY):
            self._consume(TokenType.LBRACE,
                          "Expect '{' after 'finally'.")
            self._block()
            finally_branch = self._current - begin - 1
        end = self._current

        unit = TryStmt(self._tokens[begin:end], try_branch,
                                                exception,
                                                catch_branch,
                                                finally_branch)
        self._tokens[begin:end] = (unit,)
        self._current = begin + 1

    def _var_decl_stmt(self):
        begin = self._current - 1
        variables = []
        while True:
            self._consume(TokenType.IDENTIFIER,
                          "Expect variable name.")
            name = self._current - begin - 1
            init = -1
            if self._match(TokenType.ASSIGN):
                self._expression()
                init = self._current - begin - 1

            variables.append((name, init))
            if not self._match(TokenType.COMMA):
                break

        self._consume(TokenType.SEMICOLON,
                      "Expect ';' after variable declaration.")
        end = self._current

        unit = VarDeclStmt(self._tokens[begin:end], 0, tuple(variables))
        self._tokens[begin:end] = (unit,)
        self._current = begin + 1

    def _for_stmt(self):
        begin = self._current - 1
        self._consume(TokenType.LPAREN,
                      "Expect '(' after 'for'.")

        initializer = []
        if not self._check(TokenType.SEMICOLON):
            if self._match(TokenType.TYPE):
                self._var_decl_expr()
                index = self._current - begin - 1
                initializer.append(index)
            else:
                while True:
                    self._expression()
                    index = self._current - begin - 1
                    initializer.append(index)
                    if not self._match(TokenType.COMMA):
                        break
        self._consume(TokenType.SEMICOLON,
                      "Expect ';' after loop initializer.")

        condition = -1
        if not self._check(TokenType.SEMICOLON):
            self._expression()
            condition = self._current - begin - 1
        self._consume(TokenType.SEMICOLON,
                      "Expect ';' after loop condition.")

        increment = []
        if not self._check(TokenType.RPAREN):
            while True:
                self._expression()
                index = self._current - begin - 1
                increment.append(index)
                if not self._match(TokenType.COMMA):
                    break
        self._consume(TokenType.RPAREN,
                      "Expect ')' after 'for' clauses.")

        body = -1
        if not self._match(TokenType.SEMICOLON):
            self._statement()
            body = self._current - begin - 1

        end = self._current
        unit = ForStmt(self._tokens[begin:end], tuple(initializer),
                                                condition,
                                                tuple(increment),
                                                body)
        self._tokens[begin:end] = unit
        self._current = begin + 1

    def _while_stmt(self):
        begin = self._current - 1
        self._consume(TokenType.LPAREN,
                      "Expect '(' after 'while'.")
        self._expression()
        condition = self._current - begin - 1
        self._consume(TokenType.RPAREN,
                      "Expect ')' after condition.")

        body = -1
        if not self._match(TokenType.SEMICOLON):
            self._statement()
            body = self._current - begin - 1

        end = self._current
        unit = WhileStmt(self._tokens[begin:end], condition,
                                                  body)
        self._tokens[begin:end] = (unit,)
        self._current = begin + 1

    def _if_stmt(self):
        begin = self._current - 1
        self._consume(TokenType.LPAREN,
                      "Expect '(' after 'if'.")
        self._expression()
        condition = self._current - begin - 1
        self._consume(TokenType.RPAREN,
                      "Expect ')' after condition.")

        then_branch = -1
        if not self._match(TokenType.SEMICOLON):
            self._statement()
            then_branch = self._current - begin - 1

        else_branch = -1
        if self._match(TokenType.ELSE):
            self._statement()
            else_branch = self._current - begin - 1

        end = self._current
        unit = IfStmt(self._tokens[begin:end], condition,
                                               then_branch,
                                               else_branch)
        self._tokens[begin:end] = (unit,)
        self._current = begin + 1

    def _class(self):
        begin = self._current - 1
        self._consume(TokenType.IDENTIFIER,
                      "Expect class name.")
        name = self._current - begin - 1

        parents = []
        if self._match(TokenType.COLON):
            while True:
                self._consume(TokenType.IDENTIFIER,
                              "Expect superclass name.")
                parent = self._current - begin - 1
                parents.append(parent)
                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.LBRACE,
                      "Expect '{' before class body.")
        self._block()
        body = self._current - begin - 1

        end = self._current
        unit = ClassStmt(self._tokens[begin:end], name,
                                                  tuple(parents),
                                                  body)
        self._tokens[begin:end] = (unit,)
        self._current = begin + 1

    def _function(self):
        begin = self._current - 1
        self._consume(TokenType.IDENTIFIER,
                      "Expect function name.")
        name = self._current - begin - 1

        self._consume(TokenType.LPAREN,
                      "Expect '(' after function name.")

        parameters = []
        if not self._check(TokenType.RPAREN):
            while True:
                type = -1
                if self._match(TokenType.TYPE):
                    type = self._current - begin - 1

                self._consume(TokenType.IDENTIFIER,
                              "Expect parameter name.")
                arg = self._current - begin - 1

                init = -1
                if self._match(TokenType.ASSIGN):
                    if self._match(TokenType.STRING, TokenType.NUMBER):
                        init = self._current - begin - 1

                parameters.append((type, arg, init))

                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RPAREN,
                      "Expect ')' after parameters.")

        self._consume(TokenType.LBRACE,
                      "Expect '{' before function body.")
        self._block()
        body = self._current - begin - 1

        end = self._current
        unit = FunctionStmt(self._tokens[begin:end], name,
                                                     tuple(parameters),
                                                     body)
        self._tokens[begin:end] = (unit,)
        self._current = begin + 1

    def _block(self):
        begin = self._current - 1
        statements = []
        while not self._check(TokenType.RBRACE):
            self._statement()
            index = self._current - begin - 1
            statements.append(index)
        self._consume(TokenType.RBRACE,
                      "Expect '}' after block.")
        end = self._current
        unit = BlockStmt(self._tokens[begin:end], tuple(statements))
        self._tokens[begin:end] = (unit,)
        self._current = begin + 1

    def _expr_stmt(self):
        begin = self._current
        self._expression()
        self._consume(TokenType.SEMICOLON,
                      "Expect ';' after expression.")
        end = self._current
        unit = ExpressionStmt(self._tokens[begin:end], 0)
        self._tokens[begin:end] = (unit,)
        self._current = begin + 1

    def _expression(self):
        self._assignment()

    def _assignment(self):
        begin = self._current
        self._logical_or()
        if self._match(TokenType.ASSIGN):
            self._assignment()
            value = self._current - begin - 1
            end = self._current
            unit = AssignExpr(self._tokens[begin:end], 0, value)
            self._tokens[begin:end] = (unit,)
            self._current = begin + 1

    def _logical_or(self):
        begin = self._current
        self._logical_and()
        while self._match(TokenType.OR):
            op = self._current - begin - 1
            self._logical_and()
            right = self._current - begin - 1
            end = self._current
            unit = BinaryExpr(self._tokens[begin:end], 0, op, right)
            self._tokens[begin:end] = (unit,)
            self._current = begin + 1

    def _logical_and(self):
        begin = self._current
        self._bitwise_and()
        while self._match(TokenType.AND):
            op = self._current - begin - 1
            self._bitwise_or()
            right = self._current - begin - 1
            end = self._current
            unit = BinaryExpr(self._tokens[begin:end], 0, op, right)
            self._tokens[begin:end] = (unit,)
            self._current = begin + 1

    def _bitwise_or(self):
        begin = self._current
        self._bitwise_and()
        while self._match(TokenType.BIT_OR):
            op = self._current - begin - 1
            self._bitwise_and()
            right = self._current - begin - 1
            end = self._current
            unit = BinaryExpr(self._tokens[begin:end], 0, op, right)
            self._tokens[begin:end] = (unit,)
            self._current = begin + 1

    def _bitwise_and(self):
        begin = self._current
        self._equality()
        while self._match(TokenType.BIT_AND):
            op = self._current - begin - 1
            self._equality()
            right = self._current - begin - 1
            end = self._current
            unit = BinaryExpr(self._tokens[begin:end], 0, op, right)
            self._tokens[begin:end] = (unit,)
            self._current = begin + 1

    def _equality(self):
        begin = self._current
        self._comparison()
        while self._match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            op = self._current - begin - 1
            self._comparison()
            right = self._current - begin - 1
            end = self._current
            unit = BinaryExpr(self._tokens[begin:end], 0, op, right)
            self._tokens[begin:end] = (unit,)
            self._current = begin + 1

    def _comparison(self):
        begin = self._current
        self._shift()
        while self._match(TokenType.MORE, TokenType.MORE_EQUAL,
                          TokenType.LESS, TokenType.LESS_EQUAL):
            op = self._current - begin - 1
            self._shift()
            right = self._current - begin - 1
            end = self._current
            unit = BinaryExpr(self._tokens[begin:end], 0, op, right)
            self._tokens[begin:end] = (unit,)
            self._current = begin + 1

    def _shift(self):
        begin = self._current
        self._addition()
        while self._match(TokenType.SHL, TokenType.SHR):
            op = self._current - begin - 1
            self._addition()
            right = self._current - begin - 1
            end = self._current
            unit = BinaryExpr(self._tokens[begin:end], 0, op, right)
            self._tokens[begin:end] = (unit,)
            self._current = begin + 1

    def _addition(self):
        begin = self._current
        self._multiplication()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op = self._current - begin - 1
            self._multiplication()
            right = self._current - begin - 1
            end = self._current
            unit = BinaryExpr(self._tokens[begin:end], 0, op, right)
            self._tokens[begin:end] = (unit,)
            self._current = begin + 1

    def _multiplication(self):
        begin = self._current
        self._unary()
        while self._match(TokenType.MUL, TokenType.DIV, TokenType.MOD):
            op = self._current - begin - 1
            self._unary()
            right = self._current - begin - 1
            end = self._current
            unit = BinaryExpr(self._tokens[begin:end], 0, op, right)
            self._tokens[begin:end] = (unit,)
            self._current = begin + 1

    def _unary(self):
        if self._match(TokenType.MINUS, TokenType.BIT_NOT, TokenType.NOT):
            begin = self._current - 1
            self._unary()
            index = self._current - begin - 1
            end = self._current
            unit = UnaryExpr(self._tokens[begin:end], 0, index)
            self._tokens[begin:end] = (unit,)
            self._current = begin + 1
        else:
            self._operand()

    def _var_decl_expr(self):
        begin = self._current - 1
        variables = []
        while True:
            self._consume(TokenType.IDENTIFIER,
                          "Expect variable name.")
            name = self._current - begin - 1
            init = -1
            if self._match(TokenType.ASSIGN):
                self._expression()
                init = self._current - begin - 1

            variables.append((name, init))
            if not self._match(TokenType.COMMA):
                break
        end = self._current

        unit = VarDeclExpr(self._tokens[begin:end], 0, tuple(variables))
        self._tokens[begin:end] = (unit,)
        self._current = begin + 1

    def _array(self, begin):
        indices = []
        if not self._check(TokenType.RSQUARE):
            while True:
                self._expression()
                index = self._current - begin - 1
                indices.append(index)
                if not self._match(TokenType.COMMA):
                    break
        self._consume(TokenType.RSQUARE,
                      "Expect bracket after indices.")
        end = self._current

        unit = ArrayExpr(self._tokens[begin:end], 0, tuple(indices))
        self._tokens[begin:end] = (unit,)
        self._current = begin + 1

    def _call(self, begin):
        arguments = []
        if not self._check(TokenType.RPAREN):
            while True:
                self._expression()
                index = self._current - begin - 1
                arguments.append(index)
                if not self._match(TokenType.COMMA):
                    break
        self._consume(TokenType.RPAREN,
                      "Expect bracket after arguments.")
        end = self._current

        unit = CallExpr(self._tokens[begin:end], 0, tuple(arguments))
        self._tokens[begin:end] = (unit,)
        self._current = begin + 1

    def _typecast(self):
        begin = self._current - 1
        end = self._current
        unit = VariableExpr(self._tokens[begin:end], 0)
        self._tokens[begin:end] = (unit,)

        self._consume(TokenType.LPAREN,
                      "Expect bracket after typecast operator.")
        arguments = []
        if not self._check(TokenType.RPAREN):
            self._expression()
            index = self._current - begin - 1
            arguments.append(index)
        self._consume(TokenType.RPAREN,
                      "Expect bracket after typecast argument.")
        end = self._current

        unit = CallExpr(self._tokens[begin:end], 0, tuple(arguments))
        self._tokens[begin:end] = (unit,)
        self._current = begin + 1

    def _variable(self):
        begin = self._current - 1
        end = self._current
        unit = VariableExpr(self._tokens[begin:end], 0)
        self._tokens[begin:end] = (unit,)

        if self._match(TokenType.DOT):
            self._consume(TokenType.IDENTIFIER,
                          "Expect property name after '.'.")
            index = self._current - begin - 1
            end = self._current
            unit = AccessExpr(self._tokens[begin:end], 0, index)
            self._tokens[begin:end] = (unit,)
            self._current = begin + 1

        if self._match(TokenType.LPAREN):
            self._call(begin)
        elif self._match(TokenType.LSQUARE):
            self._array(begin)

    def _operand(self):
        if self._match(TokenType.STRING, TokenType.NUMBER):
            begin = self._current - 1
            end = self._current
            unit = LiteralExpr(self._tokens[begin:end], 0)
            self._tokens[begin:end] = (unit,)
        elif self._match(TokenType.IDENTIFIER):
            self._variable()
        elif self._match(TokenType.TYPE):
            self._typecast()
        elif self._match(TokenType.LPAREN):
            begin = self._current - 1
            self._expression()
            index = self._current - begin - 1
            self._consume(TokenType.RPAREN,
                          "Expect ')' after expression.")
            end = self._current
            unit = GroupExpr(self._tokens[begin:end], index)
            self._tokens[begin:end] = (unit,)
            self._current = begin + 1
