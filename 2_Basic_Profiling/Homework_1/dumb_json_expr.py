from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Any
from dataclasses import dataclass


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: ExprVisitor) -> None:
        pass

class ExprVisitor(ABC):
    @abstractmethod
    def visit_literal(self, element: Literal) -> None:
        ...
    
    @abstractmethod
    def visit_unary(self, element: Unary) -> None:
        ...
    
    @abstractmethod
    def visit_binary(self, element: Binary) -> None:
        ...
    
    @abstractmethod
    def visit_grouping(self, element: Grouping) -> None:
        ...

@dataclass
class Literal(Expr):
    value: Any

    def accept(self, visitor: ExprVisitor) -> None:
        return visitor.visit_literal(self)

@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor: ExprVisitor) -> None:
        return visitor.visit_unary(self)
    
@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: ExprVisitor) -> None:
        return visitor.visit_binary(self) 

@dataclass
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor: ExprVisitor) -> None:
        return visitor.visit_grouping(self)



class AstPrinter(ExprVisitor):

    def do_it(self, expr: Expr) -> str:
        print(expr.accept(self))
        return expr.accept(self)

    def _parenthasize(self, name, *exprs: Expr) -> str:
        return f"({name} {' '.join([expr.accept(self) for expr in exprs])})"

    def visit_literal(self, expr: Literal) -> None:
        if expr.value == None:
            return "nil"
        return str(expr.value)
    
    def visit_unary(self, expr: Unary) -> None:
        return self._parenthasize(expr.operator.lexeme, expr.right)

    def visit_binary(self, expr: Binary) -> None:
        return self._parenthasize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping(self, expr: Grouping) -> None:
        return self._parenthasize("group", expr.expression)

if __name__ == "__main__":
    test_expression = Binary(
        left=Unary(
            operator=Token(
                TokenType.MINUS, 
                "-", 
                None, 
                1
            ),
            right=Literal(
                123
            )
        ),
        operator=Token(
            TokenType.STAR, 
            "*", 
            None, 
            1
        ), 
        right=Grouping(
            Literal(
                45.67
            )
        )
    )
    john=Literal(45.67)
    
    printer = AstPrinter()
    print(printer.do_it(test_expression))
