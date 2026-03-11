"""
pages/0_◈_执行摘要.py
核心研究发现、关键指标、投资者定位矩阵
"""
import streamlit as st
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data.fetcher import fetch_both, fetch_info

st.set_page_config(page_title="执行摘要", page_icon="◈", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&family=Noto+Sans+SC:wght@400;700;900&display=swap');
html, body, [class*="css"] { font-family:'Noto Sans SC',sans-serif; background:#07090e; color:#cdd6e0; }
.metric-card { background:#0c1018; border:1px solid #1c2535; border-radius:10px; padding:16px; text-align:center; }
.metric-val  { font-family:'IBM Plex Mono',monospace; font-size:24px; font-weight:700; }
.metric-lbl  { font-size:10px; color:#4e6278; letter-spacing:1px; margin-top:4px; }
.metric-sub  { font-size:10px; color:#4e6278; margin-top:2px; }
.finding-card { background:#0c1018; border:1px solid #1c2535; border-radius:10px; padding:16px; }
.finding-num  { font-family:'IBM Plex Mono',monospace; font-size:11px; color:#a3e635; font-weight:900; }
.finding-title{ font-size:13px; font-weight:700; color:#cdd6e0; margin:6px 0 4px; }
.finding-body { font-size:12px; color:#4e6278; line-height:1.7; }
.phase-card  { background:#0c1018; border:1px solid #1c2535; border-radius:10px; padding:16px; border-left:3px solid; }
.phase-label { font-size:11px; font-weight:700; margin-bottom:6px; }
.phase-alloc { font-size:14px; font-weight:800; color:#cdd6e0; margin-bottom:4px; }
.phase-note  { font-size:11px; color:#4e6278; }
</style>""", unsafe_allow_html=True)

C = {"schd":"#38bdf8","spy":"#f59e0b","green":"#4ade80","red":"#f87171",
     "accent":"#a3e635","bg":"#07090e","card":"#0c1018","border":"#1c2535","muted":"#4e6278"}

st.markdown("# ◈ 执行摘要")
st.markdown("##### SCHD · SPY 深度研究核心发现")
st.divider()

# ── 加载数据 ──────────────────────────────────────
with st.spinner("正在加载数据..."):
    schd_df, spy_df = fetch_both()

if schd_df.empty or spy_df.empty:
    st.error("数据加载失败，请稍后刷新重试")
    st.stop()

# 计算 CAGR
years = (schd_df.index.max() - schd_df.index.min()).days / 365.25
schd_cagr = ((schd_df["close"].iloc[-1] / schd_df["close"].iloc[0]) ** (1/years) - 1) * 100
spy_cagr = ((spy_df["close"].iloc[-1] / spy_df["close"].iloc[0]) ** (1/years) - 1) * 100

# ══════════════════════════════════════════════════
# 关键指标
# ══════════════════════════════════════════════════
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="metric-card" style="border-top:3px solid {C['schd']}">
        <div class="metric-val" style="color:{C['schd']}">{schd_cagr:.1f}%</div>
        <div class="metric-lbl">SCHD CAGR</div>
        <div class="metric-sub">含股息再投资</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card" style="border-top:3px solid {C['spy']}">
        <div class="metric-val" style="color:{C['spy']}">{spy_cagr:.1f}%</div>
        <div class="metric-lbl">SPY CAGR</div>
        <div class="metric-sub">含股息再投资</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-card" style="border-top:3px solid {C['green']}">
        <div class="metric-val" style="color:{C['green']}">~3.5%</div>
        <div class="metric-lbl">SCHD 股息率</div>
        <div class="metric-sub">vs SPY ~1.4%</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="metric-card" style="border-top:3px solid {C['accent']}">
        <div class="metric-val" style="color:{C['accent']}">-5.8%</div>
        <div class="metric-lbl">2022 防御性</div>
        <div class="metric-sub">SPY 同期 -18.2%</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════
# 核心研究发现
# ══════════════════════════════════════════════════
st.markdown("#### 核心研究发现")

findings = [
    {
        "num": "01", "title": "收益模式差异",
        "body": f"SPY CAGR {spy_cagr:.1f}%，SCHD {schd_cagr:.1f}%，差距约2%。但 SCHD 靠高股息（~3.5%）和稳定增长弥补价差，长期持股舒适度更高。"
    },
    {
        "num": "02", "title": "回调风险特征",
        "body": "60%+ 的回调幅度不超过10%，仅 COVID（2020）触及 -27% 极端区间。SCHD 选股质量高，深度回调概率极低。"
    },
    {
        "num": "03", "title": "熊市防御优势",
        "body": "2022年加息周期 SCHD 仅跌 -5.8%，SPY 跌 -18.2%。Beta 约 0.75，系统性风险显著低于市场基准。"
    },
    {
        "num": "04", "title": "定投复利效应",
        "body": "每月投入 $500 持续13年，含分红再投资收益率超100%。股息再投资是 SCHD 长期复利的核心引擎。"
    },
]

f1, f2 = st.columns(2)
for i, f in enumerate(findings):
    with f1 if i % 2 == 0 else f2:
        st.markdown(f"""<div class="finding-card">
            <div class="finding-num">{f['num']}</div>
            <div class="finding-title">{f['title']}</div>
            <div class="finding-body">{f['body']}</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("")

st.divider()

# ══════════════════════════════════════════════════
# 投资者定位矩阵
# ══════════════════════════════════════════════════
st.markdown("#### 投资者定位矩阵")

phases = [
    {"phase": "积累期 (20-40岁)", "alloc": "70% SPY + 30% SCHD", "note": "成长优先，SCHD 作压舱石", "color": C["spy"]},
    {"phase": "平衡期 (40-55岁)", "alloc": "50% SPY + 50% SCHD", "note": "增值与现金流并重", "color": C["accent"]},
    {"phase": "分配期 (55岁+)",   "alloc": "20% SPY + 80% SCHD", "note": "现金流主导，低波动", "color": C["schd"]},
]

cols = st.columns(3)
for col, p in zip(cols, phases):
    with col:
        st.markdown(f"""<div class="phase-card" style="border-left-color:{p['color']}">
            <div class="phase-label" style="color:{p['color']}">{p['phase']}</div>
            <div class="phase-alloc">{p['alloc']}</div>
            <div class="phase-note">{p['note']}</div>
        </div>""", unsafe_allow_html=True)
