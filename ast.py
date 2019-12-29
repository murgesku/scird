__all__ = ["Visitor",
           "LiteralExpr", "VariableExpr", "AccessExpr", "CallExpr", "ArrayExpr",
           "GroupExpr", "UnaryExpr", "BinaryExpr", "AssignExpr", "DeclarationExpr",
           "ExpressionStmt", "DeclarationStmt", "FunctionStmt", "ClassStmt",
           "IfStmt", "WhileStmt", "ForStmt", "TryStmt", "ThrowStmt",
           "BreakStmt", "ContinueStmt", "ExitStmt", "BlockStmt"]

from abc import ABCMeta


class Visitor(metaclass=ABCMeta):
    def visit_literal_expr(self, expr): pass
    def visit_variable_expr(self, expr): pass
    def visit_access_expr(self, expr): pass
    def visit_call_expr(self, expr): pass
    def visit_array_expr(self, expr): pass
    def visit_group_expr(self, expr): pass
    def visit_unary_expr(self, expr): pass
    def visit_binary_expr(self, expr): pass
    def visit_assign_expr(self, expr): pass
    def visit_declaration_expr(self, expr): pass

    def visit_expression_stmt(self, stmt): pass
    def visit_block_stmt(self, stmt): pass
    def visit_declaration_stmt(self, stmt): pass
    def visit_function_stmt(self, stmt): pass
    def visit_class_stmt(self, stmt): pass
    def visit_if_stmt(self, stmt): pass
    def visit_for_stmt(self, stmt): pass
    def visit_while_stmt(self, stmt): pass
    def visit_try_stmt(self, stmt): pass
    def visit_throw_stmt(self, stmt): pass
    def visit_break_stmt(self, stmt): pass
    def visit_continue_stmt(self, stmt): pass
    def visit_exit_stmt(self, stmt): pass


class Expr(metaclass=ABCMeta):
    def accept(self, visitor):
        pass


class LiteralExpr(Expr):
    __slots__ = "value",

    def __init__(self, value):
        self.value = value

    def accept(self, visitor):
        return visitor.visit_literal_expr(self)


class VariableExpr(Expr):
    __slots__ = "name",

    def __init__(self, name):
        self.name = name

    def accept(self, visitor):
        return visitor.visit_variable_expr(self)


class AccessExpr(Expr):
    __slots__ = "object", "name",

    def __init__(self, object, name):
        self.object = object
        self.name = name

    def accept(self, visitor):
        return visitor.visit_access_expr(self)


class CallExpr(Expr):
    __slots__ = "name", "arguments",

    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def accept(self, visitor):
        return visitor.visit_call_expr(self)


class ArrayExpr(Expr):
    __slots__ = "name", "indices",

    def __init__(self, name, indices):
        self.name = name
        self.indices = indices

    def accept(self, visitor):
        return visitor.visit_array_expr(self)


class GroupExpr(Expr):
    __slots__ = "expression",

    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_group_expr(self)


class UnaryExpr(Expr):
    __slots__ = "operator", "right",

    def __init__(self, operator, right):
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_unary_expr(self)


class BinaryExpr(Expr):
    __slots__ = "operator", "left", "right",

    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right

    def accept(self, visitor):
        return visitor.visit_binary_expr(self)


class AssignExpr(Expr):
    __slots__ = "name", "value",

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def accept(self, visitor):
        return visitor.visit_assign_expr(self)


class DeclarationExpr(Expr):
    __slots__ = "variables",

    def __init__(self, variables):
        self.variables = variables

    def accept(self, visitor):
        return visitor.visit_declaration_expr(self)


class Stmt(metaclass=ABCMeta):
    def accept(self, visitor):
        pass


class ExpressionStmt(Stmt):
    __slots__ = "expression",

    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_expression_stmt(self)


class BlockStmt(Stmt):
    __slots__ = "statements",

    def __init__(self, statements):
        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_block_stmt(self)


class DeclarationStmt(Stmt):
    __slots__ = "variables",

    def __init__(self, variables):
        self.variables = variables

    def accept(self, visitor):
        return visitor.visit_declaration_stmt(self)


class FunctionStmt(Stmt):
    __slots__ = "name", "parameters", "body",

    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body

    def accept(self, visitor):
        return visitor.visit_function_stmt(self)


class ClassStmt(Stmt):
    __slots__ = "name", "parents", "body",

    def __init__(self, name, parents, body):
        self.name = name
        self.parents = parents
        self.body = body

    def accept(self, visitor):
        return visitor.visit_class_stmt(self)


class IfStmt(Stmt):
    __slots__ = "condition", "then_branch", "else_branch",

    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor):
        return visitor.visit_if_stmt(self)


class WhileStmt(Stmt):
    __slots__ = "condition", "body",

    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def accept(self, visitor):
        return visitor.visit_while_stmt(self)


class ForStmt(Stmt):
    __slots__ = "initializer", "condition", "increment", "body",

    def __init__(self, initializer, condition, increment, body):
        self.initializer = initializer
        self.condition = condition
        self.increment = increment
        self.body = body

    def accept(self, visitor):
        return visitor.visit_for_stmt(self)


class TryStmt(Stmt):
    __slots__ = "try_branch", "exception", "catch_branch", "finally_branch",

    def __init__(self, try_branch, exception, catch_branch, finally_branch):
        self.try_branch = try_branch
        self.exception = exception
        self.catch_branch = catch_branch
        self.finally_branch = finally_branch

    def accept(self, visitor):
        return visitor.visit_try_stmt(self)


class ThrowStmt(Stmt):
    __slots__ = "expression",

    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_throw_stmt(self)


class BreakStmt(Stmt):
    __slots__ = "keyword",

    def __init__(self):
        self.keyword = "break"

    def accept(self, visitor):
        return visitor.visit_break_stmt(self)


class ContinueStmt(Stmt):
    __slots__ = "keyword",

    def __init__(self):
        self.keyword = "continue"

    def accept(self, visitor):
        return visitor.visit_continue_stmt(self)


class ExitStmt(Stmt):
    __slots__ = "keyword",

    def __init__(self):
        self.keyword = "exit"

    def accept(self, visitor):
        return visitor.visit_exit_stmt(self)
