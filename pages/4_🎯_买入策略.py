"""
pages/4_🎯_买入策略.py
金字塔加仓模型：小跌小买，大跌大买
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data.fetcher import fetch_history

st.set_page_config(page_title="买入策略", page_icon="🎯", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&family=Noto+Sans+SC:wght@400;700&display=swap');
html, body, [class*="css"] { font-family:'Noto Sans SC',sans-serif; background:#07090e; color:#cdd6e0; }
.metric-card { background:#0c1018; border:1px solid #1c2535; border-radius:10px; padding:16px; text-align:center; }
.metric-val  { font-family:'IBM Plex Mono',monospace; font-size:22px; font-weight:700; }
.metric-lbl  { font-size:10px; color:#4e6278; letter-spacing:1px; margin-top:4px; }
</style>""", unsafe_allow_html=True)

C = {"schd":"#38bdf8","spy":"#f59e0b","green":"#4ade80","red":"#f87171",
     "accent":"#a3e635","bg":"#07090e","card":"#0c1018","border":"#1c2535","muted":"#4e6278"}

st.markdown("# 🎯 买入策略")
st.markdown("##### 金字塔加仓模型 · 小跌小买大跌大买")
st.divider()

# ── 侧边栏参数 ──────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ 策略参数")
    st.divider()

    base_amount = st.number_input(
        "基础定投金额（$/月）", min_value=100, max_value=50000,
        value=1000, step=100, format="%d"
    )

    st.markdown("**金字塔加仓倍数**")
    st.caption("当回撤达到对应区间时，投入 = 基础金额 × 倍数")

    tier1_mult = st.slider("回撤 5–10%  加仓倍数", 1.0, 5.0, 1.5, 0.5)
    tier2_mult = st.slider("回撤 10–20% 加仓倍数", 1.0, 8.0, 2.5, 0.5)
    tier3_mult = st.slider("回撤 20–30% 加仓倍数", 1.0, 10.0, 4.0, 0.5)
    tier4_mult = st.slider("回撤 > 30%  加仓倍数", 1.0, 15.0, 6.0, 0.5)

# ── 策略规则展示 ──────────────────────────────────
st.markdown("#### 金字塔加仓规则")

rules = pd.DataFrame({
    "回撤区间":    ["< 5%",           "5–10%",           "10–20%",          "20–30%",          "> 30%"],
    "加仓倍数":    ["1.0x（正常定投）", f"{tier1_mult:.1f}x", f"{tier2_mult:.1f}x", f"{tier3_mult:.1f}x", f"{tier4_mult:.1f}x"],
    "月投入金额":  [f"${base_amount:,}", f"${base_amount * tier1_mult:,.0f}", f"${base_amount * tier2_mult:,.0f}", f"${base_amount * tier3_mult:,.0f}", f"${base_amount * tier4_mult:,.0f}"],
    "策略理念":    ["保持纪律", "小幅折扣，稍微加码", "明显低估，加大力度", "恐慌区域，大幅加仓", "极端机会，全力出击"],
})
st.dataframe(rules, use_container_width=True, hide_index=True)

# ── 加载数据 ──────────────────────────────────────
with st.spinner("正在加载数据（每 24 小时自动刷新）..."):
    df = fetch_history("SCHD")

if df.empty:
    st.error("数据加载失败，请稍后刷新重试")
    st.stop()

st.divider()

# ══════════════════════════════════════════════════
# 回测：金字塔策略 vs 普通 DCA
# ══════════════════════════════════════════════════
st.markdown("#### 历史回测：金字塔策略 vs 普通定投")

def get_multiplier(dd):
    """根据回撤幅度返回加仓倍数"""
    if dd > -5:   return 1.0
    if dd > -10:  return tier1_mult
    if dd > -20:  return tier2_mult
    if dd > -30:  return tier3_mult
    return tier4_mult

# 模拟金字塔策略
pyramid_rows = []
p_shares = 0.0
p_invested = 0.0
p_dividends = 0.0

dca_rows = []
d_shares = 0.0
d_invested = 0.0
d_dividends = 0.0

for _, row in df.iterrows():
    price = row["close"]
    dd = row["drawdown"]
    if price <= 0:
        continue

    # 金字塔策略
    mult = get_multiplier(dd)
    p_amount = base_amount * mult
    p_new = p_amount / price
    p_shares += p_new
    p_invested += p_amount

    p_div = p_shares * row.get("dividend", 0)
    p_dividends += p_div
    if row.get("dividend", 0) > 0 and price > 0:
        p_shares += p_div / price

    p_value = p_shares * price

    pyramid_rows.append({
        "date": row.name,
        "invested": round(p_invested),
        "value": round(p_value),
        "multiplier": mult,
        "drawdown": dd,
    })

    # 普通 DCA
    d_new = base_amount / price
    d_shares += d_new
    d_invested += base_amount

    d_div = d_shares * row.get("dividend", 0)
    d_dividends += d_div
    if row.get("dividend", 0) > 0 and price > 0:
        d_shares += d_div / price

    d_value = d_shares * price

    dca_rows.append({
        "date": row.name,
        "invested": round(d_invested),
        "value": round(d_value),
    })

pyramid_df = pd.DataFrame(pyramid_rows)
dca_result = pd.DataFrame(dca_rows)

# 关键指标对比
if not pyramid_df.empty and not dca_result.empty:
    p_final = pyramid_df.iloc[-1]
    d_final = dca_result.iloc[-1]
    p_return = (p_final["value"] - p_final["invested"]) / p_final["invested"] * 100
    d_return = (d_final["value"] - d_final["invested"]) / d_final["invested"] * 100

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-val" style="color:{C['accent']}">${p_final['value']:,.0f}</div>
            <div class="metric-lbl">金字塔策略市值</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-val" style="color:{C['schd']}">${d_final['value']:,.0f}</div>
            <div class="metric-lbl">普通定投市值</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        diff = p_final["value"] - d_final["value"]
        st.markdown(f"""<div class="metric-card">
            <div class="metric-val" style="color:{C['green']}">${diff:,.0f}</div>
            <div class="metric-lbl">金字塔额外收益</div>
        </div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-val" style="color:{C['spy']}">{p_return:.1f}% vs {d_return:.1f}%</div>
            <div class="metric-lbl">总收益率对比</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")

    # 市值对比图
    fig_compare = go.Figure()
    fig_compare.add_trace(go.Scatter(
        x=pyramid_df["date"], y=pyramid_df["value"],
        name="金字塔策略", fill="tozeroy",
        line=dict(color=C["accent"], width=2),
        fillcolor="rgba(163,230,53,0.1)",
    ))
    fig_compare.add_trace(go.Scatter(
        x=dca_result["date"], y=dca_result["value"],
        name="普通定投",
        line=dict(color=C["schd"], width=2, dash="dash"),
    ))
    fig_compare.update_layout(
        plot_bgcolor=C["card"], paper_bgcolor=C["bg"], font_color=C["muted"],
        height=350, margin=dict(t=10, b=20, l=10, r=10),
        xaxis=dict(gridcolor=C["border"]),
        yaxis=dict(gridcolor=C["border"], tickformat="$,.0f"),
        legend=dict(orientation="h", y=1.1),
        hovermode="x unified",
    )
    st.plotly_chart(fig_compare, use_container_width=True)

    # 加仓倍数时间线
    st.markdown("#### 历史加仓倍数变化")
    st.caption("显示每个月实际触发的加仓倍数，越高说明回撤越深、加仓越多")

    fig_mult = go.Figure()
    mult_colors = []
    for m in pyramid_df["multiplier"]:
        if m <= 1.0:   mult_colors.append(C["muted"])
        elif m <= 2.0: mult_colors.append(C["spy"])
        elif m <= 4.0: mult_colors.append("#fb923c")
        else:          mult_colors.append(C["red"])

    fig_mult.add_trace(go.Bar(
        x=pyramid_df["date"], y=pyramid_df["multiplier"],
        marker_color=mult_colors, opacity=0.8,
        hovertemplate="日期：%{x}<br>倍数：%{y:.1f}x<extra></extra>",
    ))
    fig_mult.add_hline(y=1, line_color=C["muted"], line_width=1, line_dash="dash")
    fig_mult.update_layout(
        plot_bgcolor=C["card"], paper_bgcolor=C["bg"], font_color=C["muted"],
        height=220, margin=dict(t=10, b=20, l=10, r=10),
        xaxis=dict(gridcolor=C["border"]),
        yaxis=dict(gridcolor=C["border"], title="加仓倍数"),
        showlegend=False,
    )
    st.plotly_chart(fig_mult, use_container_width=True)

# ══════════════════════════════════════════════════
# 实用建议
# ══════════════════════════════════════════════════
st.divider()
st.markdown("#### 💡 金字塔加仓使用建议")

n1, n2, n3 = st.columns(3)
n1.info("**资金管理**\n\n预留足够的现金储备（建议 6 个月生活费），确保大跌时有钱加仓，不要借钱投资。")
n2.warning("**纪律执行**\n\n策略的核心是反人性操作 —— 市场越恐慌越要买。提前设好计划，用自动化工具执行。")
n3.success("**长期视角**\n\n金字塔策略的优势需要经历完整牛熊周期才能体现，短期可能因为多投入而暂时亏损更多。")
