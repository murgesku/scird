from rscript.lang.ast import *


class Stringifier(Visitor):

    def __init__(self, lang):
        """
        :type lang: blockpar.BlockPar
        """
        if lang is None:
            self.make_substitution = False
            self.lang = None
        else:
            self.make_substitution = True
            self.lang = lang
        self.level = -1

    def process(self, unit):
        result = unit.accept(self)
        return result

    def process_sequence(self, seq, *, level=-1):
        self.level = level
        result = []
        i = 0
        while i < len(seq):
            unit = seq[i]
            if unit.type is TokenType.INDENT:
                c = 1  # _c_ounter
                while (i+1 < len(seq)) and seq[i+1].type is TokenType.INDENT:
                    c += 1
                    i += 1
                if self.level < 0:
                    self.level = c
                c -= self.level
                if c > 0:
                    result += (unit.lexeme * c)
            else:
                result.append(unit.accept(self))
            i += 1
        return ''.join(result)

    def visit_token(self, tok):
        return tok.lexeme

    def visit_literal_expr(self, expr):
        return expr.children[expr.value].lexeme

    def visit_variable_expr(self, expr):
        return expr.children[expr.name].lexeme

    def visit_access_expr(self, expr):
        return self.process_sequence(expr.children, level=self.level)

    def visit_call_expr(self, expr):
        if self.make_substitution:
            return Interpreter(self.lang).evaluate(expr)
        return self.process_sequence(expr.children, level=self.level)

    def visit_array_expr(self, expr):
        return self.process_sequence(expr.children, level=self.level)

    def visit_group_expr(self, expr):
        return self.process_sequence(expr.children, level=self.level)

    def visit_unary_expr(self, expr):
        return self.process_sequence(expr.children, level=self.level)

    def visit_binary_expr(self, expr):
        return self.process_sequence(expr.children, level=self.level)

    def visit_assign_expr(self, expr):
        return self.process_sequence(expr.children, level=self.level)

    def visit_vardecl_expr(self, expr):
        return self.process_sequence(expr.children, level=self.level)

    def visit_expression_stmt(self, stmt):
        return self.process_sequence(stmt.children, level=self.level)

    def visit_block_stmt(self, stmt):
        return '{' + self.process_sequence(stmt.children, level=self.level) + '}'

    def visit_vardecl_stmt(self, stmt):
        return self.process_sequence(stmt.children, level=self.level)

    def visit_function_stmt(self, stmt):
        return self.process_sequence(stmt.children, level=self.level)

    def visit_class_stmt(self, stmt):
        return self.process_sequence(stmt.children, level=self.level)

    def visit_if_stmt(self, stmt):
        return self.process_sequence(stmt.children, level=self.level)

    def visit_for_stmt(self, stmt):
        return self.process_sequence(stmt.children, level=self.level)

    def visit_while_stmt(self, stmt):
        return self.process_sequence(stmt.children, level=self.level)

    def visit_try_stmt(self, stmt):
        return self.process_sequence(stmt.children, level=self.level)

    def visit_throw_stmt(self, stmt):
        return self.process_sequence(stmt.children, level=self.level)

    def visit_keyword_stmt(self, stmt):
        return self.process_sequence(stmt.children, level=self.level)


class Interpreter(Visitor):

    def __init__(self, lang):
        if lang is None:
            self.make_substitution = False
            self.lang = None
        else:
            self.make_substitution = True
            self.lang = lang

    def evaluate(self, unit):
        return unit.accept(self)

    def visit_token(self, tok):
        pass

    def visit_literal_expr(self, expr):
        return expr.children[expr.value].literal

    def visit_variable_expr(self, expr):
        raise NotImplementedError()

    def visit_access_expr(self, expr):
        raise NotImplementedError()

    def visit_call_expr(self, expr):
        name = Stringifier(None).process(expr.children[expr.name])
        if name == "CT":
            if self.make_substitution:
                path = self.evaluate(expr.children[expr.arguments[0]])
                path = path.split('.')
                result = self.lang
                for p in path:
                    result = result[p][0].content
                return result
            else:
                return Stringifier(None).process(expr)
        elif name == "Format":
            if self.make_substitution:
                source = expr.arguments[0]
                result = self.evaluate(expr.children[source])
                for tag, string in zip(expr.arguments[1::2], expr.arguments[2::2]):
                    tag = self.evaluate(expr.children[tag])
                    string = Stringifier(None).process(expr.children[string])
                    string = f"<{string}>"
                    result = result.replace(tag, string)
                return result
            else:
                return Stringifier(None).process(expr)
        raise NotImplementedError()

    def visit_array_expr(self, expr):
        raise NotImplementedError()

    def visit_group_expr(self, expr):
        return self.evaluate(expr.children[expr.expression])

    def visit_unary_expr(self, expr):
        right = self.evaluate(expr.children[expr.right])
        operator = expr.children[expr.operator]
        if operator.type is TokenType.MINUS:
            return -right
        elif operator.type is TokenType.BIT_NOT:
            return ~right
        elif operator.type is TokenType.NOT:
            return not right
        return

    def visit_binary_expr(self, expr):
        left = self.evaluate(expr.children[expr.left])
        right = self.evaluate(expr.children[expr.right])
        operator = expr.children[expr.operator]
        if operator.type is TokenType.PLUS:
            if isinstance(left, str):
                return left + str(right)
            else:
                return left + right
        elif operator.type is TokenType.MINIS:
            return left - right
        elif operator.type is TokenType.MUL:
            return left * right
        elif operator.type is TokenType.DIV:
            if isinstance(left, int):
                return left // right
            else:
                return left / right
        elif operator.type is TokenType.MOD:
            return left % right
        elif operator.type is TokenType.AND:
            return left and right
        elif operator.type is TokenType.OR:
            return left or right
        elif operator.type is TokenType.EQUAL:
            return left == right
        elif operator.type is TokenType.NOT_EQUAL:
            return left != right
        elif operator.type is TokenType.MORE:
            return left > right
        elif operator.type is TokenType.LESS:
            return left < right
        elif operator.type is TokenType.MORE_EQUAL:
            return left >= right
        elif operator.type is TokenType.LESS_EQUAL:
            return left <= right
        elif operator.type is TokenType.BIT_AND:
            return left & right
        elif operator.type is TokenType.BIT_OR:
            return left | right
        elif operator.type is TokenType.Bit_XOR:
            return left ^ right
        elif operator.type is TokenType.SHL:
            return left << right
        elif operator.type is TokenType.SHR:
            return left >> right
        return

    def visit_assign_expr(self, expr):
        raise NotImplementedError()

    def visit_vardecl_expr(self, expr):
        raise NotImplementedError()

    def visit_expression_stmt(self, stmt):
        raise NotImplementedError()

    def visit_block_stmt(self, stmt):
        raise NotImplementedError()

    def visit_vardecl_stmt(self, stmt):
        raise NotImplementedError()

    def visit_function_stmt(self, stmt):
        raise NotImplementedError()

    def visit_class_stmt(self, stmt):
        raise NotImplementedError()

    def visit_if_stmt(self, stmt):
        raise NotImplementedError()

    def visit_for_stmt(self, stmt):
        raise NotImplementedError()

    def visit_while_stmt(self, stmt):
        raise NotImplementedError()

    def visit_try_stmt(self, stmt):
        raise NotImplementedError()

    def visit_throw_stmt(self, stmt):
        raise NotImplementedError()

    def visit_keyword_stmt(self, stmt):
        raise NotImplementedError()
