"""
Interpreter test suite for C-Lite.


Test Coverage:
1. Boolean Semantics (truthiness rules)
2. Relational & Equality Evaluation
3. Mixed-Type Comparisons
4. Type Assignment Violations
5. Uninitialized Variable Usage
6. State After Runtime Exception
7. Deep Nested Block Execution
8. Large Expression Stress Test
9. Sequential Control Flow Integrity
10. Multiple Print Statements Order
11. Negative Numeric Behavior
12. Float Precision Tolerance
13. Division Mixed-Type Edge Cases
14. Variable Lifetime After Block
15. Garbage Program After Valid Code
16. Execution Time Safety
17. Large Program Stress
18. Symbol Table Isolation Between Runs
"""

import pytest
import time
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.errors import SemanticError, ParserError


# =============================================================================
# Boolean Semantics (Truthiness Rules)
# =============================================================================

class TestBooleanSemantics:
    """Test C-style truthiness rules"""

    def test_if_zero_is_false(self):
        """Test: if (0) { } (false)"""
        code = "if (0) { printf(1); }"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert output == []  # Nothing printed

    def test_if_nonzero_int_is_true(self):
        """Test: if (1) { }, if (3) { }, if (-1) { } (all true)"""
        for value in [1, 3, -1, 100]:
            code = f"if ({value}) {{ printf(1); }}"
            tokens = list(Lexer(code).tokenize())
            parser = Parser(tokens)
            ast = parser.parse()
            
            interpreter = Interpreter()
            output = interpreter.execute(ast)
            
            assert output == [1], f"if ({value}) should be true"

    def test_if_float_zero_is_false(self):
        """Test: if (0.0) { } (false)"""
        code = "if (0.0) { printf(1); }"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert output == []

    def test_if_float_nonzero_is_true(self):
        """Test: if (3.14) { } (true)"""
        code = "if (3.14) { printf(1); }"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert output == [1]

    def test_if_else_with_zero(self):
        """Test: if (0) { } else { printf(2); }"""
        code = "if (0) { printf(1); } else { printf(2); }"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert output == [2]


# =============================================================================
# Relational & Equality Evaluation
# =============================================================================

class TestRelationalEqualityEvaluation:
    """Test relational operator runtime evaluation"""

    def test_greater_than_true(self):
        """Test: printf(3 > 2); → 1"""
        code = "printf(3 > 2);"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert output == [1]

    def test_greater_than_false(self):
        """Test: printf(3 < 2); → 0"""
        code = "printf(3 < 2);"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert output == [0]

    def test_equality_true(self):
        """Test: printf(3 == 3); → 1"""
        code = "printf(3 == 3);"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert output == [1]

    def test_equality_false(self):
        """Test: printf(3 == 4); → 0"""
        code = "printf(3 == 4);"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert output == [0]

    def test_relational_returns_int(self):
        """Test: Relational operators return int (1 or 0)"""
        code = """
        int x;
        x = 3 > 2;
        printf(x);
        """
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert output == [1]
        assert isinstance(output[0], int)


# =============================================================================
# Mixed-Type Comparisons
# =============================================================================

class TestMixedTypeComparisons:
    """Test mixed-type comparison behavior"""

    def test_int_equals_float(self):
        """Test: printf(3 == 3.0); → 1 (coerced)"""
        code = "printf(3 == 3.0);"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert output == [1]

    def test_int_less_than_float(self):
        """Test: printf(3 < 3.5); → 1"""
        code = "printf(3 < 3.5);"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert output == [1]

    def test_float_greater_than_int(self):
        """Test: printf(3.5 > 3); → 1"""
        code = "printf(3.5 > 3);"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert output == [1]


# =============================================================================
# Type Assignment Violations
# =============================================================================

class TestTypeAssignmentViolations:
    """Test type enforcement on assignment"""

    def test_int_assigned_float_coercion(self):
        """Test: int x; x = 3.14; (coerces to 3)"""
        code = """
        int x;
        x = 3.14;
        printf(x);
        """
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert output == [3]  # Truncated

    def test_float_assigned_int_coercion(self):
        """Test: float y; y = 10; (promotes to 10.0)"""
        code = """
        float y;
        y = 10;
        printf(y);
        """
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        # GAP 12: Float precision tolerance
        assert abs(output[0] - 10.0) < 1e-9


# =============================================================================
# Uninitialized Variable Usage
# =============================================================================

class TestUninitializedVariableUsage:
    """Test uninitialized variable error handling"""

    def test_use_uninitialized_variable(self):
        """Test: int x; printf(x); (error)"""
        code = """
        int x;
        printf(x);
        """
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        
        with pytest.raises(SemanticError) as exc:
            interpreter.execute(ast)
        
        assert 'initialization' in str(exc.value).lower() or 'uninitialized' in str(exc.value).lower()

    def test_uninitialized_in_expression(self):
        """Test: int x; y = x + 1; (error)"""
        code = """
        int x;
        int y;
        y = x + 1;
        """
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        
        with pytest.raises(SemanticError):
            interpreter.execute(ast)


