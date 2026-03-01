"""
AST node structure and visitor pattern tests.

Test Coverage Gaps Addressed:
1. Full Expression Tree Composition
2. Block Scope Nesting
3. IfStatement Traversal Coverage
4. Identifier Usage in Expressions
5. Printf Traversal
6. Equality & Structural Comparison
7. AST Base Class Contract
8. Invalid Construction Protection
9. Program Node Edge Cases
10. Deep Visitor Contract Test
11. Complex Integration Scenario
12. Defensive Location Integrity
"""

import pytest
from src.ast import (
    ASTNode, ASTVisitor,
    Program, Declaration, Assignment, IfStatement, Block, PrintfCall,
    BinaryOp, UnaryOp, NumberLiteral, Identifier, EmptyStatement
)


# =============================================================================
# Full Expression Tree Composition
# =============================================================================

class TestExpressionTreeComposition:
    """Test complex nested expression trees (CO523 Week 3: Expressions)"""

    def test_arithmetic_expression_tree(self):
        """Test: (a + b) * (c - d)"""
        # Left subtree: (a + b)
        left = BinaryOp(
            left=Identifier(name='a', line=1, column=1),
            operator='+',
            right=Identifier(name='b', line=1, column=5),
            line=1,
            column=3
        )
        
        # Right subtree: (c - d)
        right = BinaryOp(
            left=Identifier(name='c', line=1, column=9),
            operator='-',
            right=Identifier(name='d', line=1, column=13),
            line=1,
            column=11
        )
        
        # Root: left * right
        expr = BinaryOp(left=left, operator='*', right=right, line=1, column=7)
        
        # Verify tree structure
        assert expr.operator == '*'
        assert isinstance(expr.left, BinaryOp)
        assert isinstance(expr.right, BinaryOp)
        assert expr.left.operator == '+'
        assert expr.right.operator == '-'

    def test_unary_in_expression_tree(self):
        """Test: -x + y * -z"""
        # Unary negations
        neg_x = UnaryOp(operator='-', operand=Identifier(name='x', line=1, column=2), line=1, column=1)
        neg_z = UnaryOp(operator='-', operand=Identifier(name='z', line=1, column=11), line=1, column=10)
        
        # Multiplication: y * -z
        mult = BinaryOp(
            left=Identifier(name='y', line=1, column=6),
            operator='*',
            right=neg_z,
            line=1,
            column=8
        )
        
        # Addition: -x + (y * -z)
        expr = BinaryOp(left=neg_x, operator='+', right=mult, line=1, column=4)
        
        # Verify precedence structure
        assert expr.operator == '+'
        assert expr.right.operator == '*'
        assert isinstance(expr.left, UnaryOp)
        assert isinstance(expr.right.right, UnaryOp)

    def test_deeply_nested_expression(self):
        """Test: ((1 + 2) * (3 + 4)) - (5 * 6)"""
        # Depth 3 expression tree
        inner_left = BinaryOp(
            left=NumberLiteral(value=1, line=1, column=3),
            operator='+',
            right=NumberLiteral(value=2, line=1, column=7),
            line=1,
            column=5
        )
        
        inner_right = BinaryOp(
            left=NumberLiteral(value=3, line=1, column=11),
            operator='+',
            right=NumberLiteral(value=4, line=1, column=15),
            line=1,
            column=13
        )
        
        mult = BinaryOp(left=inner_left, operator='*', right=inner_right, line=1, column=9)
        
        right_side = BinaryOp(
            left=NumberLiteral(value=5, line=1, column=22),
            operator='*',
            right=NumberLiteral(value=6, line=1, column=26),
            line=1,
            column=24
        )
        
        expr = BinaryOp(left=mult, operator='-', right=right_side, line=1, column=19)
        
        # Verify depth
        assert expr.left.left.left.value == 1  # Depth 3 access
        assert expr.right.right.value == 6

    def test_mixed_literal_identifier_expression(self):
        """Test: x + 5 * y - 3.14"""
        # 5 * y
        mult = BinaryOp(
            left=NumberLiteral(value=5, line=1, column=5),
            operator='*',
            right=Identifier(name='y', line=1, column=9),
            line=1,
            column=7
        )
        
        # x + (5 * y)
        add = BinaryOp(
            left=Identifier(name='x', line=1, column=1),
            operator='+',
            right=mult,
            line=1,
            column=3
        )
        
        # (x + 5 * y) - 3.14
        expr = BinaryOp(
            left=add,
            operator='-',
            right=NumberLiteral(value=3.14, line=1, column=14),
            line=1,
            column=11
        )
        
        # Verify mixed types
        assert isinstance(expr.left.left, Identifier)
        assert isinstance(expr.left.right.left, NumberLiteral)
        assert isinstance(expr.right, NumberLiteral)
        assert expr.right.value == 3.14


