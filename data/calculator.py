"""
data/calculator.py
所有核心指标计算：退休模拟、DCA、Yield on Cost
"""
import pandas as pd
import numpy as np


def simulate_retirement(
    current_assets:   float = 150_000,
    monthly_invest:   float = 2_000,
    years:            int   = 30,
    annual_return:    float = 0.10,
    dividend_yield:   float = 0.035,
    dividend_growth:  float = 0.10,
    spy_pct:          float = 0.60,   # 积累期 SPY 比例
) -> pd.DataFrame:
    """
    逐年模拟资产增长 + 股息收入
    返回每年的：总资产、SCHD 部分、年股息、月收入、Yield on Cost
    """
    rows   = []
    assets = current_assets

    for y in range(1, years + 1):
        # 当年年龄对应的 SCHD 比例（随年龄增加）
        age = 30 + y
        if age < 40:
            schd_pct = 0.40
        elif age < 50:
            schd_pct = 0.60
        else:
            schd_pct = 0.80

        spy_return  = 0.135   # SPY 历史年化
        schd_return = 0.115   # SCHD 历史年化

        blended_return = spy_pct * spy_return + (1 - spy_pct) * schd_return
        assets = assets * (1 + blended_return) + monthly_invest * 12

        schd_assets = assets * schd_pct
        yoc         = dividend_yield * ((1 + dividend_growth) ** y)
        annual_div  = schd_assets * yoc
        monthly_inc = annual_div / 12

        rows.append({
            "year":           y,
            "age":            age,
            "total_assets":   round(assets),
            "schd_assets":    round(schd_assets),
            "yield_on_cost":  round(yoc * 100, 2),
            "annual_dividend":round(annual_div),
            "monthly_income": round(monthly_inc),
        })

    return pd.DataFrame(rows)


def simulate_dca(
    df:             pd.DataFrame,
    monthly_amount: float = 500,
    ticker:         str   = "SCHD",
) -> pd.DataFrame:
    """
    DCA 模拟：每月固定金额买入
    返回：每月的总投入、总市值、总股息收入、累计份额
    """
    rows   = []
    shares = 0.0
    total_invested = 0.0
    total_dividends = 0.0

    for _, row in df.iterrows():
        price = row["close"]
        if price <= 0:
            continue

        # 每月买入
        new_shares      = monthly_amount / price
        shares         += new_shares
        total_invested += monthly_amount

        # 当月股息（按持仓份额）
        div_per_share    = row.get("dividend", 0)
        monthly_div      = shares * div_per_share
        total_dividends += monthly_div
        # 股息再投资
        if div_per_share > 0 and price > 0:
            shares += monthly_div / price

        market_value = shares * price
        gain_pct     = (market_value - total_invested) / total_invested * 100

        rows.append({
            "date":             row.name if hasattr(row, "name") else row.get("date"),
            "total_invested":   round(total_invested),
            "market_value":     round(market_value),
            "total_dividends":  round(total_dividends),
            "shares":           round(shares, 2),
            "gain_pct":         round(gain_pct, 1),
        })

    return pd.DataFrame(rows)


def calc_annual_returns(df: pd.DataFrame) -> pd.DataFrame:
    """从月度数据计算年度收益率"""
    annual = (
        df.groupby("year")["close"]
        .agg(["first", "last"])
        .assign(annual_return=lambda x: (x["last"] / x["first"] - 1) * 100)
        .reset_index()
    )
    return annual[["year", "annual_return"]].rename(
        columns={"annual_return": "return_pct"}
    )


def calc_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    """
    月度收益热力图数据
    返回 pivot table：行=年，列=月
    """
    pivot = df.pivot_table(
        values="monthly_return",
        index="year",
        columns="month",
        aggfunc="first",
    )
    pivot.columns = [f"{m}月" for m in pivot.columns]
    return pivot.round(1)


def find_retirement_year(
    simulation_df: pd.DataFrame,
    target_monthly: float,
) -> dict:
    """找到股息首次达到目标月收入的年份"""
    reached = simulation_df[simulation_df["monthly_income"] >= target_monthly]
    if reached.empty:
        return {"reached": False, "age": None, "assets": None}
    row = reached.iloc[0]
    return {
        "reached": True,
        "age":     int(row["age"]),
        "assets":  int(row["total_assets"]),
        "monthly": int(row["monthly_income"]),
    }
