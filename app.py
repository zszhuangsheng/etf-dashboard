import streamlit as st

st.set_page_config(
    page_title="ETF 退休规划 Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 全局样式 ──────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Noto+Sans+SC:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans SC', sans-serif;
    background-color: #07090e;
    color: #cdd6e0;
}
.stMetric { background: #0c1018; border: 1px solid #1c2535; border-radius: 8px; padding: 16px; }
.stMetric label { color: #4e6278 !important; font-size: 11px !important; letter-spacing: 2px; }
.stMetric [data-testid="stMetricValue"] { color: #38bdf8 !important; font-size: 28px !important; font-family: 'IBM Plex Mono', monospace; }
</style>
""", unsafe_allow_html=True)

# ── 首页内容 ──────────────────────────────────────
st.markdown("## 📈 ETF 退休规划 Dashboard")
st.markdown("##### 基于真实市场数据的 SCHD · SPY 分析工具")
st.divider()

col1, col2, col3 = st.columns(3)
col1.info("👈 左边导航栏选择模块")
col2.info("📊 数据每日美股收盘后自动更新")
col3.info("🔄 所有图表支持交互缩放")

st.markdown("""
### 包含模块（8个分析章节）
| 模块 | 内容 |
|------|------|
| ◈ 执行摘要 | 核心研究发现、关键 CAGR 指标、投资者定位矩阵 |
| 📉 风险回调 | 回撤深度分析、熊市对比、风险指标、恢复时间详解 |
| 📈 收益分析 | 年度收益率、月度热力图、DCA 模拟 |
| ⚖️ SCHD vs SPY | 总回报对比、雷达图、熊市事件、场景解析 |
| 🎯 买入策略 | 金字塔加仓模型，小跌小买大跌大买 |
| 🏖️ 退休规划 | 个人化参数，预测退休资产和月收入 |
| 📊 持仓分析 | 前10大持仓深度分析、股息贵族、散点图 |
| ◆ 投资结论 | SPY vs SCHD 评分、六大场景推荐、配置建议 |
""")
