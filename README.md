# 🔥 **Natural Language → DSL → AST → Python Strategy Engine**  
### **A Mini Research-Engineering Pipeline for Rule-Based Trading Logic**

This project implements a **complete end-to-end compiler-style pipeline** that converts natural-language trading rules into a **domain-specific language (DSL)**, parses them into an **AST**, generates **executable Python code**, evaluates signals, and finally runs a **simple backtest engine**.

The assignment demonstrates skills in:

- **DSL design**  
- **Natural-language rule parsing**  
- **AST construction**  
- **Code generation**  
- **Time-series simulation**  
- **Modular system architecture**

---

## 📌 **PIPELINE OVERVIEW**
Natural Language
→ NL → JSON Rule Parser
→ Custom Trading DSL
→ DSL Parser (Lark)
→ AST (Abstract Syntax Tree)
→ Python Expression Generator
→ Signal Evaluation (Pandas)
→ Backtest Engine
→ Final Metrics + Trades Log

This mirrors a **real compiler architecture** applied to financial rule execution.

---

## 🧠 **EXAMPLE END-TO-END FLOW**

### **Input (Natural Language)**

**Entry:** “Buy when the close price is above the 20-day moving average and volume is above 1 million.”  
**Exit:** “Exit when RSI(14) is below 30.”

---

### **Generated DSL**
ENTRY: close > SMA(close,20) AND volume > 1000000
EXIT: RSI(close,14) < 30


---

### **AST (simplified)**

Entry → **AND**  
- left: close > SMA(close,20)  
- right: volume > 1000000  

Exit → **RSI(close,14) < 30**

---

### **Generated Python Expression**

```python
(df['close'] > SMA(df['close'],20)) & (df['volume'] > 1000000)

Backtest Output (example)

Total Return: 12.3%

Max Drawdown: –3.1%

Number of Trades: 4

Trades:

Buy 2023-01-02 @ 107

Sell 2023-01-08 @ 115

**💡 KEY FEATURES**
1. Natural Language Parsing

Handles:

price

moving averages

RSI

volume

percentage change

cross-above / cross-below events

**2. Custom Trading DSL**

Supports:

ENTRY / EXIT blocks

Boolean logic (AND, OR)

Parentheses

Comparison operators

Indicators (SMA, RSI)

Lookbacks (close[1])

Cross events

**3. AST Construction**

Built using Lark. Supports:

binary ops (and, or)

comparison nodes

series nodes

indicator nodes

cross events

**4. Automatic Code Generation**

Converts AST → Pandas expressions

Handles nested logic

Handles parentheses

Handles indicators

Handles cross events

**5. Backtest Engine**

Tracks:

entry/exit

P/L

total return

max drawdown

number of trades

***▶️ HOW TO RUN***
Step 1: Install dependencies
pip install -r requirements.txt

Step 2: Run the demo
python demo.py


This will:

Accept NL rules

Convert to DSL

Parse DSL to AST

Generate Python logic

Evaluate signals

Run backtest

Show performance metrics

📘 DSL SPECIFICATION

Full grammar and examples provided in DSL_SPEC.md.



***🎯 WHY THIS PROJECT STANDS OUT***

Designed like a real compiler pipeline

Clean modular architecture

Lark-based DSL grammar

AST-driven code execution

Fully automated signal engine

Very professional documentation

🛠️ FUTURE EXTENSIONS

Stop-loss / take-profit rules

Multi-timeframe support

ML-based signal blending

Strategy optimisation

GPU-accelerated backtests

⭐ AUTHOR

Assignment implementation by Asmi Verma