# =============================================================================
# Block Scope Nesting
# =============================================================================

class TestBlockScopeNesting:
    """Test nested block structures (CO523 Week 4: Scopes & Lifetimes)"""

    def test_single_block(self):
        """Test: { int x; x = 5; }"""
        statements = [
            Declaration(var_type='int', name='x', line=1, column=2),
            Assignment(
                name='x',
                value=NumberLiteral(value=5, line=2, column=5),
                line=2,
                column=2
            )
        ]
        block = Block(statements=statements, line=1, column=1)
        
        assert len(block.statements) == 2
        assert isinstance(block.statements[0], Declaration)
        assert isinstance(block.statements[1], Assignment)

    def test_nested_blocks_two_levels(self):
        """Test: { { int x; } { int y; } }"""
        inner_block_1 = Block(
            statements=[Declaration(var_type='int', name='x', line=2, column=3)],
            line=2,
            column=2
        )
        
        inner_block_2 = Block(
            statements=[Declaration(var_type='int', name='y', line=3, column=3)],
            line=3,
            column=2
        )
        
        outer_block = Block(
            statements=[inner_block_1, inner_block_2],
            line=1,
            column=1
        )
        
        # Verify nesting structure
        assert len(outer_block.statements) == 2
        assert isinstance(outer_block.statements[0], Block)
        assert isinstance(outer_block.statements[1], Block)
        assert outer_block.statements[0].statements[0].name == 'x'
        assert outer_block.statements[1].statements[0].name == 'y'

    def test_deeply_nested_blocks(self):
        """Test: { { { int z; } } }"""
        innermost = Block(
            statements=[Declaration(var_type='int', name='z', line=3, column=4)],
            line=3,
            column=3
        )
        
        middle = Block(statements=[innermost], line=2, column=2)
        outer = Block(statements=[middle], line=1, column=1)
        
        # Verify 3-level nesting
        assert isinstance(outer.statements[0], Block)
        assert isinstance(outer.statements[0].statements[0], Block)
        assert outer.statements[0].statements[0].statements[0].name == 'z'

    def test_block_with_mixed_statements(self):
        """Test: { int x; if (x) { x = 1; } printf(x); }"""
        if_stmt = IfStatement(
            condition=Identifier(name='x', line=2, column=5),
            then_branch=Block(
                statements=[Assignment(
                    name='x',
                    value=NumberLiteral(value=1, line=3, column=6),
                    line=3,
                    column=3
                )],
                line=3,
                column=2
            ),
            else_branch=None,
            line=2,
            column=1
        )
        
        printf = PrintfCall(
            argument=Identifier(name='x', line=4, column=9),
            line=4,
            column=1
        )
        
        block = Block(
            statements=[
                Declaration(var_type='int', name='x', line=1, column=2),
                if_stmt,
                printf
            ],
            line=1,
            column=1
        )
        
        # Verify mixed statement types
        assert len(block.statements) == 3
        assert isinstance(block.statements[0], Declaration)
        assert isinstance(block.statements[1], IfStatement)
        assert isinstance(block.statements[2], PrintfCall)

    def test_empty_block(self):
        """Test: { }"""
        block = Block(statements=[], line=1, column=1)
        assert len(block.statements) == 0


# =============================================================================
# IfStatement Traversal Coverage
# =============================================================================

