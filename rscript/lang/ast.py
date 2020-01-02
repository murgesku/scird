__all__ = ["Visitor", "TokenType", "Token", "insignificant", "Expr", "Stmt",
           "LiteralExpr", "VariableExpr", "AccessExpr", "CallExpr", "ArrayExpr",
           "GroupExpr", "UnaryExpr", "BinaryExpr", "AssignExpr", "VarDeclExpr",
           "ExpressionStmt", "VarDeclStmt", "FunctionStmt", "ClassStmt",
           "IfStmt", "WhileStmt", "ForStmt", "TryStmt", "ThrowStmt",
           "KeywordStmt", "BlockStmt"]

from abc import ABC, abstractmethod
from enum import Enum

_tokens = ("LPAREN", "RPAREN", "LBRACE", "RBRACE", "LSQUARE", "RSQUARE",
           "COMMA", "DOT", "COLON", "SEMICOLON", "POINTER",
           "ASSIGN", "MINUS", "PLUS", "MUL", "DIV", "MOD",
           "BIT_NOT", "BIT_AND", "BIT_OR", "BIT_XOR", "SHL", "SHR",
           "NOT", "AND", "OR",
           "EQUAL", "NOT_EQUAL", "LESS", "MORE", "LESS_EQUAL", "MORE_EQUAL",
           "IDENTIFIER", "NUMBER", "INTEGER", "DWORD", "FLOAT", "STRING",
           "TYPE",
           "IF", "ELSE", "WHILE", "FOR", "BREAK", "CONTINUE", "EXIT",
           "FUNCTION", "CLASS", "INCLUDE", "INSERT",
           "TRY", "CATCH", "FINALLY", "THROW",
           "NEWLINE", "INDENT", "TAB", "SPACE", "COMMENT", "BLOCK_COMMENT",
           "END")

# noinspection PyArgumentList
TokenType = Enum("TokenType", _tokens)
del _tokens


class Token:
    __slots__ = "type", "lexeme", "literal", "line", "column",

    def __init__(self, type, lexeme, literal, line, column):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
        self.column = column

    def __repr__(self):
        return f"{self.type.name}({self.lexeme}) at {self.line}:{self.column}"


insignificant = (TokenType.INDENT, TokenType.SPACE,
                 TokenType.TAB, TokenType.NEWLINE,
                 TokenType.COMMENT, TokenType.BLOCK_COMMENT)


class Expr:
    __slots__ = "children",

    def __init__(self, children):
        """
        :type children: list[Token|Expr]
        """
        self.children = children if children is not None else []

    @abstractmethod
    def accept(self, visitor):
        pass


class LiteralExpr(Expr):
    """
    Represent number or string value.
    """
    __slots__ = "value",

    def __init__(self, children, value):
        """
        :param value: Index of "value" unit
        :type value: int
        """
        super().__init__(children)
        self.value = value

    def accept(self, visitor):
        return visitor.visit_literal_expr(self)


class VariableExpr(Expr):
    """
    Represent variable or function identifier.
    """
    __slots__ = "name",

    def __init__(self, children, name):
        """
        :param name: Index of "name" unit
        :type name: int
        """
        super().__init__(children)
        self.name = name

    def accept(self, visitor):
        return visitor.visit_variable_expr(self)


class AccessExpr(Expr):
    """
    Represent access to object member.
    """
    __slots__ = "object", "name",

    def __init__(self, children, object, name):
        """
        :param object: Index of "object" unit
        :type object: int
        :param name: Index of "name" unit
        :type name: int
        """
        super().__init__(children)
        self.object = object
        self.name = name

    def accept(self, visitor):
        return visitor.visit_access_expr(self)


class CallExpr(Expr):
    """
    Represent function call.
    """
    __slots__ = "name", "arguments",

    def __init__(self, children, name, arguments):
        """
        :type name: int
        :type arguments: tuple[int]
        """
        super().__init__(children)
        self.name = name
        self.arguments = arguments

    def accept(self, visitor):
        return visitor.visit_call_expr(self)


