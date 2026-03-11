"""
data/fetcher.py
从 yfinance 拉取 SCHD / SPY 真实历史数据
"""
import yfinance as yf
import pandas as pd
import streamlit as st
import time
from datetime import datetime, timedelta


def _yf_history_with_retry(ticker: str, period: str = "max", max_retries: int = 3) -> pd.DataFrame:
    """带重试和退避的 yfinance 历史数据请求"""
    for attempt in range(max_retries):
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period=period, auto_adjust=False)
            if not hist.empty:
                return hist
        except Exception:
            pass
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # 1s, 2s 退避
    return pd.DataFrame()


@st.cache_data(ttl=86400)   # 缓存 24 小时，大幅减少请求量
def fetch_history(ticker: str, period: str = "max") -> pd.DataFrame:
    """拉取历史价格 + 股息，返回月度数据"""
    hist = _yf_history_with_retry(ticker, period)

    if hist.empty:
        return pd.DataFrame()

    # 月度收盘价
    monthly = hist["Close"].resample("ME").last().to_frame("close")
    monthly.index = monthly.index.to_period("M").to_timestamp()

    # 月度股息（当月所有股息加总）
    divs = hist["Dividends"].resample("ME").sum().to_frame("dividend")
    divs.index = divs.index.to_period("M").to_timestamp()

    df = monthly.join(divs, how="left").fillna(0)
    df["ticker"]         = ticker
    df["monthly_return"] = df["close"].pct_change() * 100
    df["drawdown"]       = (df["close"] / df["close"].cummax() - 1) * 100
    df["year"]           = df.index.year
    df["month"]          = df.index.month

    return df.dropna(subset=["monthly_return"])


@st.cache_data(ttl=86400)
def fetch_info(ticker: str) -> dict:
    """拉取基本面信息，失败时返回默认值"""
    try:
        t    = yf.Ticker(ticker)
        info = t.info
        return {
            "price":          info.get("regularMarketPrice") or info.get("previousClose", 0),
            "dividend_yield": round((info.get("trailingAnnualDividendYield") or 0) * 100, 2),
            "expense_ratio":  round((info.get("annualReportExpenseRatio") or 0) * 100, 2),
            "beta":           info.get("beta3Year") or info.get("beta", 1.0),
            "name":           info.get("longName", ticker),
            "ytd_return":     round((info.get("ytdReturn") or 0) * 100, 2),
        }
    except Exception:
        defaults = {
            "SCHD": {"price": 28.0, "dividend_yield": 3.50, "expense_ratio": 0.06, "beta": 0.75, "name": "Schwab U.S. Dividend Equity ETF", "ytd_return": 0.0},
            "SPY":  {"price": 580.0, "dividend_yield": 1.30, "expense_ratio": 0.09, "beta": 1.0, "name": "SPDR S&P 500 ETF Trust", "ytd_return": 0.0},
        }
        return defaults.get(ticker, {"price": 0, "dividend_yield": 0, "expense_ratio": 0, "beta": 1.0, "name": ticker, "ytd_return": 0})


@st.cache_data(ttl=86400)
def fetch_both() -> tuple[pd.DataFrame, pd.DataFrame]:
    """同时拉 SCHD 和 SPY，返回 (schd_df, spy_df)"""
    schd = fetch_history("SCHD")
    time.sleep(1)  # 请求间隔，避免限流
    spy  = fetch_history("SPY")

    # 对齐时间范围（取两者都有数据的区间）
    if not schd.empty and not spy.empty:
        start = max(schd.index.min(), spy.index.min())
        schd  = schd[schd.index >= start]
        spy   = spy[spy.index >= start]

    return schd, spy


def calc_drawdown_buckets(df: pd.DataFrame) -> pd.DataFrame:
    """
    找出每次完整的回调事件（从高点到谷底到恢复）
    返回：每次事件的 峰值日期、谷底日期、恢复日期、最大回撤、恢复月数
    """
    closes   = df["close"]
    peak     = closes.cummax()
    drawdown = (closes / peak - 1) * 100

    events = []
    in_drawdown = False
    peak_date = trough_date = None
    peak_price = trough_price = 0

    for date, dd in drawdown.items():
        if not in_drawdown and dd < -1:          # 开始回调
            in_drawdown  = True
            peak_date    = date
            peak_price   = closes[date]
            trough_date  = date
            trough_price = closes[date]

        elif in_drawdown:
            if closes[date] < trough_price:       # 继续下探
                trough_date  = date
                trough_price = closes[date]

            elif closes[date] >= peak_price:      # 恢复到前高
                max_dd        = (trough_price / peak_price - 1) * 100
                recover_months = len(pd.date_range(trough_date, date, freq="ME"))
                events.append({
                    "peak_date":      peak_date,
                    "trough_date":    trough_date,
                    "recover_date":   date,
                    "max_drawdown":   round(max_dd, 1),
                    "recover_months": recover_months,
                })
                in_drawdown = False

    if not events:
        return pd.DataFrame()

    result = pd.DataFrame(events)

    def bucket(dd):
        if dd > -5:   return "< 5%"
        if dd > -10:  return "5–10%"
        if dd > -15:  return "10–15%"
        if dd > -20:  return "15–20%"
        if dd > -30:  return "20–30%"
        return "> 30%"

    result["bucket"] = result["max_drawdown"].apply(bucket)
    return result
