import re

# ---------------------------------------------
# BASIC HELPERS
# ---------------------------------------------
def normalize_text(text):
    return re.sub(r"\s+", " ", text.lower()).strip()

def extract_numbers(text):
    text = text.lower()
    nums = re.findall(r"\d+", text)
    nums = [int(n) for n in nums] if nums else []

    if "million" in text and nums:
        nums = [nums[0] * 1_000_000]
    if "thousand" in text and nums:
        nums = [nums[0] * 1000]

    return nums


# ---------------------------------------------
# CROSS CONDITION (price crosses above yesterday’s high)
# ---------------------------------------------
def parse_cross_condition(sentence):
    s = normalize_text(sentence)

    if "crosses above" in s or "cross above" in s:
        left = "close"

        if "yesterday" in s and "high" in s:
            right = "high[1]"
        elif "yesterday" in s and "low" in s:
            right = "low[1]"
        else:
            right = None

        if right:
            return {"left": left, "operator": "crosses_above", "right": right}

    return None


# ---------------------------------------------
# PERCENT INCREASE COMPARED TO LAST WEEK
# "volume increases by more than 30 percent compared to last week"
# ---------------------------------------------
def parse_percent_last_week(sentence):
    s = normalize_text(sentence)

    if "percent" in s and ("increase" in s or "increases" in s):
        nums = re.findall(r"\d+", s)
        if not nums:
            return None

        percent = int(nums[0])

        if "volume" not in s:
            return None

        if "last week" in s:
            base = "volume[7]"
        else:
            return None

        multiplier = 1 + (percent / 100)
        right = f"{base} * {multiplier}"

        return {"left": "volume", "operator": ">", "right": right}

    return None


# ---------------------------------------------
# MAIN CONDITION HANDLER
# ---------------------------------------------
def parse_one_condition(sentence):
    s = normalize_text(sentence)

    # 1) Percent change rule
    rule = parse_percent_last_week(sentence)
    if rule:
        return rule

    # 2) Cross condition
    rule = parse_cross_condition(sentence)
    if rule:
        return rule

    # 3) RSI rule
    if "rsi" in s:
        nums = re.findall(r"\d+", s)
        period = int(nums[0]) if nums else 14
        threshold = int(nums[-1]) if len(nums) >= 2 else 30

        op = "<" if "below" in s else ">" if "above" in s else None

        return {"left": f"rsi(close,{period})", "operator": op, "right": threshold}

    # 4) Basic comparisons (close, volume, SMA)
    left = None
    op = None
    right = None

    if "close" in s or "price" in s:
        left = "close"
    elif "volume" in s:
        left = "volume"

    if "above" in s:
        op = ">"
    elif "below" in s:
        op = "<"
    elif "equal" in s:
        op = "=="

    if "moving average" in s or "ma" in s:
        nums = extract_numbers(s)
        period = nums[0] if nums else 20
        right = f"sma({left},{period})"

    if right is None:
        nums = extract_numbers(s)
        if nums:
            right = nums[0]

    if left and op and right is not None:
        return {"left": left, "operator": op, "right": right}

    return None


# ---------------------------------------------
# ENTRY POINT: NL → JSON RULES
# ---------------------------------------------
def nl_to_json_rules(text):
    t = normalize_text(text)

    is_entry = any(x in t for x in ["buy", "enter", "trigger entry"])
    is_exit = any(x in t for x in ["exit", "sell"])

    entry_rules = []
    exit_rules = []

    parts = re.split(r"\band\b", t)

    for part in parts:
        rule = parse_one_condition(part)
        if rule:
            if is_exit:
                exit_rules.append(rule)
            else:
                entry_rules.append(rule)

    return {"entry": entry_rules, "exit": exit_rules}
