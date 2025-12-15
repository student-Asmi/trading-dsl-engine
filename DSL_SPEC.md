
📄 DSL_SPEC.md — Trading Strategy DSL Specification
1. Overview

This Domain-Specific Language (DSL) provides a concise, unambiguous syntax for specifying rule-based trading strategies.
The DSL supports:

Entry and Exit rule blocks

Boolean logic

Comparisons

Cross events

Indicators

Lookbacks

Numeric expressions

It is designed to be:

Human-readable

Easy to parse using Lark (LALR mode)

Mappable to executable Python/Pandas expressions

2. DSL Structure

A DSL script contains two optional sections:

ENTRY: <expression>
EXIT: <expression>


Both blocks accept complete boolean expressions and may include nested logic, indicators, and cross events.

Examples:

ENTRY: close > SMA(close,20) AND volume > 1000000
EXIT: RSI(close,14) < 30

ENTRY: (close > open) OR (close crosses_above SMA(close,50))
EXIT: close < low[1]

3. Expressions & Grammar
Expression Types

An expression can consist of:

Comparison

Cross events

Nested expressions

Boolean combinations

4. Grammar Definition (Lark-compatible)
start: entry exit?

entry: "ENTRY:" expr
exit:  "EXIT:" expr

?expr: expr "OR" expr      -> or_op
     | expr "AND" expr     -> and_op
     | "(" expr ")"        -> group
     | condition

?condition: comparison
          | cross_above
          | cross_below

comparison: operand OP operand

?operand: indicator
        | series
        | NUMBER

cross_above: series "crosses_above" series
cross_below: series "crosses_below" series

series: CNAME ("[" NUMBER "]")?

indicator: CNAME "(" operand "," NUMBER ")"

OP: ">" | "<" | ">=" | "<=" | "=="

%import common.CNAME
%import common.NUMBER
%import common.WS
%ignore WS

5. Language Elements
5.1 Series

Represents a data column (OHLCV) with optional lookback.

Examples:

close
open
volume
high[1]
low[5]


Equivalent Python:

df["close"]
df["high"].shift(1)

5.2 Indicators

Supported indicators:

SMA(series, period)

Simple Moving Average.

Example:

SMA(close, 20)


Equivalent Python:

df['close'].rolling(20).mean()

RSI(series, period)

Relative Strength Index.

Example:

RSI(close, 14)


Equivalent Python:

RSI(df['close'], 14)

5.3 Comparison Operators
>, <, >=, <=, ==


Example:

close > SMA(close,20)
volume == 1000000

5.4 Boolean Logic
AND, OR


Examples:

close > open AND volume > 100000
(close > open) OR (RSI(close,14) < 30)

5.5 Cross Events

Represent momentum-based crossover conditions.

crosses_above

Triggered when a series moves from below another series to above.

Example:

close crosses_above SMA(close,20)


Python equivalent:

(df['close'].shift(1) < df['sma20'].shift(1)) &
(df['close'] >= df['sma20'])

crosses_below

Opposite event.

6. Operator Precedence

Highest → Lowest:

Parentheses

Comparison / Cross events

AND

OR

Example:

close > open AND volume > 1_000_000 OR RSI(close,14) < 30


Interpreted as:

((close > open) AND (volume > 1_000_000)) OR (RSI(close,14) < 30)

7. AST Output Format

The parsed AST follows a consistent structure.

Examples:

Comparison Node
{
  "type": "comparison",
  "left": {"type": "series", "name": "close"},
  "operator": ">",
  "right": {"type": "indicator", "name": "sma", "series": {...}, "period": 20}
}

Boolean Node
{
  "type": "and",
  "left": {...},
  "right": {...}
}

Cross Event Node
{
  "type": "cross",
  "direction": "above",
  "left": {"type": "series", "name": "close"},
  "right": {"type": "indicator", ...}
}

8. Design Decisions

Grammar kept minimal but extendable

Indicators follow TradingView-style notation

Boolean precedence ensures safe parsing

Series + lookback format is simple and expressive

Cross events modeled explicitly for correct backtesting behavior

9. Limitations (Intentional)

No arithmetic (e.g., close + 5 not supported)

No multi-line rules

No NOT operator

Indicators limited to SMA + RSI

10. Future Extensions

Support NOT / XOR

Add arithmetic expressions

Support STOP-LOSS / TAKE-PROFIT keywords

Add EMA, MACD, ATR indicators

Multi-timeframe rules

11. Summary

This DSL provides a clean, readable, and fully parsable structure for expressing algorithmic trading rules.
It is optimized for:

NL → DSL mapping

Reliable parsing

Code generation

Backtesting

This file serves as the formal specification of the language.