class ArrayExpr(Expr):
    __slots__ = "name", "indices",

    def __init__(self, children, name, indices):
        """
        :type name: int
        :type indices: tuple[int]
        """
        super().__init__(children)
        self.name = name
        self.indices = indices

    def accept(self, visitor):
        return visitor.visit_array_expr(self)


class GroupExpr(Expr):
    __slots__ = "expression",

    def __init__(self, children, expression):
        """
        :type expression: int
        """
        super().__init__(children)
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_group_expr(self)


class UnaryExpr(Expr):
    __slots__ = "operator", "right",

    def __init__(self, children, operator, right):
        """
        :type operator: int
        :type right: int
        """
        super().__init__(children)
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_unary_expr(self)


class BinaryExpr(Expr):
    __slots__ = "operator", "left", "right",

    def __init__(self, children, left, operator, right):
        """
        :type left: int
        :type operator: int
        :type right: int
        """
        super().__init__(children)
        self.operator = operator
        self.left = left
        self.right = right

    def accept(self, visitor):
        return visitor.visit_binary_expr(self)


class AssignExpr(Expr):
    __slots__ = "target", "value",

    def __init__(self, children, target, value):
        super().__init__(children)
        self.target = target
        self.value = value

    def accept(self, visitor):
        return visitor.visit_assign_expr(self)


class VarDeclExpr(Expr):
    __slots__ = "type", "variables",

    def __init__(self, children, type, variables):
        """
        :type type: int
        :type variables: tuple[tuple[int]]
        """
        super().__init__(children)
        self.type = type
        self.variables = variables

    def accept(self, visitor):
        return visitor.visit_vardecl_expr(self)


class Stmt:
    __slots__ = "children",

    def __init__(self, children):
        """
        @type children: list[Token|Expr|Stmt]
        """
        self.children = children if children is not None else []

    @abstractmethod
    def accept(self, visitor):
        pass


class ExpressionStmt(Stmt):
    __slots__ = "expression",

    def __init__(self, children, expression):
        """
        :type expression: int
        """
        super().__init__(children)
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_expression_stmt(self)


class BlockStmt(Stmt):
    __slots__ = "statements",

    def __init__(self, children, statements):
        """
        :type statements: tuple[int]
        """
        super().__init__(children)
        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_block_stmt(self)


class VarDeclStmt(Stmt):
    __slots__ = "type", "variables",

    def __init__(self, children, type, variables):
        """
        :type type: int
        :type variables: tuple[tuple[int]]
        """
        super().__init__(children)
        self.type = type
        self.variables = variables

    def accept(self, visitor):
        return visitor.visit_vardecl_stmt(self)


class FunctionStmt(Stmt):
    __slots__ = "name", "parameters", "body",

    def __init__(self, children, name, parameters, body):
        """
        :type name: int
        :type parameters: tuple[tuple[int]]
        :type body: int
        """
        super().__init__(children)
        self.name = name
        self.parameters = parameters
        self.body = body

    def accept(self, visitor):
        return visitor.visit_function_stmt(self)


class ClassStmt(Stmt):
    __slots__ = "name", "parents", "body",

    def __init__(self, children, name, parents, body):
        super().__init__(children)
        self.name = name
        self.parents = parents
        self.body = body

    def accept(self, visitor):
        return visitor.visit_class_stmt(self)


class IfStmt(Stmt):
    __slots__ = "condition", "then_branch", "else_branch",

    def __init__(self, children, condition, then_branch, else_branch):
        super().__init__(children)
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor):
        return visitor.visit_if_stmt(self)


class WhileStmt(Stmt):
    __slots__ = "condition", "body",

    def __init__(self, children, condition, body):
        super().__init__(children)
        self.condition = condition
        self.body = body

    def accept(self, visitor):
        return visitor.visit_while_stmt(self)


