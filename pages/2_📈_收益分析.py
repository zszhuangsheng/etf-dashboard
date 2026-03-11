"""
pages/2_📈_收益分析.py
年度收益率、月度热力图、DCA 模拟
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data.fetcher import fetch_history
from data.calculator import calc_annual_returns, calc_heatmap, simulate_dca

st.set_page_config(page_title="收益分析", page_icon="📈", layout="wide")

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

st.markdown("# 📈 收益分析")
st.markdown("##### SCHD 年度收益率 · 月度热力图 · DCA 定投模拟")
st.divider()

# ── 加载数据 ──────────────────────────────────────
with st.spinner("正在加载数据（每 24 小时自动刷新）..."):
    df = fetch_history("SCHD")

if df.empty:
    st.error("数据加载失败，请稍后刷新重试")
    st.stop()

last_update = df.index.max().strftime("%Y-%m-%d")
st.caption(f"数据截至：{last_update}，来源：Yahoo Finance / yfinance")

# ══════════════════════════════════════════════════
# 关键统计指标
# ══════════════════════════════════════════════════
annual_df = calc_annual_returns(df)
avg_return = annual_df["return_pct"].mean()
best_year = annual_df.loc[annual_df["return_pct"].idxmax()]
worst_year = annual_df.loc[annual_df["return_pct"].idxmin()]
positive_years = (annual_df["return_pct"] > 0).sum()
total_years = len(annual_df)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-val" style="color:{C['schd']}">{avg_return:.1f}%</div>
        <div class="metric-lbl">年均收益率</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-val" style="color:{C['green']}">{best_year['return_pct']:.1f}%</div>
        <div class="metric-lbl">最佳年度（{int(best_year['year'])}）</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-val" style="color:{C['red']}">{worst_year['return_pct']:.1f}%</div>
        <div class="metric-lbl">最差年度（{int(worst_year['year'])}）</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-val" style="color:{C['accent']}">{positive_years}/{total_years}</div>
        <div class="metric-lbl">正收益年数</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════
# 图1：年度收益率柱状图
# ══════════════════════════════════════════════════
st.markdown("#### 年度收益率")

fig_annual = go.Figure()
colors = [C["green"] if r >= 0 else C["red"] for r in annual_df["return_pct"]]
fig_annual.add_trace(go.Bar(
    x=annual_df["year"], y=annual_df["return_pct"],
    marker_color=colors, opacity=0.85,
    text=annual_df["return_pct"].apply(lambda x: f"{x:.1f}%"),
    textposition="outside", textfont_size=10,
))
fig_annual.add_hline(y=0, line_color=C["muted"], line_width=1)
fig_annual.add_hline(y=avg_return, line_dash="dash", line_color=C["schd"],
                     annotation_text=f"平均 {avg_return:.1f}%",
                     annotation_font_color=C["schd"], annotation_font_size=10)
fig_annual.update_layout(
    plot_bgcolor=C["card"], paper_bgcolor=C["bg"], font_color=C["muted"],
    height=320, margin=dict(t=10, b=20, l=10, r=10),
    xaxis=dict(gridcolor=C["border"], dtick=1),
    yaxis=dict(gridcolor=C["border"], ticksuffix="%"),
    showlegend=False, hovermode="x unified",
)
st.plotly_chart(fig_annual, use_container_width=True)

# ══════════════════════════════════════════════════
# 图2：月度收益热力图
# ══════════════════════════════════════════════════
st.markdown("#### 月度收益热力图（%）")

heatmap_df = calc_heatmap(df)

fig_heat = go.Figure(go.Heatmap(
    z=heatmap_df.values,
    x=heatmap_df.columns,
    y=[str(y) for y in heatmap_df.index],
    colorscale=[
        [0, "#7f1d1d"],
        [0.3, "#f87171"],
        [0.5, "#1c2535"],
        [0.7, "#4ade80"],
        [1, "#15803d"],
    ],
    zmid=0,
    text=heatmap_df.values,
    texttemplate="%{text:.1f}",
    textfont_size=10,
    hovertemplate="年份：%{y}<br>%{x}：%{z:.1f}%<extra></extra>",
))
fig_heat.update_layout(
    plot_bgcolor=C["card"], paper_bgcolor=C["bg"], font_color=C["muted"],
    height=max(300, len(heatmap_df) * 28),
    margin=dict(t=10, b=20, l=10, r=10),
    yaxis=dict(autorange="reversed"),
)
st.plotly_chart(fig_heat, use_container_width=True)

# ══════════════════════════════════════════════════
# 图3：DCA 定投模拟
# ══════════════════════════════════════════════════
st.divider()
st.markdown("#### DCA 定投模拟")
st.caption("假设每月固定金额买入 SCHD，股息自动再投资")

dca_col1, dca_col2 = st.columns([1, 3])
with dca_col1:
    monthly_amount = st.number_input(
        "每月定投金额（$）", min_value=100, max_value=50000,
        value=1000, step=100, format="%d"
    )

dca_df = simulate_dca(df, monthly_amount=monthly_amount, ticker="SCHD")

if not dca_df.empty:
    final = dca_df.iloc[-1]

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-val" style="color:{C['muted']}">${final['total_invested']:,.0f}</div>
            <div class="metric-lbl">累计投入</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-val" style="color:{C['schd']}">${final['market_value']:,.0f}</div>
            <div class="metric-lbl">当前市值</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        color = C["green"] if final["gain_pct"] >= 0 else C["red"]
        st.markdown(f"""<div class="metric-card">
            <div class="metric-val" style="color:{color}">{final['gain_pct']:.1f}%</div>
            <div class="metric-lbl">总收益率</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")

    fig_dca = go.Figure()
    fig_dca.add_trace(go.Scatter(
        x=dca_df["date"], y=dca_df["market_value"],
        name="市值", fill="tozeroy",
        line=dict(color=C["schd"], width=2),
        fillcolor="rgba(56,189,248,0.12)",
    ))
    fig_dca.add_trace(go.Scatter(
        x=dca_df["date"], y=dca_df["total_invested"],
        name="累计投入",
        line=dict(color=C["muted"], width=1.5, dash="dash"),
    ))
    fig_dca.update_layout(
        plot_bgcolor=C["card"], paper_bgcolor=C["bg"], font_color=C["muted"],
        height=320, margin=dict(t=10, b=20, l=10, r=10),
        xaxis=dict(gridcolor=C["border"]),
        yaxis=dict(gridcolor=C["border"], tickformat="$,.0f"),
        legend=dict(orientation="h", y=1.1),
        hovermode="x unified",
    )
    st.plotly_chart(fig_dca, use_container_width=True)
