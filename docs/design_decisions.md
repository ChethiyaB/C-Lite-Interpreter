# C-Lite Interpreter Design Decisions

## CO523 Project Specification §5: Design Discussion

### Lexical Analysis

#### Decision 1: Hand-Written Lexer vs Parser Generator
- **Choice**: Hand-written recursive scanner
- **Rationale**: Educational transparency, explicit error control
- **Trade-off**: More code, but clearer understanding of DFA implementation

#### Decision 2: Explicit EOF Token
- **Choice**: Generate explicit EOF token
- **Rationale**: Simplifies parser termination, aligns with FOLLOW set theory
- **Trade-off**: One extra token per program

#### Decision 3: Source Location Tracking
- **Choice**: 1-indexed line/column on every token
- **Rationale**: Professional error reporting
- **Trade-off**: Slightly more memory per token

### Syntax Analysis

#### Decision 4: Recursive Descent Parser
- **Choice**: LL(1) recursive descent
- **Rationale**: Educational value, explicit control flow, easy debugging
- **Trade-off**: Cannot handle left-recursion directly (grammar transformation required)

#### Decision 5: Operator Precedence Hierarchy
- **Choice**: 4-level expression hierarchy (relational, additive, multiplicative, primary)
- **Rationale**: Matches C semantics, correct AST construction
- **Trade-off**: More parser methods, but clearer precedence enforcement

#### Decision 6: Declarations in Blocks
- **Choice**: Allow declarations inside blocks
- **Rationale**: Matches C semantics, enables lexical scoping
- **Trade-off**: More complex symbol table management

### Semantic Evaluation

#### Decision 7: Visitor Pattern for Interpretation
- **Choice**: ASTVisitor pattern
- **Rationale**: Separates traversal from execution, extensible
- **Trade-off**: More classes, but cleaner architecture

#### Decision 8: Stack-Based Symbol Table
- **Choice**: List of scope dictionaries
- **Rationale**: Matches block scoping, efficient enter/exit
- **Trade-off**: O(n) lookup in deep nesting (acceptable for C-Lite)

#### Decision 9: C-Style Truthiness
- **Choice**: 0 = false, non-zero = true (int and float)
- **Rationale**: Matches C semantics
- **Trade-off**: Explicit coercion rules documented

#### Decision 10: Type Coercion on Assignment
- **Choice**: Implicit coercion (int←float truncates, float←int promotes)
- **Rationale**: Matches C semantics, simplifies mixed-type arithmetic
- **Trade-off**: Potential precision loss (documented in test suite)

#### Decision 11: Uninitialized Variable Detection
- **Choice**: Raise SemanticError on use before initialization
- **Rationale**: Type safety, prevents undefined behavior
- **Trade-off**: Slightly stricter than C (which allows uninitialized reads)

#### Decision 12: Integer Division
- **Choice**: int/int = floor division, float otherwise
- **Rationale**: Matches C semantics for integer types
- **Trade-off**: Explicit type coercion required for float division

### Error Handling Strategy

#### Decision 13: Fail-Fast vs Error Collection
- **Choice**: Fail-fast (stop on first error)
- **Rationale**: Simpler implementation, standard for educational compilers
- **Trade-off**: Only first error reported per parse/execution

#### Decision 14: Exception Hierarchy
- **Choice**: LexerError, ParserError, SemanticError with line/column
- **Rationale**: Precise error reporting
- **Trade-off**: More exception classes, but clearer error categorization

### Testing Strategy

#### Decision 15: TDD Approach
- **Choice**: Test-first development
- **Rationale**: Robustness
- **Trade-off**: More upfront time, but fewer bugs

#### Decision 16: Test Coverage Goals
- **Choice**: 200+ tests covering all 18 gap categories
- **Rationale**: Production-grade robustness
- **Trade-off**: Longer test suite execution time

### Performance Considerations

#### Decision 17: Time Complexity
- **Lexer**: O(n) single-pass
- **Parser**: O(n) single-pass
- **Interpreter**: O(n) tree traversal
- **Symbol Table Lookup**: O(s) where s = scope depth

#### Decision 18: Memory Management
- **Choice**: Python garbage collection
- **Rationale**: Simplicity for educational project
- **Trade-off**: Less control than manual memory management

## Known Limitations

### Limitation 1: Recursion Depth for Deep ASTs

**Issue**: Python's default recursion limit (~1000 frames) is exceeded by deeply nested expression trees (e.g., 1000-term addition chain).

**Root Cause**: Recursive visitor pattern (`visit_binary_op` calls itself for each nested BinaryOp node).

**Impact**: Programs with deeply nested expressions (>500 levels) may fail with `RecursionError`.

**Mitigation Strategies**:
1. **Increase recursion limit**: `sys.setrecursionlimit(3000)` (used in stress tests)
2. **Iterative evaluation**: Replace recursive visitor with stack-based evaluation (complex, not implemented)
3. **Expression flattening**: Optimize AST during parsing to reduce depth (not implemented)

**Trade-off Analysis**:
- **Choice**: Recursive visitor pattern for educational clarity
- **Benefit**: Clear separation of traversal logic, easy to understand (Week 13)
- **Cost**: Recursion depth limitation
- **Alternative**: Iterative traversal (more complex, less educational value)

**Production Systems**: JVM, CPython use stack-based evaluation or increase recursion limits for interpreter loops.

### Limitation 2: No Loop Constructs

**Issue**: C-Lite does not support `while` or `for` loops (Project Spec §3).

**Impact**: Cannot express iterative algorithms directly.

**Future Extension**: Add loop constructs with proper termination analysis (Week 6: Control Structures).

### Limitation 3: No Error Recovery

**Issue**: Parser uses fail-fast strategy (stops on first error).

**Impact**: Only first syntax error reported per compilation.

**Trade-off**: Simpler implementation vs. better user experience.

## References
- Sebesta, R.W. - Concepts of Programming Languages (12th Edition)
- Scott, M.L. - Programming Language Pragmatics (4th Edition)