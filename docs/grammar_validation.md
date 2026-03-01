###### Example 1: Basic Variable Declaration & Assignment

```
int x;
float y;
x = 5;
y = 3.14;
```
```
program
├── declaration (int x)
├── declaration (float y)
├── assignment (x = 5)
└── assignment (y = 3.14)
```

***

###### Example 2: Complex Expression with Precedence

```
int result;
result = (3 + 4) * 5 - 2 / 2;
```
```
assignment
└── expression
    └── additive_expression
        ├── multiplicative_expression: (3 + 4) * 5
        │   ├── primary: (3 + 4)
        │   │   └── additive: 3 + 4
        │   └── * 
        │   └── primary: 5
        ├── -
        └── multiplicative_expression: 2 / 2
```

***

###### Example 3: Edge Case - Empty Block

```
if (x > 0) {
    ;
}
```

Validation: block = "{" { statement } "}" allows zero statements
Valid: Empty statements are explicitly supported

***

###### Example 4: Invalid Program (Should Be Rejected)

```
x = 10;  // Error: x not declared
int x;
```

Validation: Grammar allows this syntax, but semantic analysis will catch it
Grammar validates syntax only; semantics handled later

***

###### Example 5: Nested If-Else with Block Scope

```
int a = 10;
if (a > 5) {
    float b = 3.14;
    printf(b);
} else {
    printf(a);
}
```

Validation:
if_statement → if ( expression ) statement [ else statement ]
block → { { statement } } creates nested scope for b
printf_call → printf ( expression ) ;
Valid: 
Demonstrates scoping rules