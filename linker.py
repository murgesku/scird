from lexer import TokenType
from parser import Parser, insignificant
from analyzer import SpecType
from ast import *
from svr import *
from enums import op_, et_


class Linker:
    source = None
    lang = None
    interpreter = None

    @classmethod
    def init(cls, source, lang):
        """
        @type source: SourceScript
        @type lang: BlockPar
        """
        cls.source = source
        cls.lang = lang
        cls.interpreter = Interpreter(cls.lang)

    def __init__(self, tokens, block, pool, *, type=op_.NORMAL, level=0):
        self._tokens = tokens
        self._block = block
        self._pool = pool
        self._type = type
        self._level = level

        self._start = 0
        self._current = 0

    def build(self):
        while not self._at_end():
            tok = self._advance()

            if tok.type is SpecType.IF_STMT:
                self._if_stmt(tok)
            elif tok.type in (SpecType.DCHANGE_CALL,
                         SpecType.DADD_CALL,
                         SpecType.CHSTATE_CALL):
                self._link_call(tok)
            elif tok.type is SpecType.DTEXT_CALL:
                self._dtext_call(tok)
            elif tok.type is SpecType.DANSWER_CALL:
                self._danswer_call(tok)
            # elif tok.type is SpecType.ETHER_CALL:
            #     self._ether_call(tok)
            else:
                pass

    def _advance(self):
        if self._peek().type is not TokenType.END:
            self._current += 1
        return self._tokens[self._current - 1]

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

    def _consume(self, type):
        if self._peek().type is type:
            return self._advance()
        else:
            while self._peek().type in insignificant:
                self._current += 1
                if self._peek().type is type:
                    return self._advance()
        raise Exception()

    def _peek(self):
        return self._tokens[self._current]

    def _look(self, *types):
        """Просматриваем последовательность токенов вперёд"""
        start = self._current
        while not self._peek().type is TokenType.END:
            if self._peek().type not in insignificant:
                if self._peek().type not in types:
                    self._current = start
                    return False
            self._current += 1
        self._current = start
        return True

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

    def _push(self):
        tokens = self._tokens[self._start:self._current-1]

        if not tokens:
            return

        test = [x for x in tokens if (x.type not in insignificant) and
                                     (x.type not in (TokenType.LBRACE,
                                                     TokenType.RBRACE,
                                                     TokenType.SEMICOLON))]
        if not test:
            return

        if not self._block:
            self._block = self.source.add(ExprOp)
        elif not isinstance(self._block, ExprOp):
            block = self.source.add(ExprOp)
            self.source.link(self._block, block)
            self._block = block
        self._block.expression = self._stringify(tokens, self._level)
        self._block.type = self._type

        self._start = self._current

    def _if_stmt(self, tok):
        if not self._look(SpecType.IF_STMT,
                          SpecType.DCHANGE_CALL,
                          SpecType.DADD_CALL,
                          SpecType.CHSTATE_CALL,
                          TokenType.SEMICOLON,
                          TokenType.RBRACE,
                          TokenType.EXIT):
            tokens = tok.tokens

            if not (x for x in tokens if x not in insignificant):
                return

            if not self._block:
                self._block = self.source.add(ExprOp)
            elif not isinstance(self._block, ExprOp):
                block = self.source.add(ExprOp)
                self.source.link(self._block, block)
                self._block = block
            self._block.expression += self._stringify(tokens, self._level)
            return
        self._push()
        if_block = self.source.add(ExprIf)
        if self._block:
            self.source.link(self._block, if_block)
        if_block.expression = self._stringify_expr(tok.expression)
        if_block.type = self._type

        Linker(tok.then_branch, if_block, self._pool,
               type=op_.NORMAL, level=self._level+1).build()

        self._start = self._current

    def _link_call(self, tok):
        self._push()
        if self._block is None:
            raise Exception()
        expr = Parser(tok.arguments[0]).parse_expression()
        i = int(self.interpreter.evaluate(expr))
        self.source.link(self._block, self._pool[i])
        self._consume(TokenType.SEMICOLON)

    def _dtext_call(self, tok):
        self._push()
        if self._block is None:
            raise Exception()
        expr = Parser(tok.arguments[0]).parse_expression()
        text = self.interpreter.evaluate(expr)
        self._block.msg = text
        self._consume(TokenType.SEMICOLON)

    def _danswer_call(self, tok):
        self._push()
        if self._block is None:
            raise Exception()
        expr = Parser(tok.arguments[0]).parse_expression()
        text = self.interpreter.evaluate(expr)
        text = text.split('~', 1)[-1]
        self._block.msg = text
        self._consume(TokenType.SEMICOLON)

    def _ether_call(self, tok):
        self._push()
        expr = Parser(tok.arguments[0]).parse_expression()
        type = self.interpreter.evaluate(expr)
        expr = Parser(tok.arguments[1]).parse_expression()
        uid = self.interpreter.evaluate(expr)
        expr = Parser(tok.arguments[2]).parse_expression()
        msg = self.interpreter.evaluate(expr)
        et = self.source.add(Ether)
        et.type = et_(int(type))
        et.uid = uid.strip("\'\"")
        et.msg = msg
        if self._block:
            self.source.link(self._block, et)
        self._consume(TokenType.SEMICOLON)

    def _stringify(self, tokens, level):
        result = []
        i = 0
        while i < len(tokens):
            tok = tokens[i]
            if tok.type is TokenType.INDENT:
                counter = 1
                while tokens[i+counter].type is TokenType.INDENT:
                    counter += 1
                if level == 0:
                    level = counter
                counter -= level
                if counter > 0:
                    result += [tok.lexeme * counter]
            elif tok.lexeme is not None:
                result.append(tok.lexeme)
            i += 1
        return ''.join(result)

    def _stringify_expr(self, tokens):
        result = []
        for tok in tokens:
            if tok.lexeme is not None:
                result.append(tok.lexeme)
            elif tok.type in (SpecType.CT_CALL, SpecType.FORMAT_CALL):
                expr = Parser(tok.tokens).parse_expression()
                result.append(self.interpreter.evaluate(expr))
            else:
                raise NotImplementedError
        return ''.join(result)


