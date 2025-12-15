from lark.lexer import Token

# ============================================================
# Convert AST Node → Pandas Expression String
# ============================================================
def generate_python_expr(node):
    """Convert AST node into a valid pandas-evaluable expression string."""

    # ---------------------------------------------------
    # 1. COMPARISON NODE
    # ---------------------------------------------------
    if node["type"] == "comparison":
        left = node["left"]
        op = node["operator"]
        right = node["right"]

        # Token → int
        if isinstance(right, Token) and right.type == "NUMBER":
            right = int(right.value)

        # LEFT SIDE
        if isinstance(left, dict) and left.get("type") == "indicator":
            left_expr = generate_python_expr(left)

        elif isinstance(left, str):
            if "[" in left:        # e.g. volume[7]
                col, lag = left.split("[")
                lag = lag.replace("]", "")
                left_expr = f"df['{col}'].shift({lag})"
            else:
                left_expr = f"df['{left}']"

        else:
            raise ValueError("Unsupported left operand:", left)

        # RIGHT SIDE
        if isinstance(right, (int, float)):
            right_expr = str(right)

        elif isinstance(right, str):
            if "[" in right:        # e.g. high[1]
                col, lag = right.split("[")
                lag = lag.replace("]", "")
                right_expr = f"df['{col}'].shift({lag})"
            else:
                right_expr = f"df['{right}']"

        elif isinstance(right, dict) and right.get("type") == "indicator":
            right_expr = generate_python_expr(right)

        else:
            raise ValueError("Unsupported right operand:", right)

        return f"({left_expr} {op} {right_expr})"

    # ---------------------------------------------------
    # 2. INDICATOR NODE (SMA, RSI)
    # ---------------------------------------------------
    if node["type"] == "indicator":
        name = node["name"].upper()
        series = node["series"]
        period = node["period"]

        if isinstance(series, dict):   # nested indicator
            series_expr = generate_python_expr(series)

        elif "[" in series:            # e.g. close[5]
            col, lag = series.split("[")
            lag = lag.replace("]", "")
            series_expr = f"df['{col}'].shift({lag})"

        else:
            series_expr = f"df['{series}']"

        return f"{name}({series_expr}, {period})"

    # ---------------------------------------------------
    # 3. CROSS EVENTS (crosses_above / crosses_below)
    # ---------------------------------------------------
    if node["type"] == "cross":
        left = node["left"]
        right = node["right"]

        # Left side
        if isinstance(left, dict):
            left_now = generate_python_expr(left)
            left_prev = f"({left_now}).shift(1)"
        else:
            left_now = f"df['{left}']"
            left_prev = f"df['{left}'].shift(1)"

        # Right side
        if "[" in right:           # high[1]
            col, lag = right.split("[")
            lag = int(lag.replace("]", ""))
            right_now = f"df['{col}'].shift({lag})"
            right_prev = f"df['{col}'].shift({lag+1})"

        else:
            right_now = f"df['{right}']"
            right_prev = f"df['{right}'].shift(1)"

        # CROSS ABOVE
        if node["direction"] == "above":
            return (
                f"((({left_prev}) <= ({right_prev})) "
                f"& (({left_now}) > ({right_now})))"
            )

        # CROSS BELOW
        if node["direction"] == "below":
            return (
                f"((({left_prev}) >= ({right_prev})) "
                f"& (({left_now}) < ({right_now})))"
            )

    # ---------------------------------------------------
    # 4. LOGICAL OPERATORS
    # ---------------------------------------------------
    if node["type"] == "and":
        return f"({generate_python_expr(node['left'])} & {generate_python_expr(node['right'])})"

    if node["type"] == "or":
        return f"({generate_python_expr(node['left'])} | {generate_python_expr(node['right'])})"

    # ---------------------------------------------------
    # UNKNOWN NODE
    # ---------------------------------------------------
    raise ValueError("Unknown AST node:", node)


# ============================================================
# Convert Full AST → Python Function Code
# ============================================================
def ast_to_python_code(final_ast):
    entry_expr = ""
    exit_expr = ""

    if final_ast["entry"]:
        entry_expr = generate_python_expr(final_ast["entry"][0])
    if final_ast["exit"]:
        exit_expr = generate_python_expr(final_ast["exit"][0])

    code = f"""
def run_strategy(df):
    import pandas as pd

    signals = pd.DataFrame(index=df.index)
    signals['entry'] = {entry_expr}
    signals['exit'] = {exit_expr}

    return signals
"""
    return code
