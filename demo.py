import pandas as pd

# -----------------------------------------
# IMPORTING MODULES FROM PROJECT FILES
# -----------------------------------------
from nl_parser import nl_to_json_rules
from dsl_parser import dsl_parser
from ast_builder import DSLtoAST
from code_generator import generate_python_expr
from indicators import SMA, RSI
from backtest import backtest_signals


# ---------------------------------------------------
# JSON → DSL (Improved converter)
# ---------------------------------------------------
def json_to_dsl(json_rules):
    def convert_rule(r):
        left = r["left"]
        op = r["operator"]
        right = r["right"]
        return f"{left} {op} {right}"

    entry_rules = [convert_rule(r) for r in json_rules["entry"]]
    exit_rules = [convert_rule(r) for r in json_rules["exit"]]

    dsl = ""
    if entry_rules:
        dsl += "ENTRY: " + " AND ".join(entry_rules) + "\n"
    if exit_rules:
        dsl += "EXIT: " + " AND ".join(exit_rules)

    return dsl.strip()


# ---------------------------------------------------
# DSL → AST
# ---------------------------------------------------
def parse_dsl_to_ast(dsl_text):
    tree = dsl_parser.parse(dsl_text)
    transformer = DSLtoAST()
    parsed = transformer.transform(tree)

    final_ast = {"entry": [], "exit": []}

    for node in parsed:
        if isinstance(node, tuple):
            section, ast = node
            final_ast[section].append(ast)

    return final_ast


# ---------------------------------------------------
# AST → Signals (safe eval)
# ---------------------------------------------------
def ast_to_signals(df, ast):
    signals = pd.DataFrame(index=df.index)
    signals["entry"] = False
    signals["exit"] = False

    env = {
        "df": df,
        "SMA": SMA,
        "RSI": RSI,
        "pd": pd
    }

    # ENTRY
    if ast["entry"]:
        expr = generate_python_expr(ast["entry"][0])
        signals["entry"] = eval(expr, env)

    # EXIT
    if ast["exit"]:
        expr = generate_python_expr(ast["exit"][0])
        signals["exit"] = eval(expr, env)

    return signals.fillna(False)


# ---------------------------------------------------
# END-TO-END PIPELINE
# ---------------------------------------------------
def run_pipeline(entry_nl, exit_nl, df):
    print("\n========================")
    print("1. NL → JSON")
    print("========================")
    entry_json = nl_to_json_rules(entry_nl)
    exit_json = nl_to_json_rules(exit_nl)

    combined_json = {
        "entry": entry_json["entry"],
        "exit": exit_json["exit"]
    }
    print(combined_json)

    print("\n========================")
    print("2. JSON → DSL")
    print("========================")
    dsl = json_to_dsl(combined_json)
    print(dsl)

    print("\n========================")
    print("3. DSL → AST")
    print("========================")
    ast = parse_dsl_to_ast(dsl)
    print(ast)

    print("\n========================")
    print("4. AST → Signals")
    print("========================")
    signals = ast_to_signals(df, ast)
    print(signals.head())

    print("\n========================")
    print("5. Backtest")
    print("========================")
    result = backtest_signals(df, signals)

    print("\nFinal Backtest Result")
    print("Total Return (%) =", result["total_return_pct"])
    print("Max Drawdown (%) =", result["max_drawdown_pct"])
    print("Number of Trades =", result["num_trades"])

    print("\nTrades Log:")
    for t in result["trades"]:
        print(t)

    return result