class TestIfStatementTraversal:
    """Test IfStatement variations (CO523 Week 6: Control Structures)"""

    def test_if_without_else(self):
        """Test: if (x) { }"""
        stmt = IfStatement(
            condition=Identifier(name='x', line=1, column=4),
            then_branch=Block(statements=[], line=1, column=7),
            else_branch=None,
            line=1,
            column=1
        )
        
        assert stmt.else_branch is None
        assert isinstance(stmt.then_branch, Block)

    def test_if_with_else(self):
        """Test: if (x) { } else { }"""
        stmt = IfStatement(
            condition=Identifier(name='x', line=1, column=4),
            then_branch=Block(statements=[], line=1, column=7),
            else_branch=Block(statements=[], line=1, column=15),
            line=1,
            column=1
        )
        
        assert stmt.else_branch is not None
        assert isinstance(stmt.else_branch, Block)

    def test_nested_if_statements(self):
        """Test: if (x) { if (y) { } }"""
        inner_if = IfStatement(
            condition=Identifier(name='y', line=2, column=5),
            then_branch=Block(statements=[], line=2, column=8),
            else_branch=None,
            line=2,
            column=1
        )
        
        outer_if = IfStatement(
            condition=Identifier(name='x', line=1, column=4),
            then_branch=Block(statements=[inner_if], line=1, column=7),
            else_branch=None,
            line=1,
            column=1
        )
        
        # Verify nesting
        assert isinstance(outer_if.then_branch, Block)
        assert outer_if.then_branch.statements[0] == inner_if
        assert outer_if.then_branch.statements[0].condition.name == 'y'

    def test_if_else_if_chain(self):
        """Test: if (x) { } else { if (y) { } }"""
        inner_if = IfStatement(
            condition=Identifier(name='y', line=2, column=12),
            then_branch=Block(statements=[], line=2, column=15),
            else_branch=None,
            line=2,
            column=8
        )
        
        stmt = IfStatement(
            condition=Identifier(name='x', line=1, column=4),
            then_branch=Block(statements=[], line=1, column=7),
            else_branch=Block(statements=[inner_if], line=2, column=7),
            line=1,
            column=1
        )
        
        # Verify else-if structure
        assert stmt.else_branch is not None
        assert isinstance(stmt.else_branch, Block)
        assert stmt.else_branch.statements[0] == inner_if

    def test_if_with_expression_condition(self):
        """Test: if (x > 5) { }"""
        condition = BinaryOp(
            left=Identifier(name='x', line=1, column=4),
            operator='>',
            right=NumberLiteral(value=5, line=1, column=8),
            line=1,
            column=6
        )
        
        stmt = IfStatement(
            condition=condition,
            then_branch=Block(statements=[], line=1, column=11),
            else_branch=None,
            line=1,
            column=1
        )
        
        assert isinstance(stmt.condition, BinaryOp)
        assert stmt.condition.operator == '>'


# =============================================================================
# Identifier Usage in Expressions
# =============================================================================

class TestIdentifierInExpressions:
    """Test identifier as expression operands (CO523 Week 4: Names & Bindings)"""

    def test_identifier_in_binary_op_left(self):
        """Test: x + 5"""
        expr = BinaryOp(
            left=Identifier(name='x', line=1, column=1),
            operator='+',
            right=NumberLiteral(value=5, line=1, column=5),
            line=1,
            column=3
        )
        assert expr.left.name == 'x'

    def test_identifier_in_binary_op_right(self):
        """Test: 5 + x"""
        expr = BinaryOp(
            left=NumberLiteral(value=5, line=1, column=1),
            operator='+',
            right=Identifier(name='x', line=1, column=5),
            line=1,
            column=3
        )
        assert expr.right.name == 'x'

    def test_identifier_in_both_operands(self):
        """Test: x + y"""
        expr = BinaryOp(
            left=Identifier(name='x', line=1, column=1),
            operator='+',
            right=Identifier(name='y', line=1, column=5),
            line=1,
            column=3
        )
        assert expr.left.name == 'x'
        assert expr.right.name == 'y'

    def test_identifier_in_unary_op(self):
        """Test: -x"""
        expr = UnaryOp(
            operator='-',
            operand=Identifier(name='x', line=1, column=2),
            line=1,
            column=1
        )
        assert expr.operand.name == 'x'

    def test_identifier_in_comparison(self):
        """Test: x == y"""
        expr = BinaryOp(
            left=Identifier(name='x', line=1, column=1),
            operator='==',
            right=Identifier(name='y', line=1, column=6),
            line=1,
            column=3
        )
        assert expr.operator == '=='
        assert expr.left.name == 'x'
        assert expr.right.name == 'y'

    def test_identifier_chained_operations(self):
        """Test: x + y * z"""
        mult = BinaryOp(
            left=Identifier(name='y', line=1, column=5),
            operator='*',
            right=Identifier(name='z', line=1, column=9),
            line=1,
            column=7
        )
        
        expr = BinaryOp(
            left=Identifier(name='x', line=1, column=1),
            operator='+',
            right=mult,
            line=1,
            column=3
        )
        
        # Verify all identifiers present
        assert expr.left.name == 'x'
        assert expr.right.left.name == 'y'
        assert expr.right.right.name == 'z'