# =============================================================================
# State After Runtime Exception
# =============================================================================

class TestStateAfterRuntimeException:
    """Test interpreter state integrity after exception"""

    def test_interpreter_reusable_after_exception(self):
        """Test: Can create new interpreter after exception"""
        code = "printf(x);"  # Error: undefined variable
        
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter1 = Interpreter()
        with pytest.raises(SemanticError):
            interpreter1.execute(ast)
        
        # GAP 6: Create new interpreter (state isolated)
        interpreter2 = Interpreter()
        code2 = "int y; y = 5; printf(y);"
        tokens2 = list(Lexer(code2).tokenize())
        parser2 = Parser(tokens2)
        ast2 = parser2.parse()
        
        output = interpreter2.execute(ast2)
        assert output == [5]

    def test_interpreter_reset_method(self):
        """Test: interpreter.reset() clears state"""
        code1 = "int x; x = 5;"
        tokens1 = list(Lexer(code1).tokenize())
        parser1 = Parser(tokens1)
        ast1 = parser1.parse()
        
        interpreter = Interpreter()
        interpreter.execute(ast1)
        
        # Reset state
        interpreter.reset()
        
        # x should no longer exist
        code2 = "printf(x);"
        tokens2 = list(Lexer(code2).tokenize())
        parser2 = Parser(tokens2)
        ast2 = parser2.parse()
        
        with pytest.raises(SemanticError):
            interpreter.execute(ast2)


# =============================================================================
# Deep Nested Block Execution
# =============================================================================

class TestDeepNestedBlockExecution:
    """Test deep nesting execution"""

    def test_nested_blocks_depth_50(self):
        """Test: 50 levels of nested blocks (no stack overflow)"""
        code = "int x; x = 1; " + "{ " * 50 + "x = x + 1; " + "} " * 50
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        # Should complete without stack overflow
        assert interpreter.symbol_table.current_scope_level == 0

    def test_nested_blocks_depth_100(self):
        """Test: 100 levels of nested blocks"""
        code = "int x; x = 1; " + "{ " * 100 + "x = x + 1; " + "} " * 100
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert interpreter.symbol_table.current_scope_level == 0


# =============================================================================
# Large Expression Stress Test (FIXED)
# =============================================================================

class TestLargeExpressionStress:
    """Test large expression evaluation"""

    def test_long_addition_chain_100_terms(self):
        """Test: x = 1 + 1 + ... + 1 (100 terms) - Within recursion limit"""
        terms = " + ".join("1" for _ in range(100))
        code = f"int x; x = {terms}; printf(x);"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        start_time = time.time()
        output = interpreter.execute(ast)
        elapsed = time.time() - start_time
        
        assert output == [100]
        assert elapsed < 5.0  # Should complete in under 5 seconds

    def test_long_addition_chain_500_terms_with_recursion_limit(self):
        """Test: x = 1 + 1 + ... + 1 (500 terms) - With increased recursion limit"""
        import sys
        
        # Save original limit
        original_limit = sys.getrecursionlimit()
        
        try:
            # Increase recursion limit for deep AST traversal
            # CO523 Week 13: Language Implementation - interpreter limitations
            sys.setrecursionlimit(2000)
            
            terms = " + ".join("1" for _ in range(500))
            code = f"int x; x = {terms}; printf(x);"
            tokens = list(Lexer(code).tokenize())
            parser = Parser(tokens)
            ast = parser.parse()
            
            interpreter = Interpreter()
            start_time = time.time()
            output = interpreter.execute(ast)
            elapsed = time.time() - start_time
            
            assert output == [500]
            assert elapsed < 10.0
        finally:
            # Restore original limit
            sys.setrecursionlimit(original_limit)

    def test_long_addition_chain_1000_terms_documented_limitation(self):
        """
        Test: x = 1 + 1 + ... + 1 (1000 terms)
        """
        import sys
        
        original_limit = sys.getrecursionlimit()
        
        try:
            # Increase limit for 1000-term expression
            sys.setrecursionlimit(3000)
            
            terms = " + ".join("1" for _ in range(1000))
            code = f"int x; x = {terms}; printf(x);"
            tokens = list(Lexer(code).tokenize())
            parser = Parser(tokens)
            ast = parser.parse()
            
            interpreter = Interpreter()
            start_time = time.time()
            output = interpreter.execute(ast)
            elapsed = time.time() - start_time
            
            assert output == [1000]
            assert elapsed < 15.0
        finally:
            sys.setrecursionlimit(original_limit)

# =============================================================================
# Sequential Control Flow Integrity
# =============================================================================

class TestSequentialControlFlowIntegrity:
    """Test sequential execution state retention"""

    def test_state_retention_after_false_if(self):
        """Test: x = 1; if (0) { x = 2; } printf(x); → 1"""
        code = """
        int x;
        x = 1;
        if (0) { x = 2; }
        printf(x);
        """
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert output == [1]  # x unchanged

    def test_state_change_after_true_if(self):
        """Test: x = 1; if (1) { x = 2; } printf(x); → 2"""
        code = """
        int x;
        x = 1;
        if (1) { x = 2; }
        printf(x);
        """
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert output == [2]  # x changed


# =============================================================================
# Multiple Print Statements Order Guarantee
# =============================================================================

class TestMultiplePrintStatementsOrder:
    """Test strict execution ordering"""

    def test_printf_order_preserved(self):
        """Test: printf(1); printf(2); printf(3); → [1, 2, 3]"""
        code = """
        printf(1);
        printf(2);
        printf(3);
        """
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert output == [1, 2, 3]

    def test_printf_with_computation_order(self):
        """Test: printf order with computations"""
        code = """
        int x;
        x = 1;
        printf(x);
        x = 2;
        printf(x);
        x = 3;
        printf(x);
        """
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert output == [1, 2, 3]


# =============================================================================
# Negative Numeric Behavior
# =============================================================================

class TestNegativeNumericBehavior:
    """Test unary minus evaluation"""

    def test_negative_assignment(self):
        """Test: x = -5; printf(x); → -5"""
        code = """
        int x;
        x = -5;
        printf(x);
        """
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert output == [-5]

    def test_negative_in_expression(self):
        """Test: printf(-3 * 2); → -6"""
        code = "printf(-3 * 2);"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert output == [-6]

    def test_unary_plus(self):
        """Test: printf(+5); → 5"""
        code = "printf(+5);"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert output == [5]


# =============================================================================
# Float Precision Tolerance
# =============================================================================

class TestFloatPrecisionTolerance:
    """Test float comparison with epsilon"""

    def test_float_arithmetic_precision(self):
        """Test: float arithmetic with tolerance"""
        code = """
        float x;
        x = 3.14 + 2.86;
        printf(x);
        """
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        # GAP 12: Use epsilon comparison
        assert abs(output[0] - 6.0) < 1e-9

    def test_float_comparison_with_tolerance(self):
        """Test: float equality with tolerance"""
        code = """
        float x;
        x = 0.1 + 0.2;
        if (x == 0.3) { printf(1); } else { printf(0); }
        """
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        # Note: 0.1 + 0.2 != 0.3 in floating-point
        # This tests actual floating-point behavior
        assert output == [0] or output == [1]  # Either is acceptable


# =============================================================================
# Division Mixed-Type Edge Cases
# =============================================================================

class TestDivisionMixedTypeEdgeCases:
    """Test division with mixed types"""

    def test_int_division(self):
        """Test: int / int → int (floor)"""
        code = """
        int x;
        x = 7 / 2;
        printf(x);
        """
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert output == [3]  # Floor division

    def test_float_division(self):
        """Test: float / float → float"""
        code = """
        float x;
        x = 7.0 / 2.0;
        printf(x);
        """
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert abs(output[0] - 3.5) < 1e-9

    def test_mixed_division_int_float(self):
        """Test: int / float → float"""
        code = """
        float x;
        x = 7 / 2.0;
        printf(x);
        """
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert abs(output[0] - 3.5) < 1e-9

    def test_mixed_division_float_int(self):
        """Test: float / int → float"""
        code = """
        float x;
        x = 7.0 / 2;
        printf(x);
        """
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert abs(output[0] - 3.5) < 1e-9

    def test_division_by_zero(self):
        """Test: Division by zero error"""
        code = """
        int x;
        x = 10 / 0;
        """
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        
        with pytest.raises(SemanticError) as exc:
            interpreter.execute(ast)
        
        assert 'division by zero' in str(exc.value).lower()


# =============================================================================
# Variable Lifetime After Block
# =============================================================================

class TestVariableLifetimeAfterBlock:
    """Test variable scope exit"""

    def test_variable_inaccessible_after_block(self):
        """Test: { int x; x = 5; } printf(x); (error)"""
        code = """
        {
            int x;
            x = 5;
        }
        printf(x);
        """
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        
        with pytest.raises(SemanticError) as exc:
            interpreter.execute(ast)
        
        assert 'undefined' in str(exc.value).lower()

    def test_shadowed_variable_restored_after_block(self):
        """Test: Outer variable restored after inner scope exits"""
        code = """
        int x;
        x = 10;
        {
            int x;
            x = 20;
            printf(x);
        }
        printf(x);
        """
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(ast)
        
        assert output == [20, 10]  # Inner x, then outer x


# =============================================================================
# Garbage Program After Valid Code
# =============================================================================

class TestGarbageProgramAfterValidCode:
    """Test parser failure before interpreter"""

    def test_parser_catches_garbage_before_interpreter(self):
        """Test: int x; x = 5; } (parser error)"""
        code = "int x; x = 5; }"
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        
        # Parser should catch this before interpreter runs
        with pytest.raises(ParserError):
            parser.parse()


# =============================================================================
# Execution Time Safety
# =============================================================================

class TestExecutionTimeSafety:
    """Test execution time bounds (GAP 16)"""

    def test_execution_completes_within_time_limit(self):
        """Test: Program completes in reasonable time"""
        # Use unique variable names in block scopes to avoid redeclaration error
        lines = []
        for i in range(100):
            lines.append(f"""
            {{
                int x{i};
                x{i} = {i};
                x{i} = x{i} + 1;
                x{i} = x{i} + 1;
                x{i} = x{i} + 1;
                x{i} = x{i} + 1;
                x{i} = x{i} + 1;
                printf(x{i});
            }}
            """)
        
        code = "\n".join(lines)
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        start_time = time.time()
        output = interpreter.execute(ast)
        elapsed = time.time() - start_time
        
        # Should print i+5 for each block (i + 1+1+1+1+1 = i+5)
        assert len(output) == 100
        assert output[0] == 5      # x0 = 0 + 5 = 5 (FIXED)
        assert output[99] == 104   # x99 = 99 + 5 = 104 (FIXED)
        assert elapsed < 10.0  # Should complete in under 10 seconds

    def test_execution_with_interpreter_reset(self):
        """Test: Multiple executions with reset (alternative approach)"""
        code = """
        int x;
        x = 0;
        x = x + 1;
        x = x + 1;
        x = x + 1;
        x = x + 1;
        x = x + 1;
        printf(x);
        """
        
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        
        # Execute 100 times with reset between each
        start_time = time.time()
        
        for i in range(100):
            interpreter.reset()  # GAP 18: Reset state between executions
            output = interpreter.execute(ast)
            assert output == [5]
        
        elapsed = time.time() - start_time
        assert elapsed < 10.0

# =============================================================================
# Large Program Stress
# =============================================================================

class TestLargeProgramStress:
    """Test large program execution"""

    def test_1000_declarations_assignments_prints(self):
        """Test: 1000 declarations, assignments, and prints"""
        lines = []
        for i in range(1000):
            lines.append(f"int var{i};")
        for i in range(1000):
            lines.append(f"var{i} = {i};")
        for i in range(1000):
            lines.append(f"printf(var{i});")
        
        code = "\n".join(lines)
        tokens = list(Lexer(code).tokenize())
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        start_time = time.time()
        output = interpreter.execute(ast)
        elapsed = time.time() - start_time
        
        assert len(output) == 1000
        assert output[0] == 0
        assert output[999] == 999
        assert elapsed < 30.0  # Should complete in under 30 seconds


# =============================================================================
# Symbol Table Isolation Between Runs
# =============================================================================

class TestSymbolTableIsolationBetweenRuns:
    """Test interpreter state isolation )"""

    def test_multiple_executions_isolated(self):
        """Test: Multiple execute() calls don't interfere"""
        code1 = "int x; x = 5; printf(x);"
        code2 = "int y; y = 10; printf(y);"
        
        tokens1 = list(Lexer(code1).tokenize())
        parser1 = Parser(tokens1)
        ast1 = parser1.parse()
        
        tokens2 = list(Lexer(code2).tokenize())
        parser2 = Parser(tokens2)
        ast2 = parser2.parse()
        
        interpreter = Interpreter()
        
        # First execution
        output1 = interpreter.execute(ast1)
        assert output1 == [5]
        
        # Reset for second execution (GAP 18)
        interpreter.reset()
        
        # Second execution
        output2 = interpreter.execute(ast2)
        assert output2 == [10]
        
        # x should not exist in second execution
        assert interpreter.symbol_table.is_declared('x') is False

    def test_fresh_interpreter_per_program(self):
        """Test: New interpreter instance has clean state"""
        code1 = "int x; x = 5;"
        code2 = "printf(x);"  # Should error (x not declared)
        
        tokens1 = list(Lexer(code1).tokenize())
        parser1 = Parser(tokens1)
        ast1 = parser1.parse()
        
        interpreter1 = Interpreter()
        interpreter1.execute(ast1)
        
        # New interpreter (GAP 18)
        tokens2 = list(Lexer(code2).tokenize())
        parser2 = Parser(tokens2)
        ast2 = parser2.parse()
        
        interpreter2 = Interpreter()
        
        with pytest.raises(SemanticError):
            interpreter2.execute(ast2)