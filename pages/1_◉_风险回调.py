"""
pages/1_◉_风险回调.py
SCHD 历史回撤深度、概率分布、恢复时间、风险指标、熊市对比
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data.fetcher import fetch_history, fetch_both, calc_drawdown_buckets

st.set_page_config(page_title="风险回调", page_icon="◉", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&family=Noto+Sans+SC:wght@400;700&display=swap');
html, body, [class*="css"] { font-family:'Noto Sans SC',sans-serif; background:#07090e; color:#cdd6e0; }
.metric-card { background:#0c1018; border:1px solid #1c2535; border-radius:10px; padding:14px; text-align:center; }
.metric-val  { font-family:'IBM Plex Mono',monospace; font-size:18px; font-weight:700; }
.metric-lbl  { font-size:10px; color:#4e6278; letter-spacing:1px; margin-top:4px; }
.recovery-card { background:#0c1018; border:1px solid #1c2535; border-left:3px solid; border-radius:8px; padding:14px 16px; margin-bottom:10px; }
.insight-box { background:rgba(163,230,53,0.05); border:1px solid rgba(163,230,53,0.15); border-radius:10px; padding:16px 18px; }
</style>""", unsafe_allow_html=True)

C = {"schd":"#38bdf8","spy":"#f59e0b","green":"#4ade80","red":"#f87171",
     "accent":"#a3e635","bg":"#07090e","card":"#0c1018","border":"#1c2535","muted":"#4e6278"}

st.markdown("# ◉ 风险与回调分析")
st.markdown("##### SCHD 历史回撤 · 概率分布 · 恢复时间 · 风险指标")
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
st.markdown("#### SCHD 历史回撤深度（从历史最高点）")

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
    height=280, margin=dict(t=10, b=20, l=10, r=10),
    xaxis=dict(gridcolor=C["border"]), yaxis=dict(gridcolor=C["border"], ticksuffix="%"),
    hovermode="x unified",
)
st.plotly_chart(fig_dd, use_container_width=True)

# ══════════════════════════════════════════════════
# 概率分布 & 四大熊市对比（并排）
# ══════════════════════════════════════════════════
col_prob, col_bear = st.columns(2)

bucket_events = calc_drawdown_buckets(df)
BUCKET_ORDER  = ["< 5%", "5\u201310%", "10\u201315%", "15\u201320%", "20\u201330%", "> 30%"]
BUCKET_COLORS = ["#4ade80", "#86efac", "#f59e0b", "#fb923c", "#f87171", "#7f1d1d"]

with col_prob:
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
            orientation="h", marker_color=BUCKET_COLORS,
            text=prob_df["prob"].apply(lambda x: f"{x:.0f}%"),
            textposition="outside",
        ))
        fig_prob.update_layout(
            plot_bgcolor=C["card"], paper_bgcolor=C["bg"], font_color=C["muted"],
            height=300, margin=dict(t=10, b=20, l=10, r=40),
            xaxis=dict(gridcolor=C["border"], ticksuffix="%"),
            yaxis=dict(gridcolor=C["border"]),
            showlegend=False,
        )
        st.plotly_chart(fig_prob, use_container_width=True)
    else:
        st.info("数据不足以计算完整的回调事件")