class Interpreter(Visitor):
    def __init__(self, lang):
        if lang is None:
            self.text_flag = True
            self.lang = None
        else:
            self.text_flag = False
            self.lang = lang

    # def interpret(self, ast):
    #     return self.evaluate(ast)

    def visit_literal_expr(self, expr):
        if self.text_flag:
            return expr.value.lexeme
        else:
            return expr.value.literal

    def visit_variable_expr(self, expr):
        if self.text_flag:
            return expr.name.lexeme
        else:
            raise NotImplementedError

    def visit_access_expr(self, expr):
        if self.text_flag:
            return self.evaluate(expr.object) + '.' + expr.name.lexeme
        else:
            raise NotImplementedError

    def visit_call_expr(self, expr):
        name = self.evaluate(expr.name, text=True)
        if self.text_flag:
            result = [name, '(']
            for argument in expr.arguments:
                if argument is not expr.arguments[0]:
                    result.append(', ')
                result.append(self.evaluate(argument, text=True))
            result.append(')')
            return ''.join(result)
        else:
            if name == "CT":
                path = self.evaluate(expr.arguments[0])
                path = path.split('.')
                result = self.lang
                for p in path:
                    result = result[p][0]
                return result
            elif name == "Format":
                source = self.evaluate(expr.arguments[0])
                result = source
                for tag, string in zip(expr.arguments[1::2], expr.arguments[2::2]):
                    tag = self.evaluate(tag)
                    string = self.evaluate(string, text=True)
                    string = f"<{string}>"
                    result = result.replace(tag, string)
                return result
            else:
                raise NotImplementedError

    def visit_array_expr(self, expr):
        if self.text_flag:
            result = [self.evaluate(expr.name), '[']
            for index in expr.indices:
                if index is not expr.indices[0]:
                    result.append(', ')
                result.append(self.evaluate(index))
            result.append(']')
            return ''.join(result)
        else:
            raise NotImplementedError

    def visit_group_expr(self, expr):
        if self.text_flag:
            return '(' + self.evaluate(expr.expression) + ')'
        else:
            return self.evaluate(expr.expression)

    def visit_unary_expr(self, expr):
        if self.text_flag:
            return expr.operator.lexeme + self.evaluate(expr.right)
        else:
            right = self.evaluate(expr.right)
            if expr.operator.type is TokenType.MINUS:
                return -right
            elif expr.operator.type is TokenType.BIT_NOT:
                return ~right
            elif expr.operator.type is TokenType.NOT:
                return not right
            return

    def visit_binary_expr(self, expr):
        if self.text_flag:
            result = [self.evaluate(expr.left),
                      ' ',
                      expr.operator.lexeme,
                      ' ',
                      self.evaluate(expr.right)]
            return ''.join(result)
        else:
            left = self.evaluate(expr.left)
            right = self.evaluate(expr.right)
            if expr.operator.type is TokenType.PLUS:
                if isinstance(left, str):
                    return left + str(right)
                else:
                    return left + right
            elif expr.operator.type is TokenType.MINIS:
                return left - right
            elif expr.operator.type is TokenType.MUL:
                return left * right
            elif expr.operator.type is TokenType.DIV:
                if isinstance(left, int):
                    return left // right
                else:
                    return left / right
            elif expr.operator.type is TokenType.MOD:
                return left % right
            elif expr.operator.type is TokenType.AND:
                return left and right
            elif expr.operator.type is TokenType.OR:
                return left or right
            elif expr.operator.type is TokenType.EQUAL:
                return left == right
            elif expr.operator.type is TokenType.NOT_EQUAL:
                return left != right
            elif expr.operator.type is TokenType.MORE:
                return left > right
            elif expr.operator.type is TokenType.LESS:
                return left < right
            elif expr.operator.type is TokenType.MORE_EQUAL:
                return left >= right
            elif expr.operator.type is TokenType.LESS_EQUAL:
                return left <= right
            elif expr.operator.type is TokenType.BIT_AND:
                return left & right
            elif expr.operator.type is TokenType.BIT_OR:
                return left | right
            elif expr.operator.type is TokenType.Bit_XOR:
                return left ^ right
            elif expr.operator.type is TokenType.SHL:
                return left << right
            elif expr.operator.type is TokenType.SHR:
                return left >> right
            return

    def visit_assign_expr(self, expr):
        if self.text_flag:
            result = [self.evaluate(expr.name),
                      ' = ',
                      self.evaluate(expr.value)]
            return ''.join(result)
        else:
            raise NotImplementedError

    def evaluate(self, expr, text=False):
        if text:
            old_text_flag = self.text_flag
            self.text_flag = True
            result = expr.accept(self)
            self.text_flag = old_text_flag
            return result
        else:
            return expr.accept(self)
