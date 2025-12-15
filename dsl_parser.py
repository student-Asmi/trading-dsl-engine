from lark import Lark

dsl_grammar = r"""
    start: entry exit?

    entry: "ENTRY:" expr
    exit: "EXIT:" expr

    // -----------------------------
    // Boolean expressions
    // Precedence: parentheses > comparison/cross > AND > OR
    // -----------------------------
    ?expr: expr "OR" expr   -> or_op
         | expr "AND" expr  -> and_op
         | "(" expr ")"     -> group
         | condition

    // -----------------------------
    // Conditions (comparison or cross events)
    // -----------------------------
    ?condition: comparison
              | cross_above
              | cross_below

    // -----------------------------
    // Comparisons
    // -----------------------------
    comparison: operand OP operand

    // -----------------------------
    // Operands: indicator, series, constant
    // -----------------------------
    ?operand: indicator
            | series
            | NUMBER

    // -----------------------------
    // Cross events
    // -----------------------------
    cross_above: series "crosses_above" series
    cross_below: series "crosses_below" series

    // -----------------------------
    // Series like: close, high, low, volume, close[1]
    // -----------------------------
    series: CNAME ("[" NUMBER "]")?

    // -----------------------------
    // Indicators like SMA(close,20), RSI(close,14)
    // -----------------------------
    indicator: CNAME "(" operand "," NUMBER ")"

    // -----------------------------
    // Operators
    // -----------------------------
    OP: ">" | "<" | ">=" | "<=" | "=="

    %import common.CNAME
    %import common.NUMBER
    %import common.WS
    %ignore WS
"""

# Important: use LALR (fast + safe)
dsl_parser = Lark(dsl_grammar, start="start", parser="lalr")
