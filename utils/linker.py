from rscript.lang.ast import *
from rscript.file.enums import op_


class Linker:
    source = None
    lang = None
    interpreter = None

    @classmethod
    def init(cls, source, lang):
        """
        :type source: svr.SourceScript
        :type lang: blockpar.BlockPar
        """
        cls.source = source
        cls.lang = lang

    def __init__(self, units, block, pool, *, type=op_.NORMAL, level=0):
        self._units = units
        self._block = block
        self._pool = pool
        self._type = type
        self._level = level

        self._start = 0
        self._current = 0

    def build(self):
        while not self._at_end():
            unit = self._advance()

            if isinstance(unit, IfStmt):
                if unit.else_branch == -1:
                    if self._probe():
                        self._if_stmt()

    def _advance(self):
        if not self._at_end():
            self._current += 1
        return self._units[self._current - 1]

    def _at_end(self):
        unit = self._units[self._current]
        if isinstance(unit, Token):
            if unit.type is TokenType.END:
                return True

    def _probe(self):
        start = self._current
        while not self._at_end():
            unit = self._units[self._current]
            if isinstance(unit, IfStmt):
                if unit.else_branch != -1:
                    return False
            elif isinstance(unit, ExpressionStmt):
                expr = unit.children[unit.expression]
                if isinstance(expr, CallExpr):
                    name = expr.children[expr.name]
                    if name.lexeme not in ("DChange", "DAdd", "ChangeState"):
                        return False
                else:
                    return False
            elif isinstance(unit, KeywordStmt):
                keyword = unit.children[unit.keyword]
                if keyword.type is not TokenType.EXIT:
                    return False
            elif isinstance(unit, Token):
                if unit.type not in (TokenType.SEMICOLON, TokenType.RBRACE) \
                        and unit.type not in insignificant:
                    return False
            else:
                return False
            self._current += 1
        self._current = start
        return True

    def _push(self):
        pass

    def _if_stmt(self):
        pass