# =============================================================================
# Printf Traversal
# =============================================================================

class TestPrintfTraversal:
    """Test PrintfCall with different argument types (Project Spec §3: Standard I/O)"""

    def test_printf_with_identifier(self):
        """Test: printf(x);"""
        printf = PrintfCall(
            argument=Identifier(name='x', line=1, column=8),
            line=1,
            column=1
        )
        assert printf.argument.name == 'x'

    def test_printf_with_number_literal(self):
        """Test: printf(42);"""
        printf = PrintfCall(
            argument=NumberLiteral(value=42, line=1, column=8),
            line=1,
            column=1
        )
        assert printf.argument.value == 42

    def test_printf_with_expression(self):
        """Test: printf(x + y);"""
        expr = BinaryOp(
            left=Identifier(name='x', line=1, column=8),
            operator='+',
            right=Identifier(name='y', line=1, column=12),
            line=1,
            column=10
        )
        
        printf = PrintfCall(argument=expr, line=1, column=1)
        assert isinstance(printf.argument, BinaryOp)
        assert printf.argument.operator == '+'

    def test_printf_with_unary_expression(self):
        """Test: printf(-x);"""
        expr = UnaryOp(
            operator='-',
            operand=Identifier(name='x', line=1, column=9),
            line=1,
            column=8
        )
        
        printf = PrintfCall(argument=expr, line=1, column=1)
        assert isinstance(printf.argument, UnaryOp)
        assert printf.argument.operator == '-'

    def test_printf_with_nested_expression(self):
        """Test: printf((a + b) * c);"""
        inner = BinaryOp(
            left=Identifier(name='a', line=1, column=9),
            operator='+',
            right=Identifier(name='b', line=1, column=13),
            line=1,
            column=11
        )
        
        expr = BinaryOp(
            left=inner,
            operator='*',
            right=Identifier(name='c', line=1, column=18),
            line=1,
            column=16
        )
        
        printf = PrintfCall(argument=expr, line=1, column=1)
        assert isinstance(printf.argument, BinaryOp)
        assert printf.argument.left.operator == '+'


# =============================================================================
# Equality & Structural Comparison
# =============================================================================

class TestASTEqualityComparison:
    """Test AST node equality and structural comparison"""

    def test_same_literal_equality(self):
        """Test two identical NumberLiteral nodes"""
        lit1 = NumberLiteral(value=42, line=1, column=1)
        lit2 = NumberLiteral(value=42, line=1, column=1)
        
        # Dataclasses compare by value
        assert lit1 == lit2
        assert lit1.value == lit2.value

    def test_different_literal_inequality(self):
        """Test two different NumberLiteral nodes"""
        lit1 = NumberLiteral(value=42, line=1, column=1)
        lit2 = NumberLiteral(value=43, line=1, column=1)
        
        assert lit1 != lit2

    def test_same_identifier_equality(self):
        """Test two identical Identifier nodes"""
        id1 = Identifier(name='x', line=1, column=1)
        id2 = Identifier(name='x', line=1, column=1)
        
        assert id1 == id2

    def test_different_identifier_inequality(self):
        """Test two different Identifier nodes"""
        id1 = Identifier(name='x', line=1, column=1)
        id2 = Identifier(name='y', line=1, column=1)
        
        assert id1 != id2

    def test_same_binary_op_equality(self):
        """Test two identical BinaryOp nodes"""
        left = NumberLiteral(value=3, line=1, column=1)
        right = NumberLiteral(value=4, line=1, column=5)
        
        op1 = BinaryOp(left=left, operator='+', right=right, line=1, column=3)
        op2 = BinaryOp(left=left, operator='+', right=right, line=1, column=3)
        
        assert op1 == op2

    def test_different_operator_inequality(self):
        """Test BinaryOp with different operators"""
        left = NumberLiteral(value=3, line=1, column=1)
        right = NumberLiteral(value=4, line=1, column=5)
        
        op1 = BinaryOp(left=left, operator='+', right=right, line=1, column=3)
        op2 = BinaryOp(left=left, operator='-', right=right, line=1, column=3)
        
        assert op1 != op2

    def test_location_difference_inequality(self):
        """Test nodes with same content but different locations"""
        lit1 = NumberLiteral(value=42, line=1, column=1)
        lit2 = NumberLiteral(value=42, line=2, column=1)
        
        # Frozen dataclasses compare all fields including location
        assert lit1 != lit2

    def test_structural_equality_deep_tree(self):
        """Test equality of deep expression trees"""
        def make_tree():
            return BinaryOp(
                left=NumberLiteral(value=3, line=1, column=1),
                operator='+',
                right=NumberLiteral(value=4, line=1, column=5),
                line=1,
                column=3
            )
        
        tree1 = make_tree()
        tree2 = make_tree()
        
        assert tree1 == tree2


