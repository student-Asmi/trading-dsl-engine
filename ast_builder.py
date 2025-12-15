from lark import Transformer

class DSLtoAST(Transformer):

    # ----------------------------
    # ENTRY / EXIT
    # ----------------------------
    def entry(self, items):
        return ("entry", items[0])

    def exit(self, items):
        return ("exit", items[0])

    # ----------------------------
    # Boolean operations
    # ----------------------------
    def and_op(self, items):
        return {
            "type": "and",
            "left": items[0],
            "right": items[1],
        }

    def or_op(self, items):
        return {
            "type": "or",
            "left": items[0],
            "right": items[1],
        }

    def group(self, items):
        # Just return the inner expression
        return items[0]

    # ----------------------------
    # Comparisons
    # ----------------------------
    def comparison(self, items):
        return {
            "type": "comparison",
            "left": items[0],
            "operator": items[1].value,
            "right": items[2],
        }

    # ----------------------------
    # Cross events
    # ----------------------------
    def cross_above(self, items):
        return {
            "type": "cross",
            "direction": "above",
            "left": items[0],
            "right": items[1],
        }

    def cross_below(self, items):
        return {
            "type": "cross",
            "direction": "below",
            "left": items[0],
            "right": items[1],
        }

    # ----------------------------
    # Series like close, volume, close[1]
    # ----------------------------
    def series(self, items):
        # items = [name] or [name, index]
        name = items[0].value
        if len(items) == 2:
            return {"type": "series", "name": name, "index": int(items[1])}
        return {"type": "series", "name": name, "index": None}

    # ----------------------------
    # Indicators like SMA(close,20)
    # ----------------------------
    def indicator(self, items):
        return {
            "type": "indicator",
            "name": items[0].value.lower(),  # sma, rsi
            "series": items[1],              # structured series node
            "period": int(items[2]),
        }


# ----------------------------
# Final AST wrapper
# ----------------------------
def build_final_ast(tree):
    """
    Input from parser transform:
        [
            ("entry", AST_Node),
            ("exit", AST_Node)
        ]

    Output:
        {
            "entry": [...],
            "exit": [...]
        }
    """
    final_ast = {"entry": [], "exit": []}

    for section, ast in tree:
        if section == "entry":
            final_ast["entry"].append(ast)
        elif section == "exit":
            final_ast["exit"].append(ast)

    return final_ast
