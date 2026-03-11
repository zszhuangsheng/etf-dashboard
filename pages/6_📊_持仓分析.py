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
# 个股深度分析（来自研究报告数据）
# ══════════════════════════════════════════════════
st.divider()
st.markdown("#### 个股深度指标")
st.caption("股息率、增长率、PE、自由现金流覆盖率、连续增长年数、护城河类型")

STOCK_DETAILS = [
    {"ticker":"LMT", "name":"洛克希德·马丁", "sector":"工业",     "divYield":2.8, "divGrowth":5,  "pe":17.2, "fcfCover":1.8, "yrsGrowth":21, "moat":"defense monopoly",  "color":"#38bdf8"},
    {"ticker":"COP", "name":"康菲石油",       "sector":"能源",     "divYield":3.1, "divGrowth":9,  "pe":12.4, "fcfCover":2.3, "yrsGrowth":13, "moat":"low-cost producer",  "color":"#f59e0b"},
    {"ticker":"VZ",  "name":"威瑞森电信",      "sector":"通信",     "divYield":6.5, "divGrowth":2,  "pe":8.9,  "fcfCover":1.2, "yrsGrowth":17, "moat":"network monopoly",   "color":"#f87171"},
    {"ticker":"CVX", "name":"雪佛龙",         "sector":"能源",     "divYield":4.0, "divGrowth":7,  "pe":14.1, "fcfCover":2.1, "yrsGrowth":36, "moat":"integrated major",   "color":"#f59e0b"},
    {"ticker":"BMY", "name":"百时美施贵宝",    "sector":"医疗",     "divYield":4.9, "divGrowth":5,  "pe":11.3, "fcfCover":1.9, "yrsGrowth":15, "moat":"patent portfolio",   "color":"#a3e635"},
    {"ticker":"MRK", "name":"默克",           "sector":"医疗",     "divYield":2.9, "divGrowth":7,  "pe":13.8, "fcfCover":2.4, "yrsGrowth":13, "moat":"blockbuster drugs",  "color":"#a3e635"},
    {"ticker":"MO",  "name":"奥驰亚（万宝路）","sector":"消费必需", "divYield":9.2, "divGrowth":4,  "pe":9.7,  "fcfCover":1.5, "yrsGrowth":54, "moat":"brand addiction",    "color":"#4ade80"},
    {"ticker":"TXN", "name":"德州仪器",        "sector":"科技",     "divYield":3.0, "divGrowth":13, "pe":33.4, "fcfCover":1.6, "yrsGrowth":20, "moat":"analog chip leader", "color":"#818cf8"},
    {"ticker":"KO",  "name":"可口可乐",        "sector":"消费必需", "divYield":3.1, "divGrowth":4,  "pe":22.7, "fcfCover":1.7, "yrsGrowth":62, "moat":"global brand",       "color":"#4ade80"},
    {"ticker":"PEP", "name":"百事可乐",        "sector":"消费必需", "divYield":3.2, "divGrowth":7,  "pe":21.5, "fcfCover":1.8, "yrsGrowth":51, "moat":"brand+distribution", "color":"#4ade80"},
]

detail_df = pd.DataFrame(STOCK_DETAILS)
st.dataframe(
    detail_df[["ticker","name","sector","divYield","divGrowth","pe","fcfCover","yrsGrowth","moat"]].rename(columns={
        "ticker":"代码","name":"公司名","sector":"行业","divYield":"股息率%",
        "divGrowth":"股息增长%/年","pe":"PE","fcfCover":"FCF覆盖率","yrsGrowth":"连续增长年数","moat":"护城河类型"
    }),
    use_container_width=True, hide_index=True,
)

# ══════════════════════════════════════════════════
# 股息率 vs 股息增长率 散点图
# ══════════════════════════════════════════════════
st.markdown("#### 股息率 vs 股息增长率")
st.caption("气泡大小 = 持仓权重，右上角是理想区间：高股息率 + 高增长率")

