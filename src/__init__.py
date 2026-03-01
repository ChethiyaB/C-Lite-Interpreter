"""
Public API for the C-Lite interpreter.
"""

from .lexer import Lexer
from .token import Token, TokenType
from .errors import LexerError, ParserError, SemanticError
from .ast import (
    ASTNode, ASTVisitor,
    Program, Declaration, Assignment, IfStatement, Block, PrintfCall,
    BinaryOp, UnaryOp, NumberLiteral, Identifier, EmptyStatement
)

__all__ = [
    # Lexical Analysis
    'Lexer', 'Token', 'TokenType', 'LexerError',
    
    # Syntax Analysis
    'ASTNode', 'ASTVisitor',
    'Program', 'Declaration', 'Assignment', 'IfStatement', 
    'Block', 'PrintfCall', 'BinaryOp', 'UnaryOp', 
    'NumberLiteral', 'Identifier', 'EmptyStatement',
    
    # Semantic Analysis
    'ParserError', 'SemanticError'
]