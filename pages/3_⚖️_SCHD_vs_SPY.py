"""
pages/3_⚖️_SCHD_vs_SPY.py
总回报对比、熊市表现、风险指标
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data.fetcher import fetch_both, fetch_info
from data.calculator import calc_annual_returns

st.set_page_config(page_title="SCHD vs SPY", page_icon="⚖️", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&family=Noto+Sans+SC:wght@400;700&display=swap');
html, body, [class*="css"] { font-family:'Noto Sans SC',sans-serif; background:#07090e; color:#cdd6e0; }
.metric-card { background:#0c1018; border:1px solid #1c2535; border-radius:10px; padding:16px; text-align:center; margin-bottom:8px; }
.metric-val  { font-family:'IBM Plex Mono',monospace; font-size:22px; font-weight:700; }
.metric-lbl  { font-size:10px; color:#4e6278; letter-spacing:1px; margin-top:4px; }
</style>""", unsafe_allow_html=True)

C = {"schd":"#38bdf8","spy":"#f59e0b","green":"#4ade80","red":"#f87171",
     "accent":"#a3e635","bg":"#07090e","card":"#0c1018","border":"#1c2535","muted":"#4e6278"}

st.markdown("# ⚖️ SCHD vs SPY 对比")
st.markdown("##### 总回报 · 风险指标 · 熊市表现")
st.divider()

with st.spinner("拉取数据中..."):
    schd_df, spy_df = fetch_both()
    schd_info = fetch_info("SCHD")
    spy_info  = fetch_info("SPY")

if schd_df.empty or spy_df.empty:
    st.error("数据加载失败")
    st.stop()

st.caption(f"数据截至：{schd_df.index.max().strftime('%Y-%m-%d')}")

# ══════════════════════════════════════════════════
# 关键指标对比
# ══════════════════════════════════════════════════
st.markdown("#### 核心指标对照")
metrics = [
    ("当前价格",     f"${schd_info['price']:.2f}",    f"${spy_info['price']:.2f}",   "—"),
    ("股息率",       f"{schd_info['dividend_yield']:.2f}%", f"{spy_info['dividend_yield']:.2f}%", "SCHD"),
    ("费用率",       f"{schd_info['expense_ratio']:.2f}%",  f"{spy_info['expense_ratio']:.2f}%",  "SCHD"),
    ("Beta",         f"~0.75",                          f"1.00",                        "SCHD"),
    ("最大历史回撤", f"~-27%",                          f"~-34%",                       "SCHD"),
    ("年化波动率",   f"~13%",                           f"~16%",                        "SCHD"),
]

cols = st.columns(len(metrics))
for col, (label, schd_v, spy_v, winner) in zip(cols, metrics):
    with col:
        schd_color = C["schd"] if winner == "SCHD" else C["muted"]
        spy_color  = C["spy"]  if winner == "SPY"  else C["muted"]
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-lbl">{label}</div>
            <div style="display:flex;justify-content:space-around;margin-top:8px">
                <div>
                    <div class="metric-val" style="color:{schd_color}">{schd_v}</div>
                    <div class="metric-lbl">SCHD</div>
                </div>
                <div>
                    <div class="metric-val" style="color:{spy_color}">{spy_v}</div>
                    <div class="metric-lbl">SPY</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════
# 图：总回报对比（归一化到 100）
# ══════════════════════════════════════════════════
st.markdown("#### 累计总回报对比（归一化，起点=100）")

schd_norm = schd_df["close"] / schd_df["close"].iloc[0] * 100
spy_norm  = spy_df["close"]  / spy_df["close"].iloc[0]  * 100

fig_total = go.Figure()
fig_total.add_trace(go.Scatter(
    x=schd_df.index, y=schd_norm, name="SCHD",
    line=dict(color=C["schd"], width=2),
))
fig_total.add_trace(go.Scatter(
    x=spy_df.index, y=spy_norm, name="SPY",
    line=dict(color=C["spy"], width=2),
))
fig_total.update_layout(
    plot_bgcolor=C["card"], paper_bgcolor=C["bg"], font_color=C["muted"],
    height=320, margin=dict(t=10,b=20,l=10,r=10),
    xaxis=dict(gridcolor=C["border"]),
    yaxis=dict(gridcolor=C["border"], ticksuffix=""),
    legend=dict(orientation="h", y=1.1),
    hovermode="x unified",
)
st.plotly_chart(fig_total, use_container_width=True)

# ══════════════════════════════════════════════════
# 年度收益对比柱状图
# ══════════════════════════════════════════════════
st.markdown("#### 年度收益率对比")

schd_annual = calc_annual_returns(schd_df)
spy_annual  = calc_annual_returns(spy_df)
merged = schd_annual.merge(spy_annual, on="year", suffixes=("_schd","_spy"))

fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(
    x=merged["year"], y=merged["return_pct_schd"],
    name="SCHD", marker_color=C["schd"], opacity=0.85,
))
fig_bar.add_trace(go.Bar(
    x=merged["year"], y=merged["return_pct_spy"],
    name="SPY", marker_color=C["spy"], opacity=0.85,
))
fig_bar.add_hline(y=0, line_color=C["muted"], line_width=1)
fig_bar.update_layout(
    plot_bgcolor=C["card"], paper_bgcolor=C["bg"], font_color=C["muted"],
    barmode="group", height=300, margin=dict(t=10,b=20,l=10,r=10),
    xaxis=dict(gridcolor=C["border"]),
    yaxis=dict(gridcolor=C["border"], ticksuffix="%"),
    legend=dict(orientation="h", y=1.1),
    hovermode="x unified",
)
st.plotly_chart(fig_bar, use_container_width=True)

# ══════════════════════════════════════════════════
# 多维能力雷达对比
# ══════════════════════════════════════════════════
st.divider()
radar_col, bear_col = st.columns(2)

with radar_col:
    st.markdown("#### 多维能力雷达对比")

    RADAR_DATA = [
        {"axis": "成长性", "SPY": 92, "SCHD": 62},
        {"axis": "股息收益", "SPY": 32, "SCHD": 90},
        {"axis": "抗跌性", "SPY": 55, "SCHD": 78},
        {"axis": "波动稳定", "SPY": 50, "SCHD": 74},
        {"axis": "行业分散", "SPY": 80, "SCHD": 68},
        {"axis": "现金流", "SPY": 30, "SCHD": 95},
    ]

    categories = [d["axis"] for d in RADAR_DATA]
    spy_vals = [d["SPY"] for d in RADAR_DATA]
    schd_vals = [d["SCHD"] for d in RADAR_DATA]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=spy_vals + [spy_vals[0]], theta=categories + [categories[0]],
        fill="toself", fillcolor="rgba(245,158,11,0.08)",
        line=dict(color=C["spy"], width=2), name="SPY",
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=schd_vals + [schd_vals[0]], theta=categories + [categories[0]],
        fill="toself", fillcolor="rgba(56,189,248,0.08)",
        line=dict(color=C["schd"], width=2), name="SCHD",
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor=C["card"],
            radialaxis=dict(visible=True, range=[0, 100], gridcolor=C["border"], tickfont=dict(size=9, color=C["muted"])),
            angularaxis=dict(gridcolor=C["border"], tickfont=dict(size=11, color=C["muted"])),
        ),
        paper_bgcolor=C["bg"], font_color=C["muted"],
        height=380, margin=dict(t=30, b=20, l=40, r=40),
        legend=dict(orientation="h", y=-0.05),
        showlegend=True,
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ══════════════════════════════════════════════════
# 四大熊市最大回撤对比
# ══════════════════════════════════════════════════
with bear_col:
    st.markdown("#### 四大熊市最大回撤")

    BEAR_EVENTS = [
        {"event": "2015 A股冲击", "schd": -11.2, "spy": -8.5},
        {"event": "2018 Q4缩表",  "schd": -12.6, "spy": -14.0},
        {"event": "2020 COVID",   "schd": -27.3, "spy": -31.0},
        {"event": "2022 加息",    "schd": -5.8,  "spy": -19.4},
    ]

    bear_df = pd.DataFrame(BEAR_EVENTS)

    fig_bear = go.Figure()
    fig_bear.add_trace(go.Bar(
        y=bear_df["event"], x=bear_df["schd"],
        orientation="h", name="SCHD", marker_color=C["schd"], opacity=0.85,
    ))
    fig_bear.add_trace(go.Bar(
        y=bear_df["event"], x=bear_df["spy"],
        orientation="h", name="SPY", marker_color=C["spy"], opacity=0.85,
    ))
    fig_bear.update_layout(
        plot_bgcolor=C["card"], paper_bgcolor=C["bg"], font_color=C["muted"],
        barmode="group", height=380, margin=dict(t=10, b=20, l=10, r=30),
        xaxis=dict(gridcolor=C["border"], ticksuffix="%", range=[-35, 0]),
        yaxis=dict(gridcolor=C["border"]),
        legend=dict(orientation="h", y=-0.1),
    )
    st.plotly_chart(fig_bear, use_container_width=True)

# ══════════════════════════════════════════════════
# 收益模式场景解析
# ══════════════════════════════════════════════════
st.divider()
st.markdown("#### 收益模式场景解析")

scenarios = [
    {"icon": "🚀", "scene": "科技牛市",    "winner": "SPY",  "body": "2023-24年 AI 牛市 SPY +26%，SCHD 仅 +4%，科技权重差异导致巨大分化。"},
    {"icon": "🐻", "scene": "熊市防御",    "winner": "SCHD", "body": "2022年 SCHD -5.8% vs SPY -18.2%，高股息+低估值提供强力缓冲垫。"},
    {"icon": "📈", "scene": "加息周期",    "winner": "SCHD", "body": "金融/能源权重高，相对受益加息，Beta 低使整体波动更小。"},
    {"icon": "🔄", "scene": "股息再投资",  "winner": "SCHD", "body": "3.5% 股息率复利再投资，每年额外贡献约 2-3% 实际回报，长期复利效应显著。"},
]

s1, s2 = st.columns(2)
for i, sc in enumerate(scenarios):
    color = C["spy"] if sc["winner"] == "SPY" else C["schd"]
    with s1 if i % 2 == 0 else s2:
        st.markdown(f"""<div style="background:{C['card']};border:1px solid {C['border']};border-radius:8px;padding:12px 14px;margin-bottom:8px">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px">
                <span style="font-size:13px;font-weight:700;color:#cdd6e0">{sc['icon']} {sc['scene']}</span>
                <span style="font-size:11px;color:{color};font-weight:700;background:{color}15;padding:1px 8px;border-radius:4px">{sc['winner']}</span>
            </div>
            <div style="font-size:12px;color:{C['muted']};line-height:1.7">{sc['body']}</div>
        </div>""", unsafe_allow_html=True)