fig_scatter = go.Figure()
for s in STOCK_DETAILS:
    fig_scatter.add_trace(go.Scatter(
        x=[s["divYield"]], y=[s["divGrowth"]],
        mode="markers+text",
        marker=dict(size=s.get("divYield", 3) * 6 + 10, color=s["color"], opacity=0.7,
                    line=dict(width=2, color=s["color"])),
        text=[s["ticker"]], textposition="middle center",
        textfont=dict(size=9, color="white", family="IBM Plex Mono"),
        name=s["ticker"],
        hovertemplate=f"{s['ticker']}<br>股息率: {s['divYield']}%<br>增长率: {s['divGrowth']}%/yr<extra></extra>",
    ))

fig_scatter.update_layout(
    plot_bgcolor=C["card"], paper_bgcolor=C["bg"], font_color=C["muted"],
    height=350, margin=dict(t=10, b=40, l=10, r=10),
    xaxis=dict(title="股息率 (%)", gridcolor=C["border"], ticksuffix="%"),
    yaxis=dict(title="股息增长率 (%/年)", gridcolor=C["border"], ticksuffix="%"),
    showlegend=False,
)
st.plotly_chart(fig_scatter, use_container_width=True)

# ══════════════════════════════════════════════════
# 股息连续增长年数（股息贵族/股息之王）
# ══════════════════════════════════════════════════
st.markdown("#### 股息连续增长年数")
st.caption("Dividend Kings (50年+) / Dividend Aristocrats (25年+)")

sorted_stocks = sorted(STOCK_DETAILS, key=lambda x: x["yrsGrowth"], reverse=True)
tickers_sorted = [s["ticker"] for s in sorted_stocks]
years_sorted = [s["yrsGrowth"] for s in sorted_stocks]

def get_label(y):
    if y >= 50: return "👑 股息之王"
    if y >= 25: return "🏆 股息贵族"
    if y >= 10: return "✓ 合格"
    return "⚠ 观察"

bar_colors = [C["accent"] if y >= 50 else C["green"] if y >= 25 else C["spy"] if y >= 10 else C["red"] for y in years_sorted]

fig_years = go.Figure(go.Bar(
    x=years_sorted, y=tickers_sorted,
    orientation="h", marker_color=bar_colors,
    text=[f"{y}年 {get_label(y)}" for y in years_sorted],
    textposition="outside", textfont_size=11, opacity=0.85,
))
fig_years.update_layout(
    plot_bgcolor=C["card"], paper_bgcolor=C["bg"], font_color=C["muted"],
    height=380, margin=dict(t=10, b=20, l=10, r=120),
    xaxis=dict(gridcolor=C["border"], title="连续增长年数"),
    yaxis=dict(gridcolor=C["border"], autorange="reversed"),
    showlegend=False,
)
st.plotly_chart(fig_years, use_container_width=True)

st.success("**关键洞察：** MO (54年)、KO (62年)、PEP (51年) 均为股息之王，CVX (36年) 为股息贵族。即便在 2008 年金融危机、2020 年 COVID 期间，这些公司也从未削减过股息。这是 SCHD 股息稳定性的核心保障。")

st.divider()

# ══════════════════════════════════════════════════
# SCHD 选股四大标准
# ══════════════════════════════════════════════════
st.markdown("#### SCHD 选股四大标准")

criteria = [
    {"num": "01", "title": "连续股息增长", "body": "要求至少10年不间断股息增长，筛除股息不稳定公司", "color": C["schd"]},
    {"num": "02", "title": "自由现金流覆盖", "body": "FCF / 股息 > 1.5x，确保派息由真实盈利支撑而非借债", "color": C["green"]},
    {"num": "03", "title": "股东权益回报率", "body": "ROE 须高于行业中位数，证明资本配置能力", "color": C["spy"]},
    {"num": "04", "title": "股息率前25%", "body": "在同行中股息率排前四分之一，确保持有实际现金回报", "color": C["accent"]},
]

cr_cols = st.columns(4)
for col, cr in zip(cr_cols, criteria):
    with col:
        st.markdown(f"""<div class="holding-row" style="flex-direction:column;align-items:flex-start;padding:14px">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:{cr['color']};font-weight:900">{cr['num']}</div>
            <div style="font-size:13px;font-weight:700;color:{cr['color']};margin:4px 0">{cr['title']}</div>
            <div style="font-size:11px;color:{C['muted']};line-height:1.6">{cr['body']}</div>
        </div>""", unsafe_allow_html=True)
