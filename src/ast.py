"""
Abstract Syntax Tree (AST) node definitions for C-Lite.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Any

# ==================== Visitor Pattern Base Classes ====================

class ASTNode(ABC):
    """
    Abstract base class for all AST nodes.
    Implements Visitor Pattern for tree traversal (Week 13: Interpreters).
    """
    
    @abstractmethod
    def accept(self, visitor: 'ASTVisitor') -> Any:
        """Accept a visitor for tree traversal."""
        pass
    
    @abstractmethod
    def __repr__(self) -> str:
        """String representation for debugging."""
        pass


class ASTVisitor(ABC):
    """
    Abstract base class for AST visitors.
    Enables separation of traversal logic from node structure.
    
    CO523 Week 13: Visitor Pattern for interpreter implementation.
    """
    
    @abstractmethod
    def visit_program(self, node: 'Program') -> Any:
        """Visit Program node (root of AST)"""
        pass
    
    @abstractmethod
    def visit_declaration(self, node: 'Declaration') -> Any:
        """Visit Declaration node (variable declaration)"""
        pass
    
    @abstractmethod
    def visit_assignment(self, node: 'Assignment') -> Any:
        """Visit Assignment node (variable assignment)"""
        pass
    
    @abstractmethod
    def visit_if_statement(self, node: 'IfStatement') -> Any:
        """Visit IfStatement node (conditional)"""
        pass
    
    @abstractmethod
    def visit_block(self, node: 'Block') -> Any:
        """Visit Block node (scope block)"""
        pass
    
    @abstractmethod
    def visit_printf_call(self, node: 'PrintfCall') -> Any:
        """Visit PrintfCall node (output function)"""
        pass
    
    @abstractmethod
    def visit_binary_op(self, node: 'BinaryOp') -> Any:
        """Visit BinaryOp node (binary expression)"""
        pass
    
    @abstractmethod
    def visit_unary_op(self, node: 'UnaryOp') -> Any:
        """Visit UnaryOp node (unary expression)"""
        pass
    
    @abstractmethod
    def visit_number_literal(self, node: 'NumberLiteral') -> Any:
        """Visit NumberLiteral node (numeric constant)"""
        pass
    
    @abstractmethod
    def visit_identifier(self, node: 'Identifier') -> Any:
        """Visit Identifier node (variable reference)"""
        pass
    
    @abstractmethod
    def visit_empty_statement(self, node: 'EmptyStatement') -> Any:
        """Visit EmptyStatement node (no-op statement)"""
        pass


# ==================== Program Structure Nodes ====================

@dataclass(frozen=True)
class Program(ASTNode):
    """
    Root node of the AST.
    Represents the entire C-Lite program.
    """
    declarations: List['Declaration']
    statements: List[ASTNode]
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_program(self)
    
    def __repr__(self) -> str:
        return f"Program(declarations={len(self.declarations)}, statements={len(self.statements)})"


@dataclass(frozen=True)
class Declaration(ASTNode):
    """
    Variable declaration: int x; or float y;
    Project Spec §3: Variables must be declared before use.
    """
    var_type: str  # 'int' or 'float'
    name: str
    line: int
    column: int
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_declaration(self)
    
    def __repr__(self) -> str:
        return f"Declaration(type={self.var_type}, name={self.name})"


# ==================== Statement Nodes ====================

@dataclass(frozen=True)
class Assignment(ASTNode):
    """
    Assignment statement: x = expression;
    Project Spec §3: Assignment operator =
    """
    name: str
    value: ASTNode  # Expression node
    line: int
    column: int
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_assignment(self)
    
    def __repr__(self) -> str:
        return f"Assignment(name={self.name}, value={self.value})"


@dataclass(frozen=True)
class IfStatement(ASTNode):
    """
    Conditional statement: if (expr) stmt [else stmt]
    Project Spec §3: Basic conditional logic (if-else)
    """
    condition: ASTNode  # Expression node
    then_branch: ASTNode  # Statement
    else_branch: Optional[ASTNode]  # Statement or None
    line: int
    column: int
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_if_statement(self)
    
    def __repr__(self) -> str:
        return f"IfStatement(condition={self.condition}, else={self.else_branch is not None})"


@dataclass(frozen=True)
class Block(ASTNode):
    """
    Block statement: { statements }
    Introduces new scope for variable lifetime (Week 4: Scopes)
    """
    statements: List[ASTNode]
    line: int
    column: int
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_block(self)
    
    def __repr__(self) -> str:
        return f"Block(statements={len(self.statements)})"


@dataclass(frozen=True)
class PrintfCall(ASTNode):
    """
    Built-in printf() function: printf(expression);
    Project Spec §3: Standard I/O
    """
    argument: ASTNode  # Expression node
    line: int
    column: int
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_printf_call(self)
    
    def __repr__(self) -> str:
        return f"PrintfCall(argument={self.argument})"


@dataclass(frozen=True)
class EmptyStatement(ASTNode):
    """
    Empty statement: ;
    Valid but no-op statement
    """
    line: int
    column: int
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_empty_statement(self)
    
    def __repr__(self) -> str:
        return "EmptyStatement()"


# ==================== Expression Nodes ====================

@dataclass(frozen=True)
class BinaryOp(ASTNode):
    """
    Binary operation: left op right
    Project Spec §3: Arithmetic (+,-,*,/) and Comparison (>,<,==)
    """
    left: ASTNode
    operator: str  # '+', '-', '*', '/', '>', '<', '=='
    right: ASTNode
    line: int
    column: int
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_binary_op(self)
    
    def __repr__(self) -> str:
        return f"BinaryOp(left={self.left}, op={self.operator}, right={self.right})"


@dataclass(frozen=True)
class UnaryOp(ASTNode):
    """
    Unary operation: +expr or -expr
    Supports negation and positive sign
    """
    operator: str  # '+' or '-'
    operand: ASTNode
    line: int
    column: int
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_unary_op(self)
    
    def __repr__(self) -> str:
        return f"UnaryOp(op={self.operator}, operand={self.operand})"


@dataclass(frozen=True)
class NumberLiteral(ASTNode):
    """
    Numeric literal: integer or float
    Project Spec §3: Data Types (int, float)
    """
    value: Any  # int or float
    line: int
    column: int
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_number_literal(self)
    
    def __repr__(self) -> str:
        return f"NumberLiteral(value={self.value})"


@dataclass(frozen=True)
class Identifier(ASTNode):
    """
    Variable reference: x
    Must be declared before use (semantic check in Phase 3)
    """
    name: str
    line: int
    column: int
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_identifier(self)
    
    def __repr__(self) -> str:
        return f"Identifier(name={self.name})"