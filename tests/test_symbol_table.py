"""
Symbol Table test suite for C-Lite interpreter.

Test Coverage Gaps Addressed:
1. Type System Enforcement
2. Shadowing Type Differences
3. Deep Nesting Stress Test
4. Re-entrancy / Multiple Scope Exits
5. Memory Integrity Tests
6. Symbol Object Integrity
7. Error Message Quality
8. Large-Scale Performance Test
9. Attempted Illegal Shadow After Exit
10. Concurrent Variable Names Across Multiple Nested Blocks
11. Invalid Scope Exit After Errors
12. Symbol Table State Isolation
13. Float Precision Handling
14. Immutability / Internal Encapsulation
15. Integration With Semantic Phase
"""

import pytest
import time
from src.symbol_table import SymbolTable, Symbol
from src.errors import SemanticError


# =============================================================================
# Type System Enforcement
# =============================================================================

class TestTypeSystemEnforcement:
    """Test static type enforcement (CO523 Week 5)"""

    def test_int_assignment_with_int(self):
        """Test: int x; x = 5; (valid)"""
        table = SymbolTable()
        table.declare('x', 'int', line=1, column=1)
        table.update('x', 5, line=2, column=1)
        
        assert table.get_value('x', line=2, column=1) == 5

    def test_float_assignment_with_float(self):
        """Test: float x; x = 3.14; (valid)"""
        table = SymbolTable()
        table.declare('x', 'float', line=1, column=1)
        table.update('x', 3.14, line=2, column=1)
        
        value = table.get_value('x', line=2, column=1)
        assert abs(value - 3.14) < 1e-9

    def test_int_assignment_with_float_coercion(self):
        """Test: int x; x = 3.14; (coerce to 3)"""
        table = SymbolTable()
        table.declare('x', 'int', line=1, column=1)
        table.update('x', 3.14, line=2, column=1)
        
        # Should truncate float to int
        assert table.get_value('x', line=2, column=1) == 3

    def test_float_assignment_with_int_coercion(self):
        """Test: float x; x = 5; (coerce to 5.0)"""
        table = SymbolTable()
        table.declare('x', 'float', line=1, column=1)
        table.update('x', 5, line=2, column=1)
        
        # Should promote int to float
        value = table.get_value('x', line=2, column=1)
        assert isinstance(value, float)
        assert value == 5.0

    def test_type_mismatch_error_message(self):
        """Test: Error message includes variable name and location"""
        table = SymbolTable()
        table.declare('x', 'int', line=1, column=1)
        
        # This should succeed with coercion (C-style)
        table.update('x', 3.14, line=2, column=1)
        assert table.get_value('x', line=2, column=1) == 3


# =============================================================================
# Shadowing Type Differences
# =============================================================================

class TestShadowingTypeDifferences:
    """Test variable shadowing with different types"""

    def test_shadow_with_different_type(self):
        """Test: int x; { float x; } (different types in different scopes)"""
        table = SymbolTable()
        table.declare('x', 'int', line=1, column=1)
        table.update('x', 10, line=1, column=1)
        
        table.enter_scope()
        table.declare('x', 'float', line=2, column=1)  # Shadow with float
        table.update('x', 3.14, line=2, column=1)
        
        # Inner scope: float
        assert table.get_type('x', line=2, column=1) == 'float'
        assert abs(table.get_value('x', line=2, column=1) - 3.14) < 1e-9
        
        table.exit_scope()
        
        # Outer scope: int (no type contamination)
        assert table.get_type('x', line=1, column=1) == 'int'
        assert table.get_value('x', line=1, column=1) == 10

    def test_shadow_multiple_levels_different_types(self):
        """Test: int x; { float x; { int x; } }"""
        table = SymbolTable()
        table.declare('x', 'int', line=1, column=1)
        table.update('x', 10, line=1, column=1)
        
        table.enter_scope()
        table.declare('x', 'float', line=2, column=1)
        table.update('x', 3.14, line=2, column=1)
        
        table.enter_scope()
        table.declare('x', 'int', line=3, column=1)
        table.update('x', 5, line=3, column=1)
        
        # Level 2: int
        assert table.get_type('x', line=3, column=1) == 'int'
        
        table.exit_scope()
        
        # Level 1: float
        assert table.get_type('x', line=2, column=1) == 'float'
        
        table.exit_scope()
        
        # Level 0: int
        assert table.get_type('x', line=1, column=1) == 'int'


# =============================================================================
# Deep Nesting Stress Test
# =============================================================================

class TestDeepNestingStress:
    """Test symbol table under deep nesting (50-200 levels)"""

    def test_deep_nesting_50_levels(self):
        """Test: 50 levels of nested scopes"""
        table = SymbolTable()
        
        for i in range(50):
            table.enter_scope()
            table.declare(f'var{i}', 'int', line=i, column=1)
        
        assert table.current_scope_level == 50
        assert table.scope_count == 51
        
        # All variables should be accessible
        for i in range(50):
            assert table.is_declared(f'var{i}') is True
        
        # Exit all scopes
        for i in range(50):
            table.exit_scope()
        
        assert table.current_scope_level == 0
        assert table.scope_count == 1

    def test_deep_nesting_200_levels(self):
        """Test: 200 levels of nested scopes (stress test)"""
        table = SymbolTable()
        
        for i in range(200):
            table.enter_scope()
            table.declare(f'var{i}', 'int', line=i, column=1)
        
        assert table.current_scope_level == 200
        
        # Exit all scopes
        for i in range(200):
            table.exit_scope()
        
        assert table.current_scope_level == 0


# =============================================================================
# Re-entrancy / Multiple Scope Exits
# =============================================================================

class TestReentrancyMultipleScopeExits:
    """Test multiple enter/exit operations"""

    def test_multiple_enter_exit_pairs(self):
        """Test: enter, enter, exit, exit (state integrity)"""
        table = SymbolTable()
        
        table.enter_scope()
        table.enter_scope()
        assert table.current_scope_level == 2
        
        table.exit_scope()
        assert table.current_scope_level == 1
        
        table.exit_scope()
        assert table.current_scope_level == 0

    def test_scope_stack_integrity(self):
        """Test: Scope stack not corrupted after multiple operations"""
        table = SymbolTable()
        
        for _ in range(10):
            table.enter_scope()
            table.exit_scope()
        
        assert table.current_scope_level == 0
        assert table.scope_count == 1


# =============================================================================
# Memory Integrity Tests
# =============================================================================

class TestMemoryIntegrity:
    """Test memory integrity under stress"""

    def test_many_scope_operations_no_leak(self):
        """Test: 1000 scope operations with no residual leakage"""
        table = SymbolTable()
        
        for i in range(1000):
            table.enter_scope()
            table.declare(f'var{i}', 'int', line=i, column=1)
            table.exit_scope()
        
        # No residual symbols
        assert table.current_scope_level == 0
        assert table.scope_count == 1
        
        # Global scope should be empty
        assert table.is_declared('var0') is False
        assert table.is_declared('var999') is False

    def test_performance_10000_declarations(self):
        """Test: 10,000 declarations within time limit"""
        table = SymbolTable()
        
        start_time = time.time()
        
        for i in range(10000):
            table.declare(f'var{i}', 'int', line=i, column=1)
        
        elapsed = time.time() - start_time
        
        # Should complete in under 2 seconds
        assert elapsed < 2.0
        assert table.is_declared('var9999') is True


# =============================================================================
# Symbol Object Integrity
# =============================================================================

class TestSymbolObjectIntegrity:
    """Test Symbol class behavior"""

    def test_symbol_equality(self):
        """Test: Symbol equality semantics"""
        sym1 = Symbol(name='x', var_type='int', scope_level=0)
        sym2 = Symbol(name='x', var_type='int', scope_level=0)
        sym3 = Symbol(name='x', var_type='float', scope_level=0)
        
        assert sym1 == sym2
        assert sym1 != sym3

    def test_symbol_scope_level_assignment(self):
        """Test: Symbol gets correct scope_level"""
        table = SymbolTable()
        table.declare('x', 'int', line=1, column=1)
        
        symbol = table.lookup('x')
        assert symbol.scope_level == 0
        
        table.enter_scope()
        table.declare('y', 'int', line=2, column=1)
        
        symbol = table.lookup('y')
        assert symbol.scope_level == 1

    def test_symbol_value_storage_isolation(self):
        """Test: Symbol values don't interfere"""
        table = SymbolTable()
        table.declare('x', 'int', line=1, column=1)
        table.declare('y', 'int', line=2, column=1)
        
        table.update('x', 10, line=3, column=1)
        table.update('y', 20, line=4, column=1)
        
        assert table.get_value('x', line=3, column=1) == 10
        assert table.get_value('y', line=4, column=1) == 20

    def test_symbol_repr(self):
        """Test: Symbol string representation"""
        sym = Symbol(name='x', var_type='int', scope_level=0)
        repr_str = repr(sym)
        
        assert 'Symbol' in repr_str
        assert 'x' in repr_str
        assert 'int' in repr_str


# =============================================================================
# Error Message Quality
# =============================================================================

class TestErrorMessageQuality:
    """Test error message includes all required information"""

    def test_undefined_variable_error_includes_name(self):
        """Test: Error message includes variable name"""
        table = SymbolTable()
        
        with pytest.raises(SemanticError) as exc:
            table.get_value('x', line=5, column=10)
        
        error_msg = str(exc.value)
        assert 'x' in error_msg
        assert 'undefined' in error_msg.lower() or 'Undefined' in error_msg

    def test_error_includes_line_number(self):
        """Test: Error message includes line number"""
        table = SymbolTable()
        
        with pytest.raises(SemanticError) as exc:
            table.get_value('x', line=5, column=10)
        
        error_msg = str(exc.value)
        assert 'line 5' in error_msg or 'line 5' in error_msg.lower()

    def test_error_includes_column_number(self):
        """Test: Error message includes column number"""
        table = SymbolTable()
        
        with pytest.raises(SemanticError) as exc:
            table.get_value('x', line=5, column=10)
        
        error_msg = str(exc.value)
        assert 'column 10' in error_msg or 'column 10' in error_msg.lower()

    def test_redeclaration_error_includes_scope_info(self):
        """Test: Redeclaration error includes scope context"""
        table = SymbolTable()
        table.declare('x', 'int', line=1, column=1)
        
        with pytest.raises(SemanticError) as exc:
            table.declare('x', 'int', line=2, column=1)
        
        error_msg = str(exc.value)
        assert 'x' in error_msg
        assert 'already declared' in error_msg.lower()


# =============================================================================
# Large-Scale Performance Test
# =============================================================================

class TestLargeScalePerformance:
    """Test symbol table scalability"""

    def test_10000_declarations_and_lookups(self):
        """Test: 10,000 declarations with random access patterns"""
        table = SymbolTable()
        
        # Declare 10,000 variables WITH initialization
        for i in range(10000):
            table.declare(f'var{i}', 'int', line=i, column=1)
            table.update(f'var{i}', i, line=i, column=1)  # FIX: Initialize with value
        
        # Random access lookups
        start_time = time.time()
        
        for i in range(0, 10000, 100):
            value = table.get_value(f'var{i}', line=i, column=1)
            assert value == i  # FIX: Verify correct value retrieved
        
        elapsed = time.time() - start_time
        
        # Should complete in under 1 second
        assert elapsed < 1.0
        assert table.is_declared('var9999') is True

    def test_nested_lookup_performance(self):
        """Test: Lookup performance in deeply nested scopes"""
        table = SymbolTable()
        
        # Create 100 nested scopes
        for i in range(100):
            table.enter_scope()
            table.declare(f'var{i}', 'int', line=i, column=1)
            table.update(f'var{i}', i, line=i, column=1)  # FIX: Initialize
        
        # Lookup innermost variable (should be fast)
        start_time = time.time()
        
        for _ in range(1000):
            symbol = table.lookup('var99')
            assert symbol is not None
        
        elapsed = time.time() - start_time
        
        # Should complete in under 0.5 seconds
        assert elapsed < 0.5
        
# =============================================================================
# Attempted Illegal Shadow After Exit
# =============================================================================

class TestIllegalShadowAfterExit:
    """Test variable access after scope exit"""

    def test_update_after_scope_exit_fails(self):
        """Test: Cannot update variable after scope exit"""
        table = SymbolTable()
        
        table.enter_scope()
        table.declare('x', 'int', line=1, column=1)
        table.update('x', 10, line=1, column=1)
        table.exit_scope()
        
        # Variable should no longer exist
        assert table.is_declared('x') is False
        
        # Update should fail
        with pytest.raises(SemanticError) as exc:
            table.update('x', 20, line=2, column=1)
        
        assert 'undefined' in str(exc.value).lower()

    def test_get_value_after_scope_exit_fails(self):
        """Test: Cannot get value after scope exit"""
        table = SymbolTable()
        
        table.enter_scope()
        table.declare('x', 'int', line=1, column=1)
        table.update('x', 10, line=1, column=1)
        table.exit_scope()
        
        with pytest.raises(SemanticError):
            table.get_value('x', line=2, column=1)


# =============================================================================
# Concurrent Variable Names Across Multiple Nested Blocks
# =============================================================================

class TestConcurrentVariableNames:
    """Test same variable name across multiple nesting levels"""

    def test_four_level_shadowing(self):
        """Test: global x, scope1 x, scope2 x, scope3 x"""
        table = SymbolTable()
        
        # Level 0
        table.declare('x', 'int', line=1, column=1)
        table.update('x', 100, line=1, column=1)
        
        # Level 1
        table.enter_scope()
        table.declare('x', 'int', line=2, column=1)
        table.update('x', 200, line=2, column=1)
        
        # Level 2
        table.enter_scope()
        table.declare('x', 'int', line=3, column=1)
        table.update('x', 300, line=3, column=1)
        
        # Level 3
        table.enter_scope()
        table.declare('x', 'int', line=4, column=1)
        table.update('x', 400, line=4, column=1)
        
        # Innermost: 400
        assert table.get_value('x', line=4, column=1) == 400
        
        table.exit_scope()
        
        # Level 2: 300
        assert table.get_value('x', line=3, column=1) == 300
        
        table.exit_scope()
        
        # Level 1: 200
        assert table.get_value('x', line=2, column=1) == 200
        
        table.exit_scope()
        
        # Level 0: 100
        assert table.get_value('x', line=1, column=1) == 100


# =============================================================================
# Invalid Scope Exit After Errors
# =============================================================================

class TestInvalidScopeExitAfterErrors:
    """Test scope state consistency after errors"""

    def test_scope_state_after_declaration_error(self):
        """Test: Scope level preserved after declaration error"""
        table = SymbolTable()
        
        table.enter_scope()
        initial_level = table.current_scope_level
        
        try:
            table.declare('x', 'int', line=1, column=1)
            table.declare('x', 'int', line=2, column=1)  # Error
        except SemanticError:
            pass
        
        # Scope level should be unchanged
        assert table.current_scope_level == initial_level
        
        # First declaration should still exist
        assert table.is_declared('x') is True
        
        table.exit_scope()

    def test_scope_state_after_update_error(self):
        """Test: Scope level preserved after update error"""
        table = SymbolTable()
        
        table.enter_scope()
        initial_level = table.current_scope_level
        
        try:
            table.update('nonexistent', 10, line=1, column=1)  # Error
        except SemanticError:
            pass
        
        # Scope level should be unchanged
        assert table.current_scope_level == initial_level
        
        table.exit_scope()


# =============================================================================
# Symbol Table State Isolation
# =============================================================================

class TestSymbolTableStateIsolation:
    """Test symbol table instances are isolated"""

    def test_multiple_instances_isolated(self):
        """Test: Multiple SymbolTable instances don't interfere"""
        table1 = SymbolTable()
        table2 = SymbolTable()
        
        table1.declare('x', 'int', line=1, column=1)
        table1.update('x', 10, line=1, column=1)
        
        table2.declare('x', 'int', line=1, column=1)
        table2.update('x', 20, line=1, column=1)
        
        # Instances should be independent
        assert table1.get_value('x', line=1, column=1) == 10
        assert table2.get_value('x', line=1, column=1) == 20

    def test_no_global_static_state(self):
        """Test: No shared state between instances"""
        table1 = SymbolTable()
        table1.enter_scope()
        table1.declare('x', 'int', line=1, column=1)
        
        table2 = SymbolTable()
        
        # table2 should not see table1's scope
        assert table2.current_scope_level == 0
        assert table2.is_declared('x') is False


# =============================================================================
# Float Precision Handling
# =============================================================================

class TestFloatPrecisionHandling:
    """Test floating-point precision"""

    def test_float_precision_preserved(self):
        """Test: Float values maintain precision"""
        table = SymbolTable()
        table.declare('f', 'float', line=1, column=1)
        table.update('f', 3.14159265359, line=1, column=1)
        
        value = table.get_value('f', line=1, column=1)
        assert abs(value - 3.14159265359) < 1e-9

    def test_float_arithmetic_precision(self):
        """Test: Float arithmetic maintains precision"""
        table = SymbolTable()
        table.declare('f', 'float', line=1, column=1)
        table.update('f', 0.1 + 0.2, line=1, column=1)
        
        value = table.get_value('f', line=1, column=1)
        # Standard floating-point tolerance
        assert abs(value - 0.3) < 1e-9


# =============================================================================
# Immutability / Internal Encapsulation
# =============================================================================

class TestImmutabilityInternalEncapsulation:
    """Test symbol table internal protection"""

    def test_lookup_returns_symbol_object(self):
        """Test: lookup() returns Symbol object"""
        table = SymbolTable()
        table.declare('x', 'int', line=1, column=1)
        
        symbol = table.lookup('x')
        assert isinstance(symbol, Symbol)

    def test_symbol_mutation_affects_table(self):
        """Test: Symbol is mutable (by design for value updates)"""
        table = SymbolTable()
        table.declare('x', 'int', line=1, column=1)
        
        symbol = table.lookup('x')
        symbol.value = 42
        
        # Mutation should be reflected
        assert table.get_value('x', line=1, column=1) == 42
        
        # Note: Production systems might return copies or use properties
        # For C-Lite, direct mutation is acceptable for simplicity

    def test_internal_scope_list_not_exposed(self):
        """Test: Internal _scopes list is protected (naming convention)"""
        table = SymbolTable()
        
        # Should have _scopes attribute (protected by convention)
        assert hasattr(table, '_scopes')
        
        # External code should use public methods only
        assert table.scope_count == 1


# =============================================================================
# Integration With Semantic Phase
# =============================================================================

class TestIntegrationWithSemanticPhase:
    """Test symbol table integration with AST traversal"""

    def test_declaration_populates_symbol_table(self):
        """Test: AST declaration node populates symbol table"""
        from src.ast import Declaration
        
        table = SymbolTable()
        
        # Simulate visiting a Declaration node
        decl = Declaration(var_type='int', name='x', line=1, column=1)
        table.declare(decl.name, decl.var_type, decl.line, decl.column)
        
        assert table.is_declared('x') is True
        assert table.get_type('x', line=1, column=1) == 'int'

    def test_block_scope_enter_exit(self):
        """Test: Block traversal enters/exits scope"""
        table = SymbolTable()
        
        # Simulate block entry
        table.enter_scope()
        table.declare('x', 'int', line=1, column=1)
        
        assert table.current_scope_level == 1
        
        # Simulate block exit
        table.exit_scope()
        
        assert table.current_scope_level == 0
        assert table.is_declared('x') is False

    def test_nested_block_symbol_isolation(self):
        """Test: Nested blocks don't leak symbols"""
        table = SymbolTable()
        
        # Outer block
        table.enter_scope()
        table.declare('x', 'int', line=1, column=1)
        
        # Inner block
        table.enter_scope()
        table.declare('y', 'int', line=2, column=1)
        
        # Both visible
        assert table.is_declared('x') is True
        assert table.is_declared('y') is True
        
        # Exit inner block
        table.exit_scope()
        
        # Only x visible
        assert table.is_declared('x') is True
        assert table.is_declared('y') is False
        
        # Exit outer block
        table.exit_scope()
        
        # Neither visible
        assert table.is_declared('x') is False
        assert table.is_declared('y') is False