import pandas as pd

# -----------------------------------------------------------
# Simple Moving Average
# -----------------------------------------------------------
def SMA(series, period):
    """
    Calculate Simple Moving Average.
    series : pandas.Series (df['close'])
    period : int
    """
    return series.rolling(window=period).mean()


# -----------------------------------------------------------
# Relative Strength Index (RSI)
# -----------------------------------------------------------
def RSI(series, period=14):
    """
    Compute RSI using Wilder's smoothing.
    """
    delta = series.diff()

    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))
    return rsi