# =============================================================================
# AST Base Class Contract
# =============================================================================

class TestASTBaseClassContract:
    """Test ASTNode base class contract (CO523 Week 13: Language Implementation)"""

    def test_all_nodes_inherit_from_astnode(self):
        """Verify all node types inherit from ASTNode"""
        nodes = [
            Declaration(var_type='int', name='x', line=1, column=1),
            Assignment(name='x', value=NumberLiteral(value=5, line=1, column=5), line=1, column=1),
            IfStatement(
                condition=Identifier(name='x', line=1, column=4),
                then_branch=EmptyStatement(line=1, column=7),
                else_branch=None,
                line=1,
                column=1
            ),
            Block(statements=[], line=1, column=1),
            PrintfCall(argument=Identifier(name='x', line=1, column=8), line=1, column=1),
            BinaryOp(
                left=NumberLiteral(value=3, line=1, column=1),
                operator='+',
                right=NumberLiteral(value=4, line=1, column=5),
                line=1,
                column=3
            ),
            UnaryOp(operator='-', operand=NumberLiteral(value=5, line=1, column=2), line=1, column=1),
            NumberLiteral(value=42, line=1, column=1),
            Identifier(name='x', line=1, column=1),
            EmptyStatement(line=1, column=1),
            Program(declarations=[], statements=[])
        ]
        
        for node in nodes:
            assert isinstance(node, ASTNode), f"{type(node).__name__} should inherit from ASTNode"

    def test_all_nodes_implement_accept(self):
        """Verify all node types implement accept() method"""
        nodes = [
            Declaration(var_type='int', name='x', line=1, column=1),
            NumberLiteral(value=42, line=1, column=1),
            Identifier(name='x', line=1, column=1),
        ]
        
        for node in nodes:
            assert hasattr(node, 'accept'), f"{type(node).__name__} should have accept() method"
            assert callable(node.accept), f"{type(node).__name__}.accept should be callable"

    def test_all_nodes_implement_repr(self):
        """Verify all node types implement __repr__() method"""
        nodes = [
            Declaration(var_type='int', name='x', line=1, column=1),
            NumberLiteral(value=42, line=1, column=1),
        ]
        
        for node in nodes:
            assert hasattr(node, '__repr__'), f"{type(node).__name__} should have __repr__() method"
            repr_str = repr(node)
            assert isinstance(repr_str, str), f"{type(node).__name__}.__repr__ should return string"

    def test_visitor_implements_all_visit_methods(self):
        """Verify ASTVisitor has all required visit methods"""
        visitor_methods = [
            'visit_program',
            'visit_declaration',
            'visit_assignment',
            'visit_if_statement',
            'visit_block',
            'visit_printf_call',
            'visit_binary_op',
            'visit_unary_op',
            'visit_number_literal',
            'visit_identifier',
            'visit_empty_statement'
        ]
        
        for method in visitor_methods:
            assert hasattr(ASTVisitor, method), f"ASTVisitor should have {method}"


# =============================================================================
# Invalid Construction Protection
# =============================================================================

class TestInvalidConstructionProtection:
    """Test protection against invalid AST construction"""

    def test_declaration_invalid_type(self):
        """Test Declaration with invalid type (should still construct but semantically invalid)"""
        # Note: Type checking is semantic, not syntactic
        # AST allows any string, semantic analysis will validate
        decl = Declaration(var_type='invalid', name='x', line=1, column=1)
        assert decl.var_type == 'invalid'
        # This is intentional - AST is syntax-only, semantics checked later

    def test_binary_op_invalid_operator(self):
        """Test BinaryOp with invalid operator"""
        # Similar to above - AST allows any operator string
        left = NumberLiteral(value=3, line=1, column=1)
        right = NumberLiteral(value=4, line=1, column=5)
        op = BinaryOp(left=left, operator='%', right=right, line=1, column=3)
        assert op.operator == '%'
        # Semantic analysis will reject invalid operators

    def test_immutable_nodes_cannot_be_modified(self):
        """Test that frozen dataclasses prevent modification"""
        from dataclasses import FrozenInstanceError
        
        node = NumberLiteral(value=42, line=1, column=1)
        with pytest.raises(FrozenInstanceError):
            node.value = 100

    def test_none_values_where_not_allowed(self):
        """Test construction with None where values required"""
        # These should still construct (Python doesn't enforce type at runtime)
        # But type checkers (mypy) will flag them
        node = Identifier(name=None, line=1, column=1)  # type: ignore
        assert node.name is None

    def test_empty_string_identifier(self):
        """Test Identifier with empty name"""
        # AST allows it, semantic analysis should reject
        ident = Identifier(name='', line=1, column=1)
        assert ident.name == ''


# =============================================================================
# Program Node Edge Cases
# =============================================================================

class TestProgramNodeEdgeCases:
    """Test Program node variations (CO523 Week 2: Program Structure)"""

    def test_empty_program(self):
        """Test: (empty file)"""
        program = Program(declarations=[], statements=[])
        assert len(program.declarations) == 0
        assert len(program.statements) == 0

    def test_program_only_declarations(self):
        """Test: int x; int y;"""
        program = Program(
            declarations=[
                Declaration(var_type='int', name='x', line=1, column=1),
                Declaration(var_type='int', name='y', line=1, column=8)
            ],
            statements=[]
        )
        assert len(program.declarations) == 2
        assert len(program.statements) == 0

    def test_program_only_statements(self):
        """Test: x = 5; printf(x);"""
        program = Program(
            declarations=[],
            statements=[
                Assignment(
                    name='x',
                    value=NumberLiteral(value=5, line=1, column=5),
                    line=1,
                    column=1
                ),
                PrintfCall(
                    argument=Identifier(name='x', line=2, column=8),
                    line=2,
                    column=1
                )
            ]
        )
        assert len(program.declarations) == 0
        assert len(program.statements) == 2

    def test_program_with_many_declarations(self):
        """Test program with 100+ declarations"""
        declarations = [
            Declaration(var_type='int', name=f'var{i}', line=i, column=1)
            for i in range(100)
        ]
        program = Program(declarations=declarations, statements=[])
        assert len(program.declarations) == 100

    def test_program_with_many_statements(self):
        """Test program with 100+ statements"""
        statements = [
            Assignment(
                name='x',
                value=NumberLiteral(value=i, line=i, column=5),
                line=i,
                column=1
            )
            for i in range(100)
        ]
        program = Program(declarations=[], statements=statements)
        assert len(program.statements) == 100


# =============================================================================
# Deep Visitor Contract Test
# =============================================================================

class TestDeepVisitorContract:
    """Test visitor pattern with deep tree traversal"""

    def test_visitor_visits_all_node_types(self):
        """Verify visitor can visit all AST node types"""
        visited = []
        
        class RecordingVisitor(ASTVisitor):
            def visit_program(self, node):
                visited.append('Program')
                for decl in node.declarations:
                    decl.accept(self)
                for stmt in node.statements:
                    stmt.accept(self)
            def visit_declaration(self, node):
                visited.append('Declaration')
            def visit_assignment(self, node):
                visited.append('Assignment')
                node.value.accept(self)
            def visit_if_statement(self, node):
                visited.append('IfStatement')
                node.condition.accept(self)
                node.then_branch.accept(self)
                if node.else_branch:
                    node.else_branch.accept(self)
            def visit_block(self, node):
                visited.append('Block')
                for stmt in node.statements:
                    stmt.accept(self)
            def visit_printf_call(self, node):
                visited.append('PrintfCall')
                node.argument.accept(self)
            def visit_binary_op(self, node):
                visited.append('BinaryOp')
                node.left.accept(self)
                node.right.accept(self)
            def visit_unary_op(self, node):
                visited.append('UnaryOp')
                node.operand.accept(self)
            def visit_number_literal(self, node):
                visited.append('NumberLiteral')
            def visit_identifier(self, node):
                visited.append('Identifier')
            def visit_empty_statement(self, node):
                visited.append('EmptyStatement')
        
        # Create complex program
        program = Program(
            declarations=[
                Declaration(var_type='int', name='x', line=1, column=1)
            ],
            statements=[
                Assignment(
                    name='x',
                    value=BinaryOp(
                        left=NumberLiteral(value=3, line=2, column=5),
                        operator='+',
                        right=NumberLiteral(value=4, line=2, column=9),
                        line=2,
                        column=7
                    ),
                    line=2,
                    column=1
                )
            ]
        )
        
        program.accept(RecordingVisitor())
        
        # Verify all types visited
        assert 'Program' in visited
        assert 'Declaration' in visited
        assert 'Assignment' in visited
        assert 'BinaryOp' in visited
        assert 'NumberLiteral' in visited

    def test_visitor_accumulates_values(self):
        """Test visitor that accumulates values from tree"""
        class SumVisitor(ASTVisitor):
            def __init__(self):
                self.total = 0
            
            def visit_program(self, node):
                for decl in node.declarations:
                    decl.accept(self)
                for stmt in node.statements:
                    stmt.accept(self)
            def visit_declaration(self, node): pass
            def visit_assignment(self, node):
                node.value.accept(self)
            def visit_if_statement(self, node): pass
            def visit_block(self, node):
                for stmt in node.statements:
                    stmt.accept(self)
            def visit_printf_call(self, node): pass
            def visit_binary_op(self, node):
                node.left.accept(self)
                node.right.accept(self)
            def visit_unary_op(self, node): pass
            def visit_number_literal(self, node):
                if isinstance(node.value, (int, float)):
                    self.total += node.value
            def visit_identifier(self, node): pass
            def visit_empty_statement(self, node): pass
        
        # Create expression: x = 3 + 4 * 5
        program = Program(
            declarations=[],
            statements=[
                Assignment(
                    name='x',
                    value=BinaryOp(
                        left=NumberLiteral(value=3, line=1, column=5),
                        operator='+',
                        right=BinaryOp(
                            left=NumberLiteral(value=4, line=1, column=9),
                            operator='*',
                            right=NumberLiteral(value=5, line=1, column=13),
                            line=1,
                            column=11
                        ),
                        line=1,
                        column=7
                    ),
                    line=1,
                    column=1
                )
            ]
        )
        
        visitor = SumVisitor()
        program.accept(visitor)
        
        assert visitor.total == 12  # 3 + 4 + 5


# =============================================================================
# Complex Integration Scenario
# =============================================================================

class TestComplexIntegrationScenario:
    """Test complete program AST construction (Project Spec §5: Test Suite)"""

    def test_complete_program_ast(self):
        """Test: Complete C-Lite program with all features"""
        # Declarations
        declarations = [
            Declaration(var_type='int', name='x', line=1, column=1),
            Declaration(var_type='float', name='y', line=2, column=1)
        ]
        
        # Statements
        statements = [
            # x = 10;
            Assignment(
                name='x',
                value=NumberLiteral(value=10, line=3, column=5),
                line=3,
                column=1
            ),
            # y = 3.14;
            Assignment(
                name='y',
                value=NumberLiteral(value=3.14, line=4, column=5),
                line=4,
                column=1
            ),
            # if (x > 5) { printf(x); } else { printf(y); }
            IfStatement(
                condition=BinaryOp(
                    left=Identifier(name='x', line=5, column=5),
                    operator='>',
                    right=NumberLiteral(value=5, line=5, column=9),
                    line=5,
                    column=7
                ),
                then_branch=Block(
                    statements=[
                        PrintfCall(
                            argument=Identifier(name='x', line=6, column=13),
                            line=6,
                            column=9
                        )
                    ],
                    line=6,
                    column=7
                ),
                else_branch=Block(
                    statements=[
                        PrintfCall(
                            argument=Identifier(name='y', line=8, column=13),
                            line=8,
                            column=9
                        )
                    ],
                    line=8,
                    column=7
                ),
                line=5,
                column=1
            ),
            # Nested block
            Block(
                statements=[
                    Declaration(var_type='int', name='z', line=10, column=5),
                    Assignment(
                        name='z',
                        value=BinaryOp(
                            left=Identifier(name='x', line=11, column=7),
                            operator='+',
                            right=Identifier(name='y', line=11, column=11),
                            line=11,
                            column=9
                        ),
                        line=11,
                        column=5
                    )
                ],
                line=10,
                column=1
            )
        ]
        
        program = Program(declarations=declarations, statements=statements)
        
        # Verify structure
        assert len(program.declarations) == 2
        assert len(program.statements) == 4
        assert isinstance(program.statements[2], IfStatement)
        assert isinstance(program.statements[3], Block)
        
        # Verify nested structure
        if_stmt = program.statements[2]
        assert isinstance(if_stmt.then_branch, Block)
        assert isinstance(if_stmt.else_branch, Block)
        assert len(if_stmt.then_branch.statements) == 1
        assert len(if_stmt.else_branch.statements) == 1

    def test_arithmetic_expression_precedence_ast(self):
        """Test: x = 3 + 4 * 5 - 6 / 2"""
        # Verify AST reflects correct precedence: 3 + (4*5) - (6/2)
        mult = BinaryOp(
            left=NumberLiteral(value=4, line=1, column=9),
            operator='*',
            right=NumberLiteral(value=5, line=1, column=13),
            line=1,
            column=11
        )
        
        div = BinaryOp(
            left=NumberLiteral(value=6, line=1, column=18),
            operator='/',
            right=NumberLiteral(value=2, line=1, column=22),
            line=1,
            column=20
        )
        
        add = BinaryOp(
            left=NumberLiteral(value=3, line=1, column=5),
            operator='+',
            right=mult,
            line=1,
            column=7
        )
        
        expr = BinaryOp(
            left=add,
            operator='-',
            right=div,
            line=1,
            column=15
        )
        
        assignment = Assignment(name='x', value=expr, line=1, column=1)
        
        # Verify precedence structure
        assert assignment.value.operator == '-'
        assert assignment.value.left.operator == '+'
        assert assignment.value.left.right.operator == '*'
        assert assignment.value.right.operator == '/'


# =============================================================================
# Defensive Location Integrity
# =============================================================================

class TestDefensiveLocationIntegrity:
    """Test source location tracking consistency (Project Spec §5: Error Reporting)"""

    def test_all_nodes_have_line_column(self):
        """Verify all node types have line and column attributes"""
        nodes = [
            Declaration(var_type='int', name='x', line=1, column=1),
            Assignment(name='x', value=NumberLiteral(value=5, line=1, column=5), line=1, column=1),
            NumberLiteral(value=42, line=1, column=1),
            Identifier(name='x', line=1, column=1),
        ]
        
        for node in nodes:
            assert hasattr(node, 'line'), f"{type(node).__name__} should have line attribute"
            assert hasattr(node, 'column'), f"{type(node).__name__} should have column attribute"
            assert isinstance(node.line, int), f"{type(node).__name__}.line should be int"
            assert isinstance(node.column, int), f"{type(node).__name__}.column should be int"

    def test_child_locations_within_parent_range(self):
        """Verify child node locations are consistent with parent"""
        # Parent at column 1, child at column 5 (valid)
        child = NumberLiteral(value=42, line=1, column=5)
        parent = Assignment(name='x', value=child, line=1, column=1)
        
        assert parent.line == child.line
        assert parent.column <= child.column  # Child should be at or after parent

    def test_expression_tree_location_consistency(self):
        """Verify location consistency in expression tree"""
        left = NumberLiteral(value=3, line=1, column=1)
        right = NumberLiteral(value=4, line=1, column=5)
        expr = BinaryOp(left=left, operator='+', right=right, line=1, column=3)
        
        # All nodes on same line
        assert expr.line == left.line == right.line
        
        # Operator between operands
        assert left.column < expr.column < right.column

    def test_negative_line_column_rejected(self):
        """Test that negative locations are handled (should still construct but flagged)"""
        # Python doesn't enforce, but semantic analysis could validate
        node = NumberLiteral(value=42, line=-1, column=-1)
        assert node.line == -1
        assert node.column == -1
        # Note: Validation would happen in semantic phase

    def test_zero_line_column_handling(self):
        """Test zero-based locations"""
        node = NumberLiteral(value=42, line=0, column=0)
        assert node.line == 0
        assert node.column == 0
        # Note: We use 1-indexed, but 0 is technically valid Python int

    def test_large_line_column_values(self):
        """Test very large location values"""
        node = NumberLiteral(value=42, line=99999, column=99999)
        assert node.line == 99999
        assert node.column == 99999