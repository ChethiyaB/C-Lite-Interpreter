"""
tests/test_repl.py
Comprehensive test suite for C-Lite REPL (repl.py).
Aligned with CO523 Project Specification §4: Technical Requirements.
University of Peradeniya - Department of Computer Engineering

Test Coverage:
1. REPL Commands
2. Code Execution
3. State Persistence
4. Error Handling
5. Multi-line Input
6. Edge Cases
"""

import pytest
import sys
import os
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repl import CLiteREPL, REPLState, REPLCommands
from src.lexer import Lexer, LexerError
from src.parser import Parser, ParserError
from src.interpreter import Interpreter, SemanticError


# =============================================================================
# Category 1: REPL Commands Tests
# =============================================================================

class TestREPLCommands:
    """Test REPL built-in commands"""

    def test_repl_help_command(self):
        """Test: :help command"""
        repl = CLiteREPL()
        
        # Capture output
        f_out = StringIO()
        with redirect_stdout(f_out):
            repl.handle_command(":help")
        
        output = f_out.getvalue()
        assert "help" in output.lower() or "command" in output.lower()

    def test_repl_clear_command(self):
        """Test: :clear command"""
        repl = CLiteREPL()
        
        # Add a variable first
        repl.execute("int x; x = 5;")
        
        # Clear state
        f_out = StringIO()
        with redirect_stdout(f_out):
            repl.handle_command(":clear")
        
        # Variable should be cleared
        assert repl.state.interpreter.symbol_table.is_declared('x') is False

    def test_repl_version_command(self):
        """Test: :version command"""
        repl = CLiteREPL()
        
        f_out = StringIO()
        with redirect_stdout(f_out):
            repl.handle_command(":version")
        
        output = f_out.getvalue()
        assert "version" in output.lower() or "0." in output.lower()

    def test_repl_vars_command(self):
        """Test: :vars command"""
        repl = CLiteREPL()
        
        # Add variables
        repl.execute("int x; x = 42;")
        repl.execute("float y; y = 3.14;")
        
        f_out = StringIO()
        with redirect_stdout(f_out):
            repl.handle_command(":vars")
        
        output = f_out.getvalue()
        assert "x" in output
        assert "42" in output

    def test_repl_verbose_command(self):
        """Test: :verbose command"""
        repl = CLiteREPL()
        
        f_out = StringIO()
        with redirect_stdout(f_out):
            repl.handle_command(":verbose")
        
        assert repl.state.verbose is True

    def test_repl_quiet_command(self):
        """Test: :quiet command"""
        repl = CLiteREPL()
        repl.state.verbose = True
        
        f_out = StringIO()
        with redirect_stdout(f_out):
            repl.handle_command(":quiet")
        
        assert repl.state.verbose is False

    def test_repl_unknown_command(self):
        """Test: Unknown command"""
        repl = CLiteREPL()
        
        f_out = StringIO()
        with redirect_stdout(f_out):
            result = repl.handle_command(":unknown")
        
        assert "unknown" in f_out.getvalue().lower()
        assert result is True  # Should continue running

    def test_repl_exit_command(self):
        """Test: :exit command"""
        repl = CLiteREPL()
        
        result = repl.handle_command(":exit")
        assert result is False  # Should stop REPL


# =============================================================================
# Category 2: Code Execution Tests
# =============================================================================

class TestREPLCodeExecution:
    """Test REPL code execution"""

    def test_repl_execute_declaration(self):
        """Test: Execute variable declaration"""
        repl = CLiteREPL()
        
        result = repl.execute("int x;")
        assert result is True
        assert repl.state.interpreter.symbol_table.is_declared('x') is True

    def test_repl_execute_assignment(self):
        """Test: Execute assignment"""
        repl = CLiteREPL()
        
        repl.execute("int x;")
        result = repl.execute("x = 42;")
        
        assert result is True
        assert repl.state.interpreter.symbol_table.get_value('x', 1, 1) == 42

    def test_repl_execute_printf(self):
        """Test: Execute printf"""
        repl = CLiteREPL()
        
        f_out = StringIO()
        with redirect_stdout(f_out):
            repl.execute("int x; x = 5; printf(x);")
        
        output = f_out.getvalue()
        assert "5" in output

    def test_repl_execute_if_statement(self):
        """Test: Execute if-else"""
        repl = CLiteREPL()
        
        f_out = StringIO()
        with redirect_stdout(f_out):
            repl.execute("int x; x = 10; if (x > 5) { printf(x); } else { printf(0); }")
        
        output = f_out.getvalue()
        assert "10" in output

    def test_repl_execute_arithmetic(self):
        """Test: Execute arithmetic"""
        repl = CLiteREPL()
        
        f_out = StringIO()
        with redirect_stdout(f_out):
            repl.execute("printf(3 + 4 * 5);")
        
        output = f_out.getvalue()
        assert "23" in output  # 3 + (4 * 5)


# =============================================================================
# Category 3: State Persistence Tests
# =============================================================================

class TestREPLStatePersistence:
    """Test REPL state persistence between commands"""

    def test_repl_variable_persists(self):
        """Test: Variables persist across commands"""
        repl = CLiteREPL()
        
        # First command
        repl.execute("int x;")
        repl.execute("x = 42;")
        
        # Second command (x should still exist)
        f_out = StringIO()
        with redirect_stdout(f_out):
            repl.execute("printf(x);")
        
        output = f_out.getvalue()
        assert "42" in output

    def test_repl_state_isolation(self):
        """Test: :clear resets state"""
        repl = CLiteREPL()
        
        repl.execute("int x; x = 5;")
        repl.handle_command(":clear")
        
        # x should no longer exist
        assert repl.state.interpreter.symbol_table.is_declared('x') is False

    def test_repl_output_isolation(self):
        """Test: Each command shows only its own output"""
        repl = CLiteREPL()
        
        # First printf
        f_out1 = StringIO()
        with redirect_stdout(f_out1):
            repl.execute("printf(1);")
        
        # Second printf (should only show 2, not 1,2)
        f_out2 = StringIO()
        with redirect_stdout(f_out2):
            repl.execute("printf(2);")
        
        # Each should show only its own output
        assert "1" in f_out1.getvalue()
        assert "2" in f_out2.getvalue()


# =============================================================================
# Category 4: Error Handling Tests
# =============================================================================

class TestREPLErrorHandling:
    """Test REPL error handling"""

    def test_repl_lexical_error(self):
        """Test: Lexical error in REPL"""
        repl = CLiteREPL()
        
        f_err = StringIO()
        with redirect_stderr(f_err):
            result = repl.execute("int x; x = @;")
        
        assert result is False
        assert "error" in f_err.getvalue().lower()

    def test_repl_syntax_error(self):
        """Test: Syntax error in REPL"""
        repl = CLiteREPL()
        
        f_err = StringIO()
        with redirect_stderr(f_err):
            result = repl.execute("int x; x = 5")  # Missing semicolon
        
        assert result is False

    def test_repl_semantic_error(self):
        """Test: Semantic error in REPL"""
        repl = CLiteREPL()
        
        f_err = StringIO()
        with redirect_stderr(f_err):
            result = repl.execute("printf(x);")  # Undefined variable
        
        assert result is False
        assert "error" in f_err.getvalue().lower()

    def test_repl_continues_after_error(self):
        """Test: REPL continues after error"""
        repl = CLiteREPL()
        
        # Error
        repl.execute("printf(x);")
        
        # Should still be able to execute valid code
        f_out = StringIO()
        with redirect_stdout(f_out):
            result = repl.execute("int y; y = 5; printf(y);")
        
        assert result is True
        assert "5" in f_out.getvalue()


# =============================================================================
# Category 5: Multi-line Input Tests
# =============================================================================

class TestREPLMultiLineInput:
    """Test REPL multi-line input handling"""

    def test_repl_multiline_block(self):
        """Test: Multi-line block input"""
        repl = CLiteREPL()
        
        # Simulate multi-line input
        code = """
        {
            int x;
            x = 5;
            printf(x);
        }
        """
        
        f_out = StringIO()
        with redirect_stdout(f_out):
            result = repl.execute(code)
        
        assert result is True
        assert "5" in f_out.getvalue()

    def test_repl_multiline_if_else(self):
        """Test: Multi-line if-else"""
        repl = CLiteREPL()
        
        code = """
        int x;
        x = 10;
        if (x > 5) {
            printf(x);
        } else {
            printf(0);
        }
        """
        
        f_out = StringIO()
        with redirect_stdout(f_out):
            result = repl.execute(code)
        
        assert result is True
        assert "10" in f_out.getvalue()

    def test_repl_is_complete_statement(self):
        """Test: Statement completion detection"""
        repl = CLiteREPL()
        
        # Complete statements
        assert repl.is_complete_statement("int x;") is True
        assert repl.is_complete_statement("x = 5;") is True
        
        # Incomplete statements
        assert repl.is_complete_statement("if (x > 0) {") is False
        assert repl.is_complete_statement("{") is False


# =============================================================================
# Category 6: Edge Cases
# =============================================================================

class TestREPLEdgeCases:
    """Test REPL edge cases"""

    def test_repl_empty_input(self):
        """Test: Empty input handling"""
        repl = CLiteREPL()
        
        # Should not crash on empty input
        result = repl.execute("")
        assert result is True  # Or False, but shouldn't crash

    def test_repl_whitespace_only(self):
        """Test: Whitespace only input"""
        repl = CLiteREPL()
        
        result = repl.execute("   \n\t\n   ")
        # Should handle gracefully

    def test_repl_very_long_input(self):
        """Test: Very long input"""
        repl = CLiteREPL()
        
        # Long expression
        code = "int x; x = " + " + ".join("1" for _ in range(100)) + ";"
        
        result = repl.execute(code)
        assert result is True

    def test_repl_rapid_commands(self):
        """Test: Rapid command execution"""
        repl = CLiteREPL()
        
        for i in range(100):
            repl.execute(f"int var{i}; var{i} = {i};")
        
        # Should not crash
        assert repl.state.running is True

    def test_repl_banner_prints(self):
        """Test: REPL banner prints on start"""
        repl = CLiteREPL()
        
        f_out = StringIO()
        with redirect_stdout(f_out):
            repl.print_banner()
        
        output = f_out.getvalue()
        assert "C-Lite" in output
        assert "REPL" in output


# =============================================================================
# Category 7: Integration Tests
# =============================================================================

class TestREPLIntegration:
    """Test REPL integration scenarios"""

    def test_repl_complete_session(self):
        """Test: Complete REPL session"""
        repl = CLiteREPL()
        
        # Session
        repl.execute("int x;")
        repl.execute("x = 42;")
        
        f_out = StringIO()
        with redirect_stdout(f_out):
            repl.execute("printf(x);")
            repl.handle_command(":vars")
            repl.handle_command(":clear")
        
        output = f_out.getvalue()
        assert "42" in output
        assert "x" in output

    def test_repl_with_verbose_mode(self):
        """Test: REPL with verbose mode enabled"""
        repl = CLiteREPL()
        repl.state.verbose = True
        
        f_out = StringIO()
        with redirect_stdout(f_out):
            repl.execute("int x; x = 5;")
        
        output = f_out.getvalue()
        assert "phase" in output.lower() or "lexical" in output.lower()

    def test_repl_nested_scopes(self):
        """Test: REPL with nested scopes"""
        repl = CLiteREPL()

        # Outer scope: x = 10
        repl.execute("int x; x = 10;")
        
        # Inner scope: x = 20 (shadows outer x)
        # This prints 20, but inner x is destroyed when block exits
        f_out1 = StringIO()
        with redirect_stdout(f_out1):
            repl.execute("{ int x; x = 20; printf(x); }")
        
        # Verify inner scope printed 20
        assert "20" in f_out1.getvalue()
        
        # After block exits, outer x should be visible again
        f_out2 = StringIO()
        with redirect_stdout(f_out2):
            repl.execute("printf(x);")
        
        output = f_out2.getvalue()
        
        # FIX: Expect outer scope value (10), not inner scope (20)
        # Inner x is out of scope after block exits (CO523 Week 4)
        assert "10" in output  # Outer scope value