"""
pages/1_📉_回撤分析.py
SCHD 历史回撤深度、概率分布、恢复时间
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data.fetcher import fetch_history, calc_drawdown_buckets

st.set_page_config(page_title="回撤分析", page_icon="📉", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&family=Noto+Sans+SC:wght@400;700&display=swap');
html, body, [class*="css"] { font-family:'Noto Sans SC',sans-serif; background:#07090e; color:#cdd6e0; }
</style>""", unsafe_allow_html=True)

C = {"schd":"#38bdf8","spy":"#f59e0b","green":"#4ade80","red":"#f87171",
     "accent":"#a3e635","bg":"#07090e","card":"#0c1018","border":"#1c2535","muted":"#4e6278"}

st.markdown("# 📉 回撤分析")
st.markdown("##### SCHD 历史回撤深度 · 概率分布 · 恢复时间")
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
# 图1：回撤深度时间序列
# ══════════════════════════════════════════════════
st.markdown("#### 历史回撤深度（从历史最高点）")

fig_dd = go.Figure()
fig_dd.add_trace(go.Scatter(
    x=df.index, y=df["drawdown"],
    fill="tozeroy", name="回撤幅度",
    line=dict(color=C["red"], width=1.5),
    fillcolor="rgba(248,113,113,0.15)",
))
for level, color in [(-10, C["spy"]), (-20, "#fb923c"), (-30, C["red"])]:
    fig_dd.add_hline(y=level, line_dash="dash", line_color=color,
                     annotation_text=f"{level}%", annotation_font_color=color,
                     annotation_font_size=10)
fig_dd.update_layout(
    plot_bgcolor=C["card"], paper_bgcolor=C["bg"], font_color=C["muted"],
    height=280, margin=dict(t=10,b=20,l=10,r=10),
    xaxis=dict(gridcolor=C["border"]), yaxis=dict(gridcolor=C["border"], ticksuffix="%"),
    hovermode="x unified",
)
st.plotly_chart(fig_dd, use_container_width=True)

# ══════════════════════════════════════════════════
# 图2 + 图3：概率分布 & 恢复时间
# ══════════════════════════════════════════════════
col1, col2 = st.columns(2)

bucket_events = calc_drawdown_buckets(df)

BUCKET_ORDER  = ["< 5%","5–10%","10–15%","15–20%","20–30%","> 30%"]
BUCKET_COLORS = ["#4ade80","#86efac","#f59e0b","#fb923c","#f87171","#7f1d1d"]

with col1:
    st.markdown("#### 回调幅度概率分布")
    if not bucket_events.empty:
        counts = bucket_events["bucket"].value_counts()
        total  = counts.sum()
        rows   = []
        for b in BUCKET_ORDER:
            n = counts.get(b, 0)
            rows.append({"bucket": b, "count": n, "prob": n / total * 100})
        prob_df = pd.DataFrame(rows)

        fig_prob = go.Figure(go.Bar(
            x=prob_df["prob"], y=prob_df["bucket"],
            orientation="h",
            marker_color=BUCKET_COLORS,
            text=prob_df["prob"].apply(lambda x: f"{x:.0f}%"),
            textposition="outside",
        ))
        fig_prob.update_layout(
            plot_bgcolor=C["card"], paper_bgcolor=C["bg"], font_color=C["muted"],
            height=300, margin=dict(t=10,b=20,l=10,r=40),
            xaxis=dict(gridcolor=C["border"], ticksuffix="%"),
            yaxis=dict(gridcolor=C["border"]),
            showlegend=False,
        )
        st.plotly_chart(fig_prob, use_container_width=True)
    else:
        st.info("数据不足以计算完整的回调事件")

with col2:
    st.markdown("#### 各区间平均恢复时间（月）")
    if not bucket_events.empty:
        recovery = (
            bucket_events.groupby("bucket")["recover_months"]
            .agg(["mean","max","min","count"])
            .reset_index()
        )
        recovery.columns = ["bucket","avg","max","min","次数"]
        recovery["avg"] = recovery["avg"].round(1)

        # 按预定顺序排序
        recovery["order"] = recovery["bucket"].map(
            {b:i for i,b in enumerate(BUCKET_ORDER)}
        )
        recovery = recovery.sort_values("order")

        fig_rec = go.Figure()
        fig_rec.add_trace(go.Bar(
            x=recovery["avg"], y=recovery["bucket"],
            orientation="h",
            marker_color=BUCKET_COLORS[:len(recovery)],
            text=recovery["avg"].apply(lambda x: f"{x:.1f}月"),
            textposition="outside",
            name="平均恢复月数",
        ))
        fig_rec.update_layout(
            plot_bgcolor=C["card"], paper_bgcolor=C["bg"], font_color=C["muted"],
            height=300, margin=dict(t=10,b=20,l=10,r=60),
            xaxis=dict(gridcolor=C["border"], title="月数"),
            yaxis=dict(gridcolor=C["border"]),
            showlegend=False,
        )
        st.plotly_chart(fig_rec, use_container_width=True)

# ══════════════════════════════════════════════════
# 回调事件明细表
# ══════════════════════════════════════════════════
if not bucket_events.empty:
    st.markdown("#### 历史回调事件明细")
    display = bucket_events[["peak_date","trough_date","recover_date",
                              "max_drawdown","recover_months","bucket"]].copy()
    display.columns = ["峰值日期","谷底日期","恢复日期","最大回撤","恢复月数","回撤区间"]
    display["最大回撤"] = display["最大回撤"].apply(lambda x: f"{x:.1f}%")
    display = display.sort_values("峰值日期", ascending=False)
    st.dataframe(display.reset_index(drop=True), use_container_width=True, height=300)
