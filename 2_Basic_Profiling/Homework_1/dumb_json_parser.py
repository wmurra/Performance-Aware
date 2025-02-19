from __future__ import annotations
from pathlib import Path
from enum import Enum, auto
from dataclasses import dataclass

from abc import ABC, abstractmethod
from typing import List, Any
from dataclasses import dataclass


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: ExprVisitor) -> None:
        pass

class ExprVisitor(ABC):
    @abstractmethod
    def visit_string(self, element: JsonString) -> None:
        ...
    
    @abstractmethod
    def visit_number(self, element: JsonNumber) -> None:
        ...
    
    @abstractmethod
    def visit_key_value_pair(self, element: KeyValuePair) -> None:
        ...
    
    @abstractmethod
    def visit_list(self, element: JsonList) -> None:
        ...
    
    @abstractmethod
    def visit_dict(self, element: JsonDict) -> None:
        ...
        

@dataclass
class JsonString(Expr):
    value: Any

    def accept(self, visitor: ExprVisitor) -> None:
        return visitor.visit_string(self)

@dataclass
class JsonNumber(Expr):
    value: Any

    def accept(self, visitor: ExprVisitor) -> None:
        return visitor.visit_number(self)
    
@dataclass
class KeyValuePair(Expr):
    # its made of a STRING COLON STRING | NUMBER
    key: JsonString
    value: Expr

    def accept(self, visitor: ExprVisitor) -> None:
        return visitor.visit_key_value_pair(self) 

@dataclass
class JsonList(Expr):
    values: list[Expr]

    def accept(self, visitor: ExprVisitor) -> None:
        return visitor.visit_list(self)

@dataclass
class JsonDict(Expr):
    items: list[KeyValuePair]

    def accept(self, visitor: ExprVisitor) -> None:
        return visitor.visit_dict(self)

class TokenType(Enum): 
    LEFT_BRACE = auto()  # {
    RIGHT_BRACE = auto()  # }
    LEFT_BRACKET = auto()  # [
    RIGHT_BRACKET = auto()  # ]
    COMMA = auto()  # ,
    COLON = auto()  # :
    STRING = auto()  # "string"
    NUMBER = auto()  # 123
    TRUE = auto()  # true
    FALSE = auto()  # false
    NULL = auto()  # null
    UNKNOWN = auto()
    EOF = auto()  # end of file

    def __str__(self):
        return self.name

@dataclass
class Token:
   token_type: TokenType
   lexeme: str

   def __str__(self):
      return f"{self.token_type} {self.lexeme}"

class jsonScanner:
    def __init__(self, source):
        self.source = source
        self.tail = 0
        self.index = 0
        self.tokens: list[Token] = []

    def _add_token(self, token_type: TokenType):
        self.tokens.append(Token(
            token_type,
            lexeme=self.source[self.tail:self.index],
        ))
        
    def _current_char(self) -> str:
        if not self._at_end():
            return self.source[self.index-1]

    def _key_word_search(self):
        ...

    def _add_string(self):
        while True:
            self.index +=1
            if self._current_char() == '"':
                break
            if self._at_end():
                break
        self._add_token(TokenType.STRING)

    def _add_number(self):
        while True:
            self.index +=1
            char = self._current_char()
            if self._at_end():
                break
            if not (char.isdigit() or char == '.'):
                self.index -=1
                break
        self._add_token(TokenType.NUMBER)
    
    def _advance(self):
        self.index +=1
        char = self._current_char()
        if not char:
            return
        match char: 
            case ' ': ...
            case '[': self._add_token(TokenType.LEFT_BRACKET)
            case ']': self._add_token(TokenType.RIGHT_BRACKET)
            case '{': self._add_token(TokenType.LEFT_BRACE)
            case '}': self._add_token(TokenType.RIGHT_BRACE)
            case ':': self._add_token(TokenType.COLON)
            case ',': self._add_token(TokenType.COMMA)
            case '"': self._add_string()
            case _:
                if char == '-' or char.isdigit():
                    self._add_number()
                elif self._key_word_search():
                    ... # lets just neglect to support true false and null, 
                    # it will make life better
                else:
                    self._add_token(TokenType.UNKNOWN)
            

    def _at_end(self) -> bool:
        if self.index > len(self.source):
            return True
        return False

    def scan_tokens(self):
        while not self._at_end():
            self._advance()
            self.tail = self.index
        self.tokens.append(Token(
            token_type=TokenType.EOF,
            lexeme='',
        ))

class jsonParser():
    def __init__(self, tokens):
        self.tokens: list[Token] = tokens
        self.current = 0

    def _match(self, *token_types: tuple[TokenType]):
        for token_type in token_types:
            if self._check(token_type):
                self._advance()
                return True
        return False
    
    def _check(self, token_type: TokenType):
        if self._at_end(): 
            return False
        return self._peek().token_type == token_type
    
    def _advance(self):
        if not self._at_end():
            self.current += 1
        return self._previous()

    def _peek(self) -> Token:
        return self.tokens[self.current]
    
    def _at_end(self) -> bool:
        return self._peek().token_type == TokenType.EOF

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]


    def _primary(self)  -> Expr:
        if self._match(TokenType.NUMBER):
            return JsonNumber(self._previous().lexeme)
        if self._match(TokenType.STRING):
            return JsonString(self._previous().lexeme)


        if self._match(TokenType.LEFT_BRACKET):
            expr = JsonList(values=[])
            while not self._match(TokenType.RIGHT_BRACKET):
                expr.values.append(self._primary())
                if self._match(TokenType.RIGHT_BRACKET):
                    break
                if not self._match(TokenType.COMMA): # so the way this is written trailing comma is legal. but who cares
                    raise SyntaxError("Perhaps you forgot a comma.")
            return expr


        if self._match(TokenType.LEFT_BRACE):
            expr = JsonDict(items=[])
            while not self._match(TokenType.RIGHT_BRACE):
                expr.items.append(self._parse_key_val_pair())
                if self._match(TokenType.RIGHT_BRACE):
                    break
                if not self._match(TokenType.COMMA): # so the way this is written trailing comma is legal. but who cares
                    raise SyntaxError("Perhaps you forgot a comma.")
            return expr

        raise SyntaxError(f"Expect Expression. {print(self._peek().token_type)}")

    def _parse_key_val_pair(self):
        if self._match(TokenType.STRING):
            key = JsonString(self._previous().lexeme)
        if not self._match(TokenType.COLON):
            raise SyntaxError("Perhaps you forgot a colon?")
        value = self._primary()
        key_val_pair = KeyValuePair(
            key=key,
            value=value
        )
        return key_val_pair


    def parse(self):
        try:
            return self._primary()
        except SyntaxError as e:
            print(e)

source_path = Path('test.json')
# source_path = Path('haversine.json')
with source_path.open() as f:
    source_code = f.read()
    scanner = jsonScanner(source_code)
    scanner.scan_tokens()
    parser = jsonParser(scanner.tokens)
    # [print(str(token)) for token in scanner.tokens]
    expr = parser.parse()
    
    print(expr)
    # scanner = Scanner(source_code)
    # tokens = scanner.scan_tokens()
    # # print([token.lexeme for token in tokens])
    # parser = Parser(tokens)
    # final_expr = parser.parse()
    # print(final_expr)
    # print(AstPrinter().do_it(final_expr))

