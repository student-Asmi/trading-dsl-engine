import pandas as pd
import numpy as np

def backtest_signals(df, signals, initial_capital=100000.0, slippage=0.0, commission=0.0):
    """
    Simple backtesting engine that trades based on ENTRY and EXIT signals.
    
    Args:
        df (DataFrame): OHLCV data with columns ['open','high','low','close','volume']
        signals (DataFrame): Boolean DataFrame with columns ['entry','exit']
        initial_capital (float): Starting cash
        slippage (float): Per-share slippage
        commission (float): Fixed commission per trade

    Returns:
        dict with:
        - trades (list)
        - equity (Series)
        - final_capital
        - total_return_pct
        - max_drawdown_pct
        - num_trades
    """

    assert 'entry' in signals.columns, "signals must include 'entry'"
    assert 'exit' in signals.columns, "signals must include 'exit'"
    assert len(df) == len(signals), "df and signals must have same length"

    signals = signals.reindex(df.index)

    cash = float(initial_capital)
    position = 0.0  # number of shares (fractional allowed)
    entry_price = None

    trades = []
    equity_values = []
    equity_index = []

    idxs = list(df.index)
    n = len(idxs)

    for i, idx in enumerate(idxs):
        row = df.loc[idx]
        close_price = float(row["close"])

        # =============================================================
        # ENTRY
        # =============================================================
        if position == 0 and signals.loc[idx, "entry"]:
            if i + 1 < n:
                fill_idx = idxs[i+1]
                fill_price = float(df.loc[fill_idx]["open"])
            else:
                fill_idx = idx
                fill_price = close_price

            buy_price = fill_price + slippage
            shares = cash / buy_price if buy_price > 0 else 0

            if shares > 0:
                position = shares
                entry_price = buy_price
                cash -= commission  # commission on entry

                trades.append({
                    "entry_index": str(idx),
                    "entry_fill_index": str(fill_idx),
                    "entry_price": float(buy_price),
                    "exit_index": None,
                    "exit_fill_index": None,
                    "exit_price": None,
                    "shares": float(shares),
                    "pnl": None,
                    "return_pct": None
                })

        # =============================================================
        # EXIT
        # =============================================================
        elif position > 0 and signals.loc[idx, "exit"]:
            if i + 1 < n:
                fill_idx = idxs[i+1]
                fill_price = float(df.loc[fill_idx]["open"])
            else:
                fill_idx = idx
                fill_price = close_price

            sell_price = fill_price - slippage

            proceeds = position * sell_price
            cost = position * entry_price

            pnl = proceeds - cost - commission
            return_pct = pnl / cost if cost != 0 else 0

            last_trade = trades[-1]
            last_trade["exit_index"] = str(idx)
            last_trade["exit_fill_index"] = str(fill_idx)
            last_trade["exit_price"] = float(sell_price)
            last_trade["pnl"] = float(pnl)
            last_trade["return_pct"] = float(return_pct) * 100.0

            cash += proceeds
            position = 0
            entry_price = None

        # =============================================================
        # DAILY MARK TO MARKET
        # =============================================================
        mtm_equity = cash + position * close_price
        equity_values.append(mtm_equity)
        equity_index.append(idx)

    # =============================================================
    # FORCE CLOSE at last price if still in position
    # =============================================================
    if position > 0:
        last_idx = idxs[-1]
        last_close = float(df.loc[last_idx, "close"])

        sell_price = last_close - slippage
        proceeds = position * sell_price
        cost = trades[-1]["shares"] * trades[-1]["entry_price"]

        pnl = proceeds - cost - commission
        return_pct = pnl / cost if cost != 0 else 0

        last_trade = trades[-1]
        last_trade["exit_index"] = str(last_idx)
        last_trade["exit_fill_index"] = str(last_idx)
        last_trade["exit_price"] = float(sell_price)
        last_trade["pnl"] = float(pnl)
        last_trade["return_pct"] = float(return_pct) * 100.0

        cash += proceeds
        position = 0

        equity_values[-1] = cash

    # =============================================================
    # EQUITY CURVE & METRICS
    # =============================================================
    equity = pd.Series(equity_values, index=equity_index)

    final_capital = float(equity.iloc[-1])
    total_return_pct = ((final_capital - initial_capital) / initial_capital) * 100.0

    roll_max = equity.cummax()
    drawdown = (equity - roll_max) / roll_max
    max_drawdown_pct = float(drawdown.min() * 100.0)

    results = {
        "trades": trades,
        "equity": equity,
        "final_capital": final_capital,
        "total_return_pct": total_return_pct,
        "max_drawdown_pct": max_drawdown_pct,
        "num_trades": len(trades)
    }

    return results
