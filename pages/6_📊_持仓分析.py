"""
pages/6_📊_持仓分析.py
SCHD 前10大持仓、行业分布、估值指标
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data.fetcher import fetch_holdings, fetch_info

st.set_page_config(page_title="持仓分析", page_icon="📊", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&family=Noto+Sans+SC:wght@400;700&display=swap');
html, body, [class*="css"] { font-family:'Noto Sans SC',sans-serif; background:#07090e; color:#cdd6e0; }
.metric-card { background:#0c1018; border:1px solid #1c2535; border-radius:10px; padding:16px; text-align:center; }
.metric-val  { font-family:'IBM Plex Mono',monospace; font-size:22px; font-weight:700; }
.metric-lbl  { font-size:10px; color:#4e6278; letter-spacing:1px; margin-top:4px; }
.holding-row { background:#0c1018; border:1px solid #1c2535; border-radius:8px; padding:12px 16px;
               margin-bottom:6px; display:flex; justify-content:space-between; align-items:center; }
.holding-rank { font-family:'IBM Plex Mono',monospace; color:#4e6278; font-size:14px; width:30px; }
.holding-symbol { font-family:'IBM Plex Mono',monospace; color:#38bdf8; font-weight:700; font-size:16px; }
.holding-name { color:#4e6278; font-size:12px; }
.holding-weight { font-family:'IBM Plex Mono',monospace; color:#a3e635; font-size:18px; font-weight:700; }
</style>""", unsafe_allow_html=True)

C = {"schd":"#38bdf8","spy":"#f59e0b","green":"#4ade80","red":"#f87171",
     "accent":"#a3e635","bg":"#07090e","card":"#0c1018","border":"#1c2535","muted":"#4e6278"}

st.markdown("# 📊 持仓分析")
st.markdown("##### SCHD 前10大持仓 · 行业分布 · 估值指标")
st.divider()

# ── 加载数据 ──────────────────────────────────────
with st.spinner("正在加载持仓数据（每 24 小时自动刷新）..."):
    data = fetch_holdings("SCHD")
    schd_info = fetch_info("SCHD")

holdings = data["holdings"]
sectors  = data["sectors"]
valuations = data["valuations"]

if not holdings:
    st.error("持仓数据加载失败，请稍后刷新重试")
    st.stop()

# ══════════════════════════════════════════════════
# 基金概览
# ══════════════════════════════════════════════════
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-val" style="color:{C['schd']}">${schd_info['price']:.2f}</div>
        <div class="metric-lbl">当前价格</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-val" style="color:{C['accent']}">{schd_info['dividend_yield']:.2f}%</div>
        <div class="metric-lbl">股息率</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-val" style="color:{C['green']}">{schd_info['expense_ratio']:.2f}%</div>
        <div class="metric-lbl">费用率</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-val" style="color:{C['spy']}">{len(holdings)}</div>
        <div class="metric-lbl">前10大持仓</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════
# 前10大持仓
# ══════════════════════════════════════════════════
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown("#### 前10大持仓")

    top10_weight = sum(h["weight"] for h in holdings)
    st.caption(f"前10大持仓合计占比 {top10_weight:.1f}%")

    for i, h in enumerate(holdings):
        st.markdown(f"""
        <div class="holding-row">
            <div style="display:flex;align-items:center;gap:12px">
                <div class="holding-rank">#{i+1}</div>
                <div>
                    <div class="holding-symbol">{h['symbol']}</div>
                    <div class="holding-name">{h['name']}</div>
                </div>
            </div>
            <div class="holding-weight">{h['weight']:.2f}%</div>
        </div>""", unsafe_allow_html=True)

    # 持仓权重柱状图
    st.markdown("")
    h_df = pd.DataFrame(holdings)
    fig_bar = go.Figure(go.Bar(
        x=h_df["weight"], y=h_df["symbol"],
        orientation="h",
        marker_color=[C["schd"]] * len(h_df),
        text=h_df["weight"].apply(lambda x: f"{x:.2f}%"),
        textposition="outside",
        opacity=0.85,
    ))
    fig_bar.update_layout(
        plot_bgcolor=C["card"], paper_bgcolor=C["bg"], font_color=C["muted"],
        height=350, margin=dict(t=10, b=20, l=10, r=50),
        xaxis=dict(gridcolor=C["border"], ticksuffix="%"),
        yaxis=dict(gridcolor=C["border"], autorange="reversed"),
        showlegend=False,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    # ══════════════════════════════════════════════════
    # 行业分布饼图
    # ══════════════════════════════════════════════════
    st.markdown("#### 行业分布")

    if sectors:
        sorted_sectors = dict(sorted(sectors.items(), key=lambda x: x[1], reverse=True))
        sector_names = list(sorted_sectors.keys())
        sector_values = list(sorted_sectors.values())

        sector_colors = [
            "#38bdf8", "#f59e0b", "#4ade80", "#f87171", "#a3e635",
            "#818cf8", "#fb923c", "#2dd4bf", "#e879f9", "#fbbf24", "#64748b",
        ]

        fig_pie = go.Figure(go.Pie(
            labels=sector_names,
            values=sector_values,
            hole=0.45,
            marker_colors=sector_colors[:len(sector_names)],
            textinfo="label+percent",
            textfont_size=11,
            hovertemplate="%{label}<br>%{value:.1f}%<extra></extra>",
        ))
        fig_pie.update_layout(
            paper_bgcolor=C["bg"], font_color=C["muted"],
            height=400, margin=dict(t=10, b=10, l=10, r=10),
            showlegend=False,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        # 行业明细表
        sector_df = pd.DataFrame({
            "行业": sector_names,
            "占比": [f"{v:.1f}%" for v in sector_values],
        })
        st.dataframe(sector_df, use_container_width=True, hide_index=True)
    else:
        st.info("行业分布数据暂不可用")

    # ══════════════════════════════════════════════════
    # 估值指标
    # ══════════════════════════════════════════════════
    st.markdown("#### 估值指标")

    if valuations:
        val_labels = {
            "Price/Earnings": "市盈率 (P/E)",
            "Price/Book": "市净率 (P/B)",
            "Price/Sales": "市销率 (P/S)",
            "Price/Cashflow": "市现率 (P/CF)",
        }
        for raw_key, val in valuations.items():
            label = val_labels.get(raw_key, raw_key)
            # yfinance 返回的是倒数形式，需要转换
            display_val = round(1 / val, 2) if val > 0 else "N/A"
            st.markdown(f"""<div class="holding-row">
                <div style="color:{C['muted']};font-size:13px">{label}</div>
                <div style="font-family:'IBM Plex Mono',monospace;color:{C['schd']};font-size:16px;font-weight:700">{display_val}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("估值数据暂不可用")

# ══════════════════════════════════════════════════
# SCHD 特点说明
# ══════════════════════════════════════════════════
st.divider()
st.markdown("#### 💡 关于 SCHD 的选股策略")

n1, n2, n3 = st.columns(3)
n1.info("**选股标准**\n\n从道琼斯美国红利100指数中筛选，要求至少连续10年分红，并综合评估现金流/总债务比、ROE、股息率和5年股息增长率。")
n2.success("**持仓特点**\n\n约100只成分股，季度再平衡，单只股票权重上限约4%，行业分散度高，偏向价值型大盘股。")
n3.warning("**注意事项**\n\n持仓数据每季度调整一次，页面显示的是最新披露数据。实际持仓可能因市场波动略有变化。")
