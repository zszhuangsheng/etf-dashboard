"""
pages/7_◆_投资结论.py
SPY vs SCHD 最终评分、六大场景推荐、综合配置建议
"""
import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

st.set_page_config(page_title="投资结论", page_icon="◆", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&family=Noto+Sans+SC:wght@400;700;900&display=swap');
html, body, [class*="css"] { font-family:'Noto Sans SC',sans-serif; background:#07090e; color:#cdd6e0; }
.verdict-card { background:#0c1018; border:1px solid #1c2535; border-radius:12px; padding:20px; }
.verdict-ticker { font-family:'IBM Plex Mono',monospace; font-size:28px; font-weight:900; letter-spacing:-1px; }
.verdict-score  { font-family:'IBM Plex Mono',monospace; font-size:36px; font-weight:900; opacity:0.35; }
.verdict-sub { font-size:12px; color:#4e6278; margin-top:2px; }
.str-item { font-size:12px; margin-bottom:4px; line-height:1.6; }
.scenario-card { background:#0c1018; border:1px solid #1c2535; border-radius:8px; padding:12px 16px; border-left:3px solid; display:flex; justify-content:space-between; align-items:center; }
.alloc-card { background:rgba(255,255,255,0.02); border:1px solid rgba(163,230,53,0.12); border-radius:10px; padding:16px; text-align:center; }
</style>""", unsafe_allow_html=True)

C = {"schd":"#38bdf8","spy":"#f59e0b","green":"#4ade80","red":"#f87171",
     "accent":"#a3e635","bg":"#07090e","card":"#0c1018","border":"#1c2535","muted":"#4e6278"}

st.markdown("# ◆ 投资结论")
st.markdown("##### SCHD vs SPY 最终评估 · 场景推荐 · 配置建议")
st.divider()

# ══════════════════════════════════════════════════
# SPY vs SCHD 评分卡
# ══════════════════════════════════════════════════
col_spy, col_schd = st.columns(2)

with col_spy:
    st.markdown(f"""<div class="verdict-card" style="border-top:4px solid {C['spy']}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px">
            <div>
                <div class="verdict-ticker" style="color:{C['spy']}">SPY</div>
                <div class="verdict-sub">成长首选</div>
            </div>
            <div class="verdict-score" style="color:{C['spy']}">A+</div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"**:green[优势]**")
    for s in ["科技驱动长期高 CAGR (~13.5%)", "流动性极强，交易成本最低", "S&P500 标准基准，分散度高", "牛市捕获能力强"]:
        st.markdown(f"<div class='str-item'><span style='color:{C[\"green\"]}'>+</span> {s}</div>", unsafe_allow_html=True)

    st.markdown(f"**:red[风险]**")
    for w in ["熊市跌幅大，-18.2% (2022)", "股息低 (1.4%)，退休现金流不足", "科技股集中风险"]:
        st.markdown(f"<div class='str-item'><span style='color:{C[\"red\"]}'>-</span> {w}</div>", unsafe_allow_html=True)

    st.info(f"**最佳场景：** 20-40岁积累期 / 牛市环境")

with col_schd:
    st.markdown(f"""<div class="verdict-card" style="border-top:4px solid {C['schd']}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px">
            <div>
                <div class="verdict-ticker" style="color:{C['schd']}">SCHD</div>
                <div class="verdict-sub">现金流首选</div>
            </div>
            <div class="verdict-score" style="color:{C['schd']}">A</div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"**:green[优势]**")
    for s in ["高股息 (3.5%) + 年增长 ~10%", "熊市防御强，Beta 0.75", "选股质量高，ROE/FCF 筛选", "持股心理舒适度高"]:
        st.markdown(f"<div class='str-item'><span style='color:{C[\"green\"]}'>+</span> {s}</div>", unsafe_allow_html=True)

    st.markdown(f"**:red[风险]**")
    for w in ["牛市跑输 SPY，错过科技溢价", "成长周期中明显落后", "持仓集中度相对高"]:
        st.markdown(f"<div class='str-item'><span style='color:{C[\"red\"]}'>-</span> {w}</div>", unsafe_allow_html=True)

    st.info(f"**最佳场景：** 退休 / 现金流需求 / 熊市环境")

st.divider()

# ══════════════════════════════════════════════════
# 六大投资场景推荐
# ══════════════════════════════════════════════════
st.markdown("#### 六大投资场景推荐")

scenarios = [
    {"icon": "📈", "scene": "资本增值优先",   "winner": "SPY",  "note": "科技+成长驱动，长期 CAGR 更高，适合积累财富阶段"},
    {"icon": "💰", "scene": "退休现金流",     "winner": "SCHD", "note": "3.5% 股息+年增10%，季度稳定派息，替代债券配置"},
    {"icon": "🛡️", "scene": "熊市防御",       "winner": "SCHD", "note": "Beta 0.75，2022年仅跌 -5.8%，下行保护显著"},
    {"icon": "⚡", "scene": "牛市成长捕获",   "winner": "SPY",  "note": "2023-24年 AI 牛市 SPY +26%，SCHD 明显落后"},
    {"icon": "🔄", "scene": "长期定投 (DCA)", "winner": "平手", "note": "两者13年 CAGR 差距约2%，SCHD 持股舒适度更优"},
    {"icon": "📊", "scene": "股债组合替代",   "winner": "SCHD", "note": "高股息+低波动可替代部分债券，比纯债收益更高"},
]

for s in scenarios:
    color = C["spy"] if s["winner"] == "SPY" else C["schd"] if s["winner"] == "SCHD" else C["muted"]
    st.markdown(f"""<div class="scenario-card" style="border-left-color:{color}; margin-bottom:8px">
        <div>
            <span style="font-size:13px;font-weight:700;color:#cdd6e0">{s['icon']} {s['scene']}</span>
            <span style="font-size:12px;color:#4e6278;margin-left:12px">{s['note']}</span>
        </div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:14px;font-weight:900;color:{color};min-width:48px;text-align:right">{s['winner']}</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════
# 综合配置建议
# ══════════════════════════════════════════════════
st.markdown("#### 综合配置建议")

alloc_cols = st.columns(3)
allocations = [
    {"phase": "20-40岁 积累期",  "alloc": "70% SPY\n30% SCHD", "note": "成长主导，分红补充，最大化长期复利", "color": C["spy"]},
    {"phase": "40-55岁 平衡期",  "alloc": "50% SPY\n50% SCHD", "note": "平衡增值与现金流，组合波动降低约20%", "color": C["accent"]},
    {"phase": "55岁+ 分配期",    "alloc": "20% SPY\n80% SCHD", "note": "股息收入为主，保持购买力，稳健传承", "color": C["schd"]},
]

for col, a in zip(alloc_cols, allocations):
    with col:
        st.markdown(f"""<div class="alloc-card">
            <div style="font-size:12px;color:{a['color']};font-weight:700;margin-bottom:10px">{a['phase']}</div>
            <div style="font-size:16px;font-weight:900;color:#cdd6e0;white-space:pre-line;line-height:1.6;margin-bottom:10px">{a['alloc']}</div>
            <div style="font-size:11px;color:#4e6278;line-height:1.6">{a['note']}</div>
        </div>""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════
# 底部总结
# ══════════════════════════════════════════════════
st.markdown("""
#### 💡 一句话总结

> **SPY 让你变富，SCHD 让你退休。** 两者不是二选一的关系，而是人生不同阶段的最佳搭档。
> 年轻时用 SPY 追逐成长，中年后逐步转向 SCHD 建立现金流管道，最终实现股息覆盖生活支出的财务自由。
""")