class ForStmt(Stmt):
    __slots__ = "initializer", "condition", "increment", "body",

    def __init__(self, children, initializer, condition, increment, body):
        """
        :type initializer: tuple[int]
        :type condition: int
        :type increment: tuple[int]
        :type body: int
        """
        super().__init__(children)
        self.initializer = initializer
        self.condition = condition
        self.increment = increment
        self.body = body

    def accept(self, visitor):
        return visitor.visit_for_stmt(self)


class TryStmt(Stmt):
    __slots__ = "try_branch", "exception", "catch_branch", "finally_branch",

    def __init__(self, children, try_branch, exception, catch_branch, finally_branch):
        """
        :type try_branch: int
        :param exception: -1 if missing
        :type exception: int
        :param catch_branch: -1 if missing
        :type catch_branch: int
        :param finally_branch: -1 if missing
        :type finally_branch: int
        """
        super().__init__(children)
        self.try_branch = try_branch
        self.exception = exception
        self.catch_branch = catch_branch
        self.finally_branch = finally_branch

    def accept(self, visitor):
        return visitor.visit_try_stmt(self)


class ThrowStmt(Stmt):
    __slots__ = "expression",

    def __init__(self, children, expression):
        super().__init__(children)
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_throw_stmt(self)


class KeywordStmt(Stmt):
    __slots__ = "keyword",

    def __init__(self, children, keyword):
        super().__init__(children)
        self.keyword = keyword

    def accept(self, visitor):
        return visitor.visit_keyword_stmt(self)


class Visitor(ABC):
    @abstractmethod
    def visit_literal_expr(self, expr):
        """:type expr: LiteralExpr"""
        pass

    @abstractmethod
    def visit_variable_expr(self, expr):
        """:type expr: VariableExpr"""
        pass

    @abstractmethod
    def visit_access_expr(self, expr):
        """:type expr: AccessExpr"""
        pass

    @abstractmethod
    def visit_call_expr(self, expr):
        """:type expr: CallExpr"""
        pass

    @abstractmethod
    def visit_array_expr(self, expr):
        """:type expr: ArrayExpr"""
        pass

    @abstractmethod
    def visit_group_expr(self, expr):
        """:type expr: GroupExpr"""
        pass

    @abstractmethod
    def visit_unary_expr(self, expr):
        """:type expr: UnaryExpr"""
        pass

    @abstractmethod
    def visit_binary_expr(self, expr):
        """:type expr: BinaryExpr"""
        pass

    @abstractmethod
    def visit_assign_expr(self, expr):
        """:type expr: AssignExpr"""
        pass

    @abstractmethod
    def visit_vardecl_expr(self, expr):
        """:type expr: VarDeclExpr"""
        pass

    @abstractmethod
    def visit_expression_stmt(self, stmt):
        """:type stmt: ExpressionStmt"""
        pass

    @abstractmethod
    def visit_block_stmt(self, stmt):
        """:type stmt: BlockStmt"""
        pass

    @abstractmethod
    def visit_vardecl_stmt(self, stmt):
        """:type stmt: VarDeclStmt"""
        pass

    @abstractmethod
    def visit_function_stmt(self, stmt):
        """:type stmt: FunctionStmt"""
        pass

    @abstractmethod
    def visit_class_stmt(self, stmt):
        """:type stmt: ClassStmt"""
        pass

    @abstractmethod
    def visit_if_stmt(self, stmt):
        """:type stmt: IfStmt"""
        pass

    @abstractmethod
    def visit_for_stmt(self, stmt):
        """:type stmt: ForStmt"""
        pass

    @abstractmethod
    def visit_while_stmt(self, stmt):
        """:type stmt: WhileStmt"""
        pass

    @abstractmethod
    def visit_try_stmt(self, stmt):
        """:type stmt: TryStmt"""
        pass

    @abstractmethod
    def visit_throw_stmt(self, stmt):
        """:type stmt: ThrowStmt"""
        pass

    @abstractmethod
    def visit_keyword_stmt(self, stmt):
        """:type stmt: KeywordStmt"""
        pass