with col_bear:
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
        barmode="group", height=300, margin=dict(t=10, b=20, l=10, r=30),
        xaxis=dict(gridcolor=C["border"], ticksuffix="%", range=[-35, 0]),
        yaxis=dict(gridcolor=C["border"]),
        legend=dict(orientation="h", y=-0.15),
    )
    st.plotly_chart(fig_bear, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════
# 风险指标对照
# ══════════════════════════════════════════════════
st.markdown("#### 风险指标对照")

risk_metrics = [
    {"label": "Beta（市场风险）", "schd": "~0.75",  "spy": "1.00",  "winner": "SCHD"},
    {"label": "年化波动率",       "schd": "~13%",   "spy": "~16%",  "winner": "SCHD"},
    {"label": "最大回撤",         "schd": "-27%",   "spy": "-33%",  "winner": "SCHD"},
    {"label": "夏普比率（近3Y）",  "schd": "~0.71",  "spy": "~0.82", "winner": "SPY"},
]

risk_cols = st.columns(4)
for col, m in zip(risk_cols, risk_metrics):
    schd_color = C["schd"] if m["winner"] == "SCHD" else "#cdd6e0"
    spy_color = C["spy"] if m["winner"] == "SPY" else "#cdd6e0"
    schd_weight = "700" if m["winner"] == "SCHD" else "400"
    spy_weight = "700" if m["winner"] == "SPY" else "400"
    with col:
        st.markdown(f"""<div class="metric-card">
            <div style="font-size:11px;color:{C['muted']};margin-bottom:10px;line-height:1.4">{m['label']}</div>
            <div style="display:flex;justify-content:space-around">
                <div style="text-align:center">
                    <div style="font-family:'IBM Plex Mono',monospace;font-size:15px;font-weight:{schd_weight};color:{schd_color}">{m['schd']}</div>
                    <div style="font-size:9px;color:{C['muted']};margin-top:2px">SCHD</div>
                </div>
                <div style="text-align:center">
                    <div style="font-family:'IBM Plex Mono',monospace;font-size:15px;font-weight:{spy_weight};color:{spy_color}">{m['spy']}</div>
                    <div style="font-size:9px;color:{C['muted']};margin-top:2px">SPY</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════
# 回调幅度 × 恢复时间 详细分析
# ══════════════════════════════════════════════════
st.markdown("#### 回调幅度 × 恢复时间")
st.caption("从跌至谷底到价格重回前高所需月数（含股息再投资加速恢复）")

RECOVERY_DATA = [
    {
        "bucket": "< 5%", "color": "#4ade80", "prob": "35%",
        "avgMonths": 2, "maxMonths": 4, "minMonths": 1,
        "note": "市场噪音级别，通常 1\u20132 个月自然回升",
        "events": ["日常波动，几乎每季度出现"],
        "psychLevel": "极低", "psychColor": "#4ade80",
        "divHelp": "股息贡献有限，主要靠价格自然反弹",
    },
    {
        "bucket": "5\u201310%", "color": "#86efac", "prob": "29%",
        "avgMonths": 4, "maxMonths": 7, "minMonths": 2,
        "note": "季节性或情绪性回调，平均 3\u20135 个月恢复",
        "events": ["2012-05（-5.8%，3个月恢复）", "2014-10（-6.2%，4个月恢复）"],
        "psychLevel": "低", "psychColor": "#86efac",
        "divHelp": "股息再投资可额外降低成本约 0.5\u20131%",
    },
    {
        "bucket": "10\u201315%", "color": "#f59e0b", "prob": "19%",
        "avgMonths": 7, "maxMonths": 11, "minMonths": 4,
        "note": "宏观事件冲击，通常半年内恢复，需要耐心",
        "events": ["2015-08 A股冲击（-11.2%，6个月恢复）", "2018-12 缩表危机（-12.6%，5个月恢复）"],
        "psychLevel": "中", "psychColor": "#f59e0b",
        "divHelp": "季度股息再投可额外积累 ~1.5% 仓位，加速恢复",
    },
    {
        "bucket": "15\u201320%", "color": "#fb923c", "prob": "10%",
        "avgMonths": 11, "maxMonths": 15, "minMonths": 7,
        "note": "较深熊市区间，通常需要 8\u201314 个月，考验持仓意志",
        "events": ["2022-09 加息周期（-14.8%，约10个月恢复）"],
        "psychLevel": "高", "psychColor": "#fb923c",
        "divHelp": "2\u20133 次股息再投可摊低成本 ~2\u20133%，明显缩短恢复时间",
    },
    {
        "bucket": "20\u201330%", "color": "#f87171", "prob": "5%",
        "avgMonths": 18, "maxMonths": 24, "minMonths": 12,
        "note": "重大系统性危机，需要 12\u201324 个月，但 SCHD 防御性使其快于大盘",
        "events": ["2020-03 COVID（-27.3%，约6个月恢复，V形反弹例外）"],
        "psychLevel": "极高", "psychColor": "#f87171",
        "divHelp": "持续再投资是这阶段最重要的工具，越跌越买积累更多份额",
    },
    {
        "bucket": "> 30%", "color": "#7f1d1d", "prob": "2%",
        "avgMonths": 30, "maxMonths": 48, "minMonths": 20,
        "note": "极端黑天鹅事件，历史上 SCHD 未曾触及，理论参考",
        "events": ["历史上 SCHD 未发生过"],
        "psychLevel": "崩溃级", "psychColor": "#7f1d1d",
        "divHelp": "理论上高股息特性会加速恢复，但需要极强的心理定力",
    },
]

for r in RECOVERY_DATA:
    bar_pct = min(r["avgMonths"] / 30 * 100, 100)

    st.markdown(f"""<div class="recovery-card" style="border-left-color:{r['color']}">
        <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;margin-bottom:10px">
            <div style="min-width:80px">
                <div style="font-size:15px;font-weight:900;color:{r['color']}">{r['bucket']}</div>
                <div style="font-size:10px;color:{C['muted']};margin-top:2px">发生概率 {r['prob']}</div>
            </div>
            <div style="flex:1;min-width:180px">
                <div style="display:flex;justify-content:space-between;font-size:10px;color:{C['muted']};margin-bottom:4px">
                    <span>平均恢复</span>
                    <span style="color:{r['color']};font-weight:700">{r['avgMonths']} 个月</span>
                </div>
                <div style="height:6px;background:#131c28;border-radius:3px">
                    <div style="height:100%;width:{bar_pct}%;background:linear-gradient(90deg,{r['color']}99,{r['color']});border-radius:3px"></div>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:9px;color:{C['muted']};margin-top:3px">
                    <span>最短 {r['minMonths']}月</span>
                    <span>最长 {r['maxMonths']}月</span>
                </div>
            </div>
            <div style="text-align:center;min-width:60px">
                <div style="font-size:9px;color:{C['muted']};margin-bottom:3px">心理压力</div>
                <div style="font-size:11px;font-weight:700;color:{r['psychColor']};background:{r['psychColor']}15;border:1px solid {r['psychColor']}40;border-radius:4px;padding:2px 8px">{r['psychLevel']}</div>
            </div>
        </div>
        <div style="border-top:1px solid {C['border']};padding-top:8px;display:grid;grid-template-columns:1fr 1fr;gap:12px">
            <div>
                <div style="font-size:9px;color:{C['muted']};letter-spacing:1px;margin-bottom:4px">历史案例</div>
                {''.join(f"<div style='font-size:11px;color:#cdd6e0;margin-bottom:2px'>· {e}</div>" for e in r['events'])}
            </div>
            <div>
                <div style="font-size:9px;color:{C['muted']};letter-spacing:1px;margin-bottom:4px">股息再投资的作用</div>
                <div style="font-size:11px;color:#86efac;line-height:1.6">{r['divHelp']}</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# 恢复时间的关键规律
# ══════════════════════════════════════════════════
st.markdown("")
st.markdown(f"""<div class="insight-box">
    <div style="font-size:11px;font-weight:700;color:{C['accent']};margin-bottom:12px;letter-spacing:1px">◆ 恢复时间的关键规律</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
        <div style="font-size:12px;color:{C['muted']};line-height:1.8">
            <span style="color:{C['green']};font-weight:700">① 股息加速恢复：</span>SCHD 的高股息在下跌期间持续再投资，等于在低价时强制买入更多份额，实际恢复速度比纯价格回升快 20–30%
        </div>
        <div style="font-size:12px;color:{C['muted']};line-height:1.8">
            <span style="color:{C['green']};font-weight:700">② COVID 是例外：</span>2020 年 -27% 但仅 6 个月恢复，因为政策刺激驱动 V 形反弹，不能作为深度回调的平均参考
        </div>
        <div style="font-size:12px;color:{C['muted']};line-height:1.8">
            <span style="color:{C['green']};font-weight:700">③ 恢复≠解套：</span>价格回前高只是解套，若算上机会成本（持有期间没参与的涨幅），深度回调的真实代价更大，越早买入越重要
        </div>
        <div style="font-size:12px;color:{C['muted']};line-height:1.8">
            <span style="color:{C['green']};font-weight:700">④ 60% 回调在 5 月内恢复：</span>历史上超过 60% 的回调事件在 5 个月内价格重回前高，持有不动是大多数情况下的最优策略
        </div>
    </div>
</div>""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════
# 回调事件明细表
# ══════════════════════════════════════════════════
if not bucket_events.empty:
    with st.expander("📋 查看历史回调事件明细"):
        display = bucket_events[["peak_date", "trough_date", "recover_date",
                                  "max_drawdown", "recover_months", "bucket"]].copy()
        display.columns = ["峰值日期", "谷底日期", "恢复日期", "最大回撤", "恢复月数", "回撤区间"]
        display["最大回撤"] = display["最大回撤"].apply(lambda x: f"{x:.1f}%")
        display = display.sort_values("峰值日期", ascending=False)
        st.dataframe(display.reset_index(drop=True), use_container_width=True, height=300)
