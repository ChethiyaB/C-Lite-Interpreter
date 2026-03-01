"""
Recursive Descent Parser for C-Lite.
Implements LL(1) parsing per EBNF grammar specification.
"""

from typing import List, Optional, Any
from .token import Token, TokenType
from .lexer import Lexer
from .ast import (
    ASTNode,
    Program, Declaration, Assignment, IfStatement, Block, PrintfCall, EmptyStatement,
    BinaryOp, UnaryOp, NumberLiteral, Identifier
)
from .errors import ParserError


class Parser:
    """
    Recursive Descent Parser for C-Lite.
    Consumes tokens from Lexer and produces AST.
    
    Theory: Implements LL(1) parsing strategy (Week 3)
    - Top-down parsing without backtracking
    - One token lookahead for decision making
    - Grammar must be LL(1) compatible (no left-recursion)
    
    CO523 Alignment:
    - Week 2: Syntax and Semantics (BNF/EBNF, Parse Trees)
    - Week 3: Lexical and Syntax Analysis (Parsers)
    - Project Spec §4.2: Syntax Analysis
    """
    
    def __init__(self, tokens: List[Token]):
        """
        Initialize parser with token stream.
        
        Args:
            tokens: List of Token objects from Lexer
        """
        self.tokens = tokens
        self.position = 0
        self.current_token: Optional[Token] = None
        
        # Initialize current token
        if self.tokens:
            self.current_token = self.tokens[0]
        else:
            # Empty program - create EOF token
            self.current_token = Token(
                type=TokenType.EOF,
                value=None,
                line=1,
                column=1
            )

    # ==================== Token Navigation ====================
    
    def advance(self) -> None:
        """
        Move to the next token in the stream.
        Updates current_token for lookahead.
        """
        if self.position < len(self.tokens) - 1:
            self.position += 1
            self.current_token = self.tokens[self.position]
        else:
            self.position = len(self.tokens) - 1
            self.current_token = self.tokens[-1]

    def peek(self, offset: int = 0) -> Optional[Token]:
        """
        Look ahead at token without advancing.
        
        Args:
            offset: Number of tokens to look ahead (0 = current)
        
        Returns:
            Token at position + offset, or None if out of bounds
        """
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def match(self, *types: TokenType) -> bool:
        """
        Check if current token matches any of the given types.
        
        Args:
            *types: Variable number of TokenType values to match
        
        Returns:
            True if current token type matches any argument
        """
        if self.current_token is None:
            return False
        return self.current_token.type in types

    def expect(self, token_type: TokenType, message: str = None) -> Token:
        """
        Expect current token to be of specific type, or raise error.
        
        Args:
            token_type: Expected TokenType
            message: Custom error message (optional)
        
        Returns:
            Current token if match succeeds
        
        Raises:
            ParserError: If token type doesn't match
        """
        if self.current_token is None:
            raise ParserError(
                message or f"Expected {token_type.value} but found end of file",
                line=self.current_token.line if self.current_token else 1,
                column=self.current_token.column if self.current_token else 1
            )
        
        if self.current_token.type != token_type:
            raise ParserError(
                message or f"Expected {token_type.value} but found '{self.current_token.value}'",
                line=self.current_token.line,
                column=self.current_token.column
            )
        
        token = self.current_token
        self.advance()
        return token

    # ==================== Main Entry Point ====================
    
    def parse(self) -> Program:
        """
        Parse entire program and return AST root.
        
        Returns:
            Program node (root of AST)
        
        Raises:
            ParserError: If syntax error encountered
        """
        return self._parse_program()

    # ==================== Grammar Productions ====================
    # Following EBNF from docs/grammar.ebnf
    
    def _parse_program(self) -> Program:
        """
        Parse program: { declaration | statement }
        
        EBNF: program = { declaration | statement } ;
        
        Returns:
            Program AST node
        """
        declarations = []
        statements = []
        
        while not self.match(TokenType.EOF):
            # Determine if this is a declaration or statement
            if self.match(TokenType.INT, TokenType.FLOAT):
                declarations.append(self._parse_declaration())
            else:
                statements.append(self._parse_statement())
        
        return Program(
            declarations=declarations,
            statements=statements
        )

    def _parse_declaration(self) -> Declaration:
        """
        Parse declaration: type_specifier identifier ";"
        
        EBNF: declaration = type_specifier identifier ";" ;
              type_specifier = "int" | "float" ;
        
        Returns:
            Declaration AST node
        
        Raises:
            ParserError: If declaration syntax is invalid
        """
        # Parse type specifier
        if self.match(TokenType.INT):
            type_token = self.expect(TokenType.INT, "Expected 'int' or 'float'")
            var_type = 'int'
        elif self.match(TokenType.FLOAT):
            type_token = self.expect(TokenType.FLOAT, "Expected 'int' or 'float'")
            var_type = 'float'
        else:
            raise ParserError(
                f"Expected type specifier (int/float) but found '{self.current_token.value}'",
                line=self.current_token.line,
                column=self.current_token.column
            )
        
        # Parse identifier
        if not self.match(TokenType.IDENTIFIER):
            raise ParserError(
                f"Expected identifier after type specifier",
                line=self.current_token.line,
                column=self.current_token.column
            )
        
        name_token = self.expect(TokenType.IDENTIFIER)
        
        # Parse semicolon
        self.expect(TokenType.SEMICOLON, "Expected ';' after variable declaration")
        
        return Declaration(
            var_type=var_type,
            name=name_token.value,
            line=type_token.line,
            column=type_token.column
        )

    def _parse_statement(self) -> ASTNode:
        """
        Parse statement: assignment | if_statement | printf_call | block | ";"
        
        EBNF: statement = assignment
                    | if_statement
                    | printf_call
                    | block
                    | ";" ;
        
        Returns:
            Statement AST node (Assignment, IfStatement, Block, PrintfCall, or EmptyStatement)
        
        Raises:
            ParserError: If statement syntax is invalid
        """
        if self.match(TokenType.IDENTIFIER):
            return self._parse_assignment()
        elif self.match(TokenType.IF):
            return self._parse_if_statement()
        elif self.match(TokenType.PRINTF):
            return self._parse_printf_call()
        elif self.match(TokenType.LBRACE):
            return self._parse_block()
        elif self.match(TokenType.SEMICOLON):
            # Empty statement: ;
            token = self.expect(TokenType.SEMICOLON)
            return EmptyStatement(line=token.line, column=token.column)
        else:
            raise ParserError(
                f"Expected statement but found '{self.current_token.value}'",
                line=self.current_token.line,
                column=self.current_token.column
            )

    def _parse_assignment(self) -> Assignment:
        """
        Parse assignment: identifier "=" expression ";"
        
        EBNF: assignment = identifier "=" expression ";" ;
        
        Returns:
            Assignment AST node
        
        Raises:
            ParserError: If assignment syntax is invalid
        """
        if not self.match(TokenType.IDENTIFIER):
            raise ParserError(
                "Expected identifier for assignment",
                line=self.current_token.line,
                column=self.current_token.column
            )
        
        name_token = self.expect(TokenType.IDENTIFIER)
        
        # Expect assignment operator
        self.expect(TokenType.ASSIGN, "Expected '=' in assignment")
        
        # Parse expression
        value = self._parse_expression()
        
        # Expect semicolon
        self.expect(TokenType.SEMICOLON, "Expected ';' after assignment")
        
        return Assignment(
            name=name_token.value,
            value=value,
            line=name_token.line,
            column=name_token.column
        )

    def _parse_if_statement(self) -> IfStatement:
        """
        Parse if_statement: "if" "(" expression ")" statement [ "else" statement ]
        
        EBNF: if_statement = "if" "(" expression ")" statement
                            [ "else" statement ] ;
        
        Note: Dangling else resolved by binding to nearest if (standard C behavior)
        
        Returns:
            IfStatement AST node
        
        Raises:
            ParserError: If if-statement syntax is invalid
        """
        if_token = self.expect(TokenType.IF)
        
        # Expect opening parenthesis
        self.expect(TokenType.LPAREN, "Expected '(' after 'if'")
        
        # Parse condition expression
        condition = self._parse_expression()
        
        # Expect closing parenthesis
        self.expect(TokenType.RPAREN, "Expected ')' after condition")
        
        # Parse then-branch statement
        then_branch = self._parse_statement()
        
        # Check for optional else clause
        else_branch = None
        if self.match(TokenType.ELSE):
            self.advance()  # Consume 'else'
            else_branch = self._parse_statement()
        
        return IfStatement(
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch,
            line=if_token.line,
            column=if_token.column
        )
    
    def _parse_block(self) -> Block:
        """
        Parse block: "{" { declaration | statement } "}"
        EBNF: block = "{" { declaration | statement } "}" ;
        
        Returns:
            Block AST node
        
        Raises:
            ParserError: If block syntax is invalid
        """
        brace_token = self.expect(TokenType.LBRACE)
        
        statements = []
        while not self.match(TokenType.RBRACE, TokenType.EOF):
            # FIX: Check for declarations inside blocks
            if self.match(TokenType.INT, TokenType.FLOAT):
                statements.append(self._parse_declaration())
            else:
                statements.append(self._parse_statement())
        
        # Expect closing brace
        self.expect(TokenType.RBRACE, "Expected '}' to close block")
        
        return Block(
            statements=statements,
            line=brace_token.line,
            column=brace_token.column
        )
    
    def _parse_printf_call(self) -> PrintfCall:
        """
        Parse printf_call: "printf" "(" expression ")" ";"
        
        EBNF: printf_call = "printf" "(" expression ")" ";" ;
        
        Returns:
            PrintfCall AST node
        
        Raises:
            ParserError: If printf syntax is invalid
        """
        printf_token = self.expect(TokenType.PRINTF)
        
        # Expect opening parenthesis
        self.expect(TokenType.LPAREN, "Expected '(' after 'printf'")
        
        # Parse argument expression
        argument = self._parse_expression()
        
        # Expect closing parenthesis
        self.expect(TokenType.RPAREN, "Expected ')' after printf argument")
        
        # Expect semicolon
        self.expect(TokenType.SEMICOLON, "Expected ';' after printf call")
        
        return PrintfCall(
            argument=argument,
            line=printf_token.line,
            column=printf_token.column
        )

    # ==================== Expression Parsing ====================
    # Implements operator precedence hierarchy (Week 3)
    
    def _parse_expression(self) -> ASTNode:
        """
        Parse expression: relational_expression
        
        EBNF: expression = relational_expression ;
        
        Returns:
            Expression AST node
        """
        return self._parse_relational_expression()

    def _parse_relational_expression(self) -> ASTNode:
        """
        Parse relational_expression: additive_expression { ( ">" | "<" | "==" ) additive_expression }
        
        EBNF: relational_expression = additive_expression 
                                    [ ( ">" | "<" | "==" ) additive_expression ] ;
        
       Support chaining with left-associativity (like additive expressions)
        
        Precedence Level 4 (lowest in expressions)
        
        Returns:
            Expression AST node (BinaryOp for relational, or lower-level expression)
        """
        left = self._parse_additive_expression()
        
        # Support chaining: a < b == c parses as ((a < b) == c)
        while self.match(TokenType.GT, TokenType.LT, TokenType.EQ):
            op_token = self.current_token
            self.advance()
            right = self._parse_additive_expression()
            
            left = BinaryOp(
                left=left,
                operator=op_token.value,
                right=right,
                line=op_token.line,
                column=op_token.column
            )
        
        return left

    def _parse_additive_expression(self) -> ASTNode:
        """
        Parse additive_expression: multiplicative_expression { ( "+" | "-" ) multiplicative_expression }
        
        EBNF: additive_expression = multiplicative_expression 
                                  { ( "+" | "-" ) multiplicative_expression } ;
        
        Precedence Level 3
        
        Note: Left-associative via loop (not recursion)
        
        Returns:
            Expression AST node
        """
        left = self._parse_multiplicative_expression()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op_token = self.current_token
            self.advance()
            right = self._parse_multiplicative_expression()
            
            left = BinaryOp(
                left=left,
                operator=op_token.value,
                right=right,
                line=op_token.line,
                column=op_token.column
            )
        
        return left

    def _parse_multiplicative_expression(self) -> ASTNode:
        """
        Parse multiplicative_expression: primary_expression { ( "*" | "/" ) primary_expression }
        
        EBNF: multiplicative_expression = primary_expression 
                                        { ( "*" | "/" ) primary_expression } ;
        
        Precedence Level 2
        
        Note: Left-associative via loop
        
        Returns:
            Expression AST node
        """
        left = self._parse_primary_expression()
        
        while self.match(TokenType.STAR, TokenType.SLASH):
            op_token = self.current_token
            self.advance()
            right = self._parse_primary_expression()
            
            left = BinaryOp(
                left=left,
                operator=op_token.value,
                right=right,
                line=op_token.line,
                column=op_token.column
            )
        
        return left

    def _parse_primary_expression(self) -> ASTNode:
        """
        Parse primary_expression: number | identifier | "(" expression ")" | unary_expression
        
        EBNF: primary_expression = number
                               | identifier
                               | "(" expression ")"
                               | unary_expression ;
        
        Precedence Level 1 (highest)
        
        Returns:
            Primary expression AST node
        
        Raises:
            ParserError: If primary expression syntax is invalid
        """
        # Check for unary expression first
        if self.match(TokenType.PLUS, TokenType.MINUS):
            return self._parse_unary_expression()
        
        # Number literal
        if self.match(TokenType.INT_LITERAL, TokenType.FLOAT_LITERAL):
            token = self.current_token
            self.advance()
            return NumberLiteral(
                value=token.value,
                line=token.line,
                column=token.column
            )
        
        # Identifier
        if self.match(TokenType.IDENTIFIER):
            token = self.current_token
            self.advance()
            return Identifier(
                name=token.value,
                line=token.line,
                column=token.column
            )
        
        # Parenthesized expression
        if self.match(TokenType.LPAREN):
            self.advance()  # Consume '('
            expr = self._parse_expression()
            self.expect(TokenType.RPAREN, "Expected ')' to close expression")
            return expr
        
        # Error: no valid primary expression
        raise ParserError(
            f"Expected expression but found '{self.current_token.value}'",
            line=self.current_token.line,
            column=self.current_token.column
        )

    def _parse_unary_expression(self) -> UnaryOp:
        """
        Parse unary_expression: ( "+" | "-" ) primary_expression
        
        EBNF: unary_expression = ( "+" | "-" ) primary_expression ;
        
        Returns:
            UnaryOp AST node
        
        Raises:
            ParserError: If unary expression syntax is invalid
        """
        op_token = self.current_token
        self.advance()
        
        operand = self._parse_primary_expression()
        
        return UnaryOp(
            operator=op_token.value,
            operand=operand,
            line=op_token.line,
            column=op_token.column
        )