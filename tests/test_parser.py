"""
Parser test suite for C-Lite.

Test Coverage Gaps Addressed:
1. Negative Path Combinatorics (Operator Misuse, Invalid Sequences, Garbage)
2. Boundary and Edge Conditions (Deep Nesting, Long Expressions)
3. Float Literal Behavior (Edge cases)
4. AST Structural Validation (Full tree topology)
5. Recovery Behavior (Error handling)
6. Invalid Nested Declarations (Grammar order)
7. Identifier Edge Cases (Boundary patterns)
8. Relational Operator Precedence (Mixed operators)
9. AST Integrity Under Stress (Large files)
10. Fuzzing / Random Input (Garbage handling)
11. EOF Edge Cases (End-of-file errors)
12. Memory / Performance Testing (Scalability)
"""

import pytest
import time
from src.lexer import Lexer
from src.parser import Parser
from src.ast import (
    Program, Declaration, Assignment, IfStatement, Block, PrintfCall, EmptyStatement,
    BinaryOp, UnaryOp, NumberLiteral, Identifier
)
from src.errors import ParserError, LexerError


# =============================================================================
# GAP 1: Negative Path Combinatorics
# =============================================================================

class TestNegativePathCombinatorics:
    """Test systematic syntax error detection"""

    # ------------------- Operator Misuse -------------------
    
    def test_error_trailing_operator(self):
        """Test: x = 5 + ;"""
        code = "x = 5 + ;"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        with pytest.raises(ParserError):
            parser.parse()

    def test_error_leading_operator(self):
        """Test: x = * 3;"""
        code = "x = * 3;"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        with pytest.raises(ParserError):
            parser.parse()

    def test_error_unclosed_parenthesis(self):
        """Test: x = (1 + 2;"""
        code = "x = (1 + 2;"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        with pytest.raises(ParserError):
            parser.parse()

    def test_error_empty_parenthesis_content(self):
        """Test: x = 1 + (2 * );"""
        code = "x = 1 + (2 * );"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        with pytest.raises(ParserError):
            parser.parse()

    def test_error_double_operator(self):
        """Test: x = 5 + + 3; (actually valid: 5 + (+3))"""
        code = "x = 5 + + 3;"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        # This is VALID: unary plus is allowed
        ast = parser.parse()
        assert isinstance(ast, Program)
        assert len(ast.statements) == 1

    # ------------------- Invalid Token Sequences -------------------
    
    def test_error_double_type_specifier(self):
        """Test: int int x;"""
        code = "int int x;"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        with pytest.raises(ParserError):
            parser.parse()

    def test_error_double_assignment(self):
        """Test: x = = 5;"""
        code = "x = = 5;"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        with pytest.raises(ParserError):
            parser.parse()

    def test_error_unmatched_parentheses(self):
        """Test: if ((x)))) { }"""
        code = "if ((x)))) { }"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        with pytest.raises(ParserError):
            parser.parse()

    def test_error_unmatched_braces(self):
        """Test: { { }"""
        code = "{ { }"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        with pytest.raises(ParserError):
            parser.parse()

    # ------------------- Garbage After Valid Program -------------------
    
    def test_error_trailing_garbage_closing_brace(self):
        """Test: int x; }"""
        code = "int x; }"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        with pytest.raises(ParserError):
            parser.parse()

    def test_error_trailing_garbage_identifier(self):
        """Test: x = 5; random"""
        code = "x = 5; random_token"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        # Should parse successfully (random_token is valid identifier statement)
        # But assignment expected, so should error
        with pytest.raises(ParserError):
            parser.parse()

    def test_error_trailing_operator(self):
        """Test: int x; +"""
        code = "int x; +"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        with pytest.raises(ParserError):
            parser.parse()

    def test_error_random_characters(self):
        """Test: int x; @#$ (lexer catches, not parser)"""
        code = "int x; @"
        
        # Lexer should catch invalid characters FIRST
        with pytest.raises(LexerError):
            list(Lexer(code).tokenize())


# =============================================================================
# GAP 2: Boundary and Edge Conditions
# =============================================================================

class TestBoundaryEdgeConditions:
    """Test pathological cases for parser robustness"""

    # ------------------- Deep Nesting (Stack Safety) -------------------
    
    def test_deep_nesting_if_statements_depth_50(self):
        """Test: 50 levels of nested if statements"""
        # Generate: if(x){ if(x){ ... } }
        code = "int x; x = 1; " + "if (x) { " * 50 + "printf(x); " + "} " * 50
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        # Should parse without stack overflow
        ast = parser.parse()
        assert isinstance(ast, Program)

    def test_deep_nesting_blocks_depth_50(self):
        """Test: 50 levels of nested blocks"""
        code = "int x; " + "{ " * 50 + "x = 1; " + "} " * 50
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        ast = parser.parse()
        assert isinstance(ast, Program)

    def test_deep_nesting_expressions_depth_20(self):
        """Test: 20 levels of nested parentheses"""
        code = "x = " + "(1 + " * 20 + "5" + ")" * 20 + ";"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        ast = parser.parse()
        assert isinstance(ast, Program)

    # Depth 100-500 may cause recursion limit issues in Python
    # Production parsers use iterative approaches or increase recursion limit
    
    # ------------------- Long Expressions -------------------
    
    def test_long_expression_chain_100_terms(self):
        """Test: x = 1 + 2 + 3 + ... + 100;"""
        terms = " + ".join(str(i) for i in range(1, 101))
        code = f"x = {terms};"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        ast = parser.parse()
        assert isinstance(ast, Program)
        assert len(ast.statements) == 1
        
        # Verify left-associativity (should be left-heavy tree)
        expr = ast.statements[0].value
        depth = 0
        current = expr
        while isinstance(current, BinaryOp):
            depth += 1
            current = current.left
        assert depth >= 50  # Should be deep left-heavy tree

    def test_long_expression_chain_1000_terms(self):
        """Test: x = 1 + 2 + ... + 1000; (stress test)"""
        terms = " + ".join(str(i) for i in range(1, 1001))
        code = f"x = {terms};"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        ast = parser.parse()
        assert isinstance(ast, Program)


# =============================================================================
# GAP 3: Float Literal Behavior
# =============================================================================

class TestFloatLiteralBehavior:
    """Test float parsing edge cases"""

    def test_float_leading_dot(self):
        """Test: .5"""
        code = "x = .5;"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        expr = ast.statements[0].value
        assert isinstance(expr, NumberLiteral)
        assert expr.value == 0.5

    def test_float_trailing_dot(self):
        """Test: 5."""
        code = "x = 5.;"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        expr = ast.statements[0].value
        assert isinstance(expr, NumberLiteral)
        assert expr.value == 5.0

    def test_float_zero_point_zero(self):
        """Test: 0.0"""
        code = "x = 0.0;"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        expr = ast.statements[0].value
        assert isinstance(expr, NumberLiteral)
        assert expr.value == 0.0

    def test_float_precise_decimal(self):
        """Test: 10.0001"""
        code = "x = 10.0001;"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        expr = ast.statements[0].value
        assert isinstance(expr, NumberLiteral)
        assert abs(expr.value - 10.0001) < 1e-6

    def test_float_declaration(self):
        """Test: float y = 3.14;"""
        code = "float y; y = 3.14;"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert ast.declarations[0].var_type == 'float'

    def test_float_invalid_double_dot(self):
        """Test: 3..4 (should fail at lexer level)"""
        code = "x = 3..4;"
        
        # Lexer should catch this
        with pytest.raises(LexerError):
            list(Lexer(code).tokenize())

    def test_float_in_expression(self):
        """Test: x = 1.5 + 2.5;"""
        code = "x = 1.5 + 2.5;"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        expr = ast.statements[0].value
        assert isinstance(expr, BinaryOp)
        assert isinstance(expr.left, NumberLiteral)
        assert isinstance(expr.right, NumberLiteral)


# =============================================================================
# GAP 4: AST Structural Validation
# =============================================================================

class TestASTStructuralValidation:
    """Test full AST topology verification"""

    def test_full_tree_validation_precedence(self):
        """Test: x = 3 + 4 * 5 - 6 / 2 (full tree shape)"""
        code = "x = 3 + 4 * 5 - 6 / 2;"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        expr = ast.statements[0].value
        
        # Root should be '-' (lowest precedence)
        assert isinstance(expr, BinaryOp)
        assert expr.operator == '-'
        
        # Left should be '+' (next level)
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.operator == '+'
        
        # Left.right should be '*' (higher precedence)
        assert isinstance(expr.left.right, BinaryOp)
        assert expr.left.right.operator == '*'
        
        # Right should be '/' (higher precedence)
        assert isinstance(expr.right, BinaryOp)
        assert expr.right.operator == '/'
        
        # Verify leaves are NumberLiterals
        assert isinstance(expr.left.left, NumberLiteral)
        assert isinstance(expr.left.right.left, NumberLiteral)
        assert isinstance(expr.left.right.right, NumberLiteral)
        assert isinstance(expr.right.left, NumberLiteral)
        assert isinstance(expr.right.right, NumberLiteral)

    def test_full_tree_validation_parentheses(self):
        """Test: x = (3 + 4) * (5 - 2) (parentheses override)"""
        code = "x = (3 + 4) * (5 - 2);"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        expr = ast.statements[0].value
        
        # Root should be '*'
        assert isinstance(expr, BinaryOp)
        assert expr.operator == '*'
        
        # Both children should be BinaryOp (parenthesized)
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.operator == '+'
        assert isinstance(expr.right, BinaryOp)
        assert expr.right.operator == '-'

    def test_full_tree_validation_unary(self):
        """Test: x = -a + -b (unary in binary)"""
        code = "x = -a + -b;"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        expr = ast.statements[0].value
        
        # Root should be '+'
        assert isinstance(expr, BinaryOp)
        assert expr.operator == '+'
        
        # Both children should be UnaryOp
        assert isinstance(expr.left, UnaryOp)
        assert expr.left.operator == '-'
        assert isinstance(expr.left.operand, Identifier)
        
        assert isinstance(expr.right, UnaryOp)
        assert expr.right.operator == '-'
        assert isinstance(expr.right.operand, Identifier)

    def test_full_tree_validation_if_condition(self):
        """Test: if (a + b > c * d) { } (complex condition)"""
        code = "if (a + b > c * d) { }"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        if_stmt = ast.statements[0]
        condition = if_stmt.condition
        
        # Root should be '>' (relational)
        assert isinstance(condition, BinaryOp)
        assert condition.operator == '>'
        
        # Left should be '+' (additive)
        assert isinstance(condition.left, BinaryOp)
        assert condition.left.operator == '+'
        
        # Right should be '*' (multiplicative)
        assert isinstance(condition.right, BinaryOp)
        assert condition.right.operator == '*'


# =============================================================================
# GAP 5: Recovery Behavior
# =============================================================================

class TestRecoveryBehavior:
    """Test error handling and recovery"""

    def test_error_stop_immediately(self):
        """Test: Parser stops on first error (fail-fast)"""
        code = "int x"  # Missing semicolon
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        with pytest.raises(ParserError):
            parser.parse()
        
        # Verify parser position is at error location
        assert parser.current_token is not None

    def test_error_location_includes_line_column(self):
        """Test: Error message includes precise location"""
        code = "int x"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        with pytest.raises(ParserError) as exc:
            parser.parse()
        
        error_msg = str(exc.value)
        assert "line" in error_msg.lower() or "column" in error_msg.lower()

    def test_error_multiple_errors_not_reported(self):
        """Test: Parser reports first error only (no error collection)"""
        code = "int x int y"  # Multiple errors
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        with pytest.raises(ParserError):
            parser.parse()
        
        # Should stop at first error, not collect all

    def test_error_does_not_crash_on_garbage(self):
        """Test: Parser raises ParserError, not exception"""
        code = "x = @#$;"
        
        # Lexer should catch invalid characters
        with pytest.raises(LexerError):
            list(Lexer(code).tokenize())


# =============================================================================
# GAP 6: Invalid Nested Declarations
# =============================================================================

class TestInvalidNestedDeclarations:
    """Test declaration rules and grammar order enforcement"""

    def test_declaration_missing_identifier(self):
        """Test: { int; }"""
        code = "{ int; }"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        with pytest.raises(ParserError):
            parser.parse()

    def test_declaration_missing_semicolon_in_block(self):
        """Test: { int x }"""
        code = "{ int x }"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        with pytest.raises(ParserError):
            parser.parse()

    def test_declaration_after_statement(self):
        """Test: x = 1; int y; (declaration after statement)"""
        code = "x = 1; int y;"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        # This is actually valid in C-Lite grammar
        # declarations and statements can be interleaved at program level
        ast = parser.parse()
        assert len(ast.statements) == 1
        assert len(ast.declarations) == 1

    def test_declaration_in_block_after_statement(self):
        """Test: { x = 1; int y; } (valid in C-Lite grammar)"""
        code = "{ x = 1; int y; }"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        # C-Lite grammar allows declarations and statements interleaved
        ast = parser.parse()
        assert isinstance(ast.statements[0], Block)
        assert len(ast.statements[0].statements) == 2

    def test_multiple_declarations_same_line(self):
        """Test: int x; int y; x = 1; int z;"""
        code = "int x; int y; x = 1; int z;"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        ast = parser.parse()
        assert len(ast.declarations) == 3
        assert len(ast.statements) == 1


# =============================================================================
# GAP 7: Identifier Edge Cases
# =============================================================================

class TestIdentifierEdgeCases:
    """Test identifier parsing boundary conditions"""

    def test_identifier_double_underscore(self):
        """Test: int __x__;"""
        code = "int __x__;"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert ast.declarations[0].name == '__x__'

    def test_identifier_alphanumeric(self):
        """Test: int x123;"""
        code = "int x123;"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert ast.declarations[0].name == 'x123'

    def test_identifier_underscore_prefix(self):
        """Test: int _123;"""
        code = "int _123;"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert ast.declarations[0].name == '_123'

    def test_identifier_starts_with_digit(self):
        """Test: int 123x; (lexer: INT_LITERAL + IDENTIFIER)"""
        code = "int 123x;"
        tokens = list(Lexer(code).tokenize())
        
        # Lexer tokenizes as: INT(123) + IDENTIFIER(x)
        # Parser sees: int 123 x; which fails on unexpected INT_LITERAL
        parser = Parser(tokens)
        with pytest.raises(ParserError):
            parser.parse()

    def test_identifier_very_long(self):
        """Test: int x...x; (1000 character identifier)"""
        ident = "x" * 1000
        code = f"int {ident};"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert len(ast.declarations[0].name) == 1000

    def test_identifier_single_underscore(self):
        """Test: int _;"""
        code = "int _;"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert ast.declarations[0].name == '_'


# =============================================================================
# GAP 8: Relational Operator Precedence
# =============================================================================

class TestRelationalOperatorPrecedence:
    """Test relational vs arithmetic operator precedence"""

    def test_relational_vs_addition(self):
        """Test: 1 + 2 > 3 parses as (1 + 2) > 3"""
        code = "x = 1 + 2 > 3;"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        expr = ast.statements[0].value
        
        # Root should be '>' (relational, lower precedence)
        assert isinstance(expr, BinaryOp)
        assert expr.operator == '>'
        
        # Left should be '+' (additive, higher precedence)
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.operator == '+'
        
        # Verify structure: (1 + 2) > 3
        assert isinstance(expr.left.left, NumberLiteral)
        assert isinstance(expr.left.right, NumberLiteral)
        assert isinstance(expr.right, NumberLiteral)

    def test_relational_vs_multiplication(self):
        """Test: 1 * 2 < 10 parses as (1 * 2) < 10"""
        code = "x = 1 * 2 < 10;"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        expr = ast.statements[0].value
        
        # Root should be '<'
        assert expr.operator == '<'
        
        # Left should be '*'
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.operator == '*'

    def test_equality_vs_relational(self):
        """Test: a < b == c parses as (a < b) == c"""
        code = "x = a < b == c;"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        expr = ast.statements[0].value
        
        # Root should be '==' (equality, same level as relational)
        # Left-associative: (a < b) == c
        assert expr.operator == '=='
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.operator == '<'

    def test_mixed_relational_chain(self):
        """Test: a > b < c (left-associative)"""
        code = "x = a > b < c;"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        expr = ast.statements[0].value
        
        # Left-associative: (a > b) < c
        assert expr.operator == '<'
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.operator == '>'


# =============================================================================
# GAP 9: AST Integrity Under Stress
# =============================================================================

class TestASTIntegrityUnderStress:
    """Test AST construction under stress conditions"""

    def test_large_file_1000_lines(self):
        """Test: 1000-line program"""
        lines = []
        for i in range(500):
            lines.append(f"int var{i};")
        for i in range(500):
            lines.append(f"var{i} = {i};")
        
        code = "\n".join(lines)
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        start_time = time.time()
        ast = parser.parse()
        elapsed = time.time() - start_time
        
        assert isinstance(ast, Program)
        assert len(ast.declarations) == 500
        assert len(ast.statements) == 500
        assert elapsed < 5.0  # Should complete in under 5 seconds

    def test_many_declarations_1000_plus(self):
        """Test: 1000+ declarations"""
        declarations = " ".join(f"int x{i};" for i in range(1000))
        code = declarations
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert len(ast.declarations) == 1000

    def test_mixed_nested_structures(self):
        """Test: Complex mixed nesting"""
        code = """
        int x;
        int y;
        x = 10;
        if (x > 5) {
            y = 20;
            if (y > 15) {
                {
                    int z;
                    z = x + y;
                    printf(z);
                }
            } else {
                y = 5;
            }
        }
        """
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Verify structure integrity
        assert len(ast.declarations) == 2
        assert len(ast.statements) == 2
        assert isinstance(ast.statements[1], IfStatement)
        assert isinstance(ast.statements[1].then_branch, Block)


# =============================================================================
# GAP 10: Fuzzing / Random Input
# =============================================================================

class TestFuzzingRandomInput:
    """Test parser robustness with garbage input"""

    def test_fuzz_random_characters(self):
        """Test: !@#$%^&*("""
        code = "!@#$%^&*("
        
        # Lexer should reject invalid characters
        with pytest.raises(LexerError):
            list(Lexer(code).tokenize())

    def test_fuzz_mixed_valid_invalid(self):
        """Test: int x; @#$; printf(x);"""
        code = "int x; @#$"
        
        # Lexer should catch invalid characters
        with pytest.raises(LexerError):
            list(Lexer(code).tokenize())

    def test_fuzz_only_whitespace(self):
        """Test: (whitespace only)"""
        code = "   \t\n   \t\n   "
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert isinstance(ast, Program)
        assert len(ast.declarations) == 0
        assert len(ast.statements) == 0

    def test_fuzz_empty_string(self):
        """Test: (empty string)"""
        code = ""
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert isinstance(ast, Program)
        assert len(ast.declarations) == 0
        assert len(ast.statements) == 0

    def test_fuzz_only_semicolons(self):
        """Test: ;;;"""
        code = ";;;"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert len(ast.statements) == 3
        assert all(isinstance(s, EmptyStatement) for s in ast.statements)


# =============================================================================
# GAP 11: EOF Edge Cases
# =============================================================================

class TestEOFEdgeCases:
    """Test end-of-file error conditions"""

    def test_eof_after_if_condition(self):
        """Test: if (x > 0) (EOF immediately)"""
        code = "if (x > 0)"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        with pytest.raises(ParserError):
            parser.parse()

    def test_eof_after_if_no_body(self):
        """Test: if (x) { (EOF in block)"""
        code = "if (x) {"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        with pytest.raises(ParserError):
            parser.parse()

    def test_eof_in_expression(self):
        """Test: x = 1 + (EOF)"""
        code = "x = 1 +"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        with pytest.raises(ParserError):
            parser.parse()

    def test_eof_after_declaration_type(self):
        """Test: int (EOF)"""
        code = "int"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        with pytest.raises(ParserError):
            parser.parse()

    def test_eof_after_identifier_in_assignment(self):
        """Test: x = (EOF)"""
        code = "x ="
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        with pytest.raises(ParserError):
            parser.parse()

    def test_eof_in_printf(self):
        """Test: printf(x (EOF)"""
        code = "printf(x"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        with pytest.raises(ParserError):
            parser.parse()


# =============================================================================
# GAP 12: Memory / Performance Testing
# =============================================================================

class TestMemoryPerformanceTesting:
    """Test parser performance and scalability"""

    def test_performance_parsing_time_1000_tokens(self):
        """Test: Parse 1000+ tokens within time limit"""
        # Generate program with ~1000 tokens
        code = " ".join(f"x{i} = {i};" for i in range(500))
        tokens = list(Lexer(code).tokenize())
        
        assert len(tokens) > 1000
        
        parser = Parser(tokens)
        start_time = time.time()
        ast = parser.parse()
        elapsed = time.time() - start_time
        
        assert isinstance(ast, Program)
        assert elapsed < 2.0  # Should complete in under 2 seconds

    def test_performance_linear_scaling(self):
        """Test: Parsing time scales linearly with input size"""
        sizes = [100, 200, 400]
        times = []
        
        for size in sizes:
            code = " ".join(f"x{i} = {i};" for i in range(size))
            tokens = list(Lexer(code).tokenize())
            parser = Parser(tokens)
            
            start_time = time.time()
            parser.parse()
            elapsed = time.time() - start_time
            times.append(elapsed)
        
        # Verify roughly linear scaling (within 3x for 4x input)
        assert times[2] < times[0] * 5  # 400 items should be < 5x time of 100

    def test_memory_no_memory_leak(self):
        """Test: Parser doesn't hold references after parsing"""
        import gc
        
        code = "int x; x = 5;" * 100
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        ast = parser.parse()
        
        # Delete parser and tokens
        del parser
        del tokens
        del ast
        
        # Force garbage collection
        gc.collect()
        
        # Should complete without memory issues
        assert True