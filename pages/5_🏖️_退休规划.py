"""
pages/5_🏖️_退休规划.py
个人化退休规划模拟器 —— 核心交互页面
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data.calculator import simulate_retirement, find_retirement_year

# ── 页面配置 ──────────────────────────────────────
st.set_page_config(page_title="退休规划", page_icon="🏖️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&family=Noto+Sans+SC:wght@400;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans SC', sans-serif; background:#07090e; color:#cdd6e0; }
.metric-card { background:#0c1018; border:1px solid #1c2535; border-radius:10px; padding:20px; text-align:center; }
.metric-value { font-family:'IBM Plex Mono',monospace; font-size:26px; font-weight:700; }
.metric-label { font-size:10px; color:#4e6278; letter-spacing:2px; margin-top:4px; }
h1, h2, h3 { color: #cdd6e0; }
</style>
""", unsafe_allow_html=True)

# ── 颜色常量 ──────────────────────────────────────
C = {
    "schd":   "#38bdf8",
    "spy":    "#f59e0b",
    "green":  "#4ade80",
    "red":    "#f87171",
    "accent": "#a3e635",
    "bg":     "#07090e",
    "card":   "#0c1018",
    "border": "#1c2535",
    "muted":  "#4e6278",
    "text":   "#cdd6e0",
}

# ══════════════════════════════════════════════════
# 侧边栏：参数输入
# ══════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚙️ 个人参数设置")
    st.divider()

    current_age = st.slider("📅 当前年龄", 25, 55, 30, 1)
    retire_age  = st.slider("🏖️ 目标退休年龄", 45, 70, 60, 1)
    years       = retire_age - current_age

    st.divider()

    current_assets = st.number_input(
        "💰 现有可投资资产（$）",
        min_value=0, max_value=5_000_000,
        value=100_000, step=10_000,
        format="%d"
    )
    monthly_invest = st.number_input(
        "📥 每月定投金额（$）",
        min_value=0, max_value=50_000,
        value=1_000, step=100,
        format="%d"
    )

    st.divider()

    target_monthly = st.number_input(
        "🎯 退休后月收入目标（$）",
        min_value=1_000, max_value=100_000,
        value=10_000, step=500,
        format="%d"
    )

    st.divider()
    st.markdown("**进阶参数**")

    annual_return   = st.slider("年化总回报假设", 6.0, 15.0, 10.0, 0.5, format="%.1f%%") / 100
    dividend_growth = st.slider("SCHD 股息增长率", 5.0, 15.0, 10.0, 0.5, format="%.1f%%") / 100
    initial_yield   = st.slider("SCHD 当前股息率", 2.0, 6.0, 3.5, 0.1, format="%.1f%%") / 100

# ══════════════════════════════════════════════════
# 计算
# ══════════════════════════════════════════════════
if years <= 0:
    st.error("退休年龄必须大于当前年龄")
    st.stop()

df = simulate_retirement(
    current_assets   = current_assets,
    monthly_invest   = monthly_invest,
    years            = years,
    annual_return    = annual_return,
    dividend_yield   = initial_yield,
    dividend_growth  = dividend_growth,
)

result      = df.iloc[-1]
target_info = find_retirement_year(df, target_monthly)
total_invested = current_assets + monthly_invest * 12 * years

# ══════════════════════════════════════════════════
# 页面标题
# ══════════════════════════════════════════════════
st.markdown(f"# 🏖️ 退休规划模拟器")
st.markdown(f"##### {current_age} 岁 → {retire_age} 岁 · {years} 年投资计划")
st.divider()

# ══════════════════════════════════════════════════
# 关键指标卡片
# ══════════════════════════════════════════════════
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color:{C['schd']}">${result['total_assets']:,.0f}</div>
        <div class="metric-label">退休时预计总资产</div>
    </div>""", unsafe_allow_html=True)

with c2:
    color = C["green"] if result["monthly_income"] >= target_monthly else C["red"]
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color:{color}">${result['monthly_income']:,.0f}</div>
        <div class="metric-label">退休时月股息收入</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color:{C['accent']}">{result['yield_on_cost']}%</div>
        <div class="metric-label">届时 Yield on Cost</div>
    </div>""", unsafe_allow_html=True)

with c4:
    gain = result["total_assets"] / total_invested if total_invested > 0 else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color:{C['spy']}">{gain:.1f}x</div>
        <div class="metric-label">总投入倍数（含本金）</div>
    </div>""", unsafe_allow_html=True)

st.markdown("")

# ══════════════════════════════════════════════════
# 达标提示
# ══════════════════════════════════════════════════
if target_info["reached"]:
    diff = retire_age - target_info["age"]
    if diff > 0:
        st.success(
            f"🎯 **{target_info['age']} 岁**时月股息将达到 **${target_info['monthly']:,}**，"
            f"比目标退休年龄提前 **{diff} 年**！可以考虑提前 FIRE。"
        )
    elif diff == 0:
        st.success(f"✅ 正好在 **{retire_age} 岁**时达到每月 **${target_monthly:,}** 的目标。")
    else:
        st.warning(
            f"⚠️ 按当前参数，**{target_info['age']} 岁**才能达到月收入目标，"
            f"比计划退休晚 **{-diff} 年**。建议增加月定投或降低目标。"
        )
else:
    st.error(
        f"❌ 按当前参数，{retire_age} 岁时月股息约 **${result['monthly_income']:,}**，"
        f"仍未达到 **${target_monthly:,}** 目标。建议增加月定投金额。"
    )

st.divider()

# ══════════════════════════════════════════════════
# 图表区：资产增长 + 月收入
# ══════════════════════════════════════════════════
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### 📈 资产增长曲线")

    # 计算总投入线
    df["cumulative_invested"] = current_assets + df["year"] * monthly_invest * 12

    fig_assets = go.Figure()

    # 总资产面积图
    fig_assets.add_trace(go.Scatter(
        x=df["age"], y=df["total_assets"],
        name="总资产",
        fill="tozeroy",
        line=dict(color=C["schd"], width=2),
        fillcolor=f"rgba(56,189,248,0.15)",
    ))

    # 总投入线
    fig_assets.add_trace(go.Scatter(
        x=df["age"], y=df["cumulative_invested"],
        name="累计投入本金",
        line=dict(color=C["muted"], width=1.5, dash="dash"),
    ))

    # 目标线
    target_assets = target_monthly * 12 / initial_yield
    fig_assets.add_hline(
        y=target_assets,
        line_dash="dot", line_color=C["accent"],
        annotation_text=f"达标所需资产 ${target_assets:,.0f}",
        annotation_font_color=C["accent"],
        annotation_font_size=10,
    )

    fig_assets.update_layout(
        plot_bgcolor=C["card"], paper_bgcolor=C["bg"],
        font_color=C["muted"], font_size=11,
        legend=dict(orientation="h", y=-0.15, font_size=10),
        margin=dict(t=20, b=40, l=10, r=10),
        xaxis=dict(
            title="年龄", gridcolor="#1c2535",
            tickfont_color=C["muted"],
        ),
        yaxis=dict(
            title="美元", gridcolor="#1c2535",
            tickfont_color=C["muted"],
            tickformat="$,.0f",
        ),
        hovermode="x unified",
    )
    st.plotly_chart(fig_assets, use_container_width=True)

with col_right:
    st.markdown("#### 💰 月股息收入增长")

    fig_income = go.Figure()

    fig_income.add_trace(go.Bar(
        x=df["age"], y=df["monthly_income"],
        name="月股息",
        marker_color=[
            C["green"] if v >= target_monthly else C["schd"]
            for v in df["monthly_income"]
        ],
        opacity=0.85,
    ))

    fig_income.add_hline(
        y=target_monthly,
        line_dash="dot", line_color=C["red"],
        annotation_text=f"目标 ${target_monthly:,}/月",
        annotation_font_color=C["red"],
        annotation_font_size=10,
    )

    fig_income.update_layout(
        plot_bgcolor=C["card"], paper_bgcolor=C["bg"],
        font_color=C["muted"], font_size=11,
        legend=dict(orientation="h", y=-0.15, font_size=10),
        margin=dict(t=20, b=40, l=10, r=10),
        xaxis=dict(title="年龄", gridcolor="#1c2535", tickfont_color=C["muted"]),
        yaxis=dict(
            title="美元/月", gridcolor="#1c2535",
            tickfont_color=C["muted"], tickformat="$,.0f",
        ),
        hovermode="x unified",
    )
    st.plotly_chart(fig_income, use_container_width=True)

# ══════════════════════════════════════════════════
# Yield on Cost 可视化
# ══════════════════════════════════════════════════
st.markdown("#### 🔁 Yield on Cost 复利效应")
st.caption("持有越久，早期买入成本对应的股息率越高，这是 SCHD 最强大的长期优势")

fig_yoc = go.Figure()

fig_yoc.add_trace(go.Scatter(
    x=df["age"], y=df["yield_on_cost"],
    name="Yield on Cost",
    fill="tozeroy",
    line=dict(color=C["accent"], width=2.5),
    fillcolor="rgba(163,230,53,0.12)",
))

# 参考线
for y_val, label, color in [
    (initial_yield * 100, f"当前名义股息率 {initial_yield*100:.1f}%", C["muted"]),
    (10, "10% YoC", C["spy"]),
    (20, "20% YoC", C["green"]),
]:
    fig_yoc.add_hline(
        y=y_val, line_dash="dash", line_color=color,
        annotation_text=label, annotation_font_color=color, annotation_font_size=10,
    )

fig_yoc.update_layout(
    plot_bgcolor=C["card"], paper_bgcolor=C["bg"],
    font_color=C["muted"], font_size=11,
    height=220,
    margin=dict(t=10, b=40, l=10, r=10),
    xaxis=dict(title="年龄", gridcolor="#1c2535", tickfont_color=C["muted"]),
    yaxis=dict(title="Yield on Cost %", gridcolor="#1c2535", tickfont_color=C["muted"], ticksuffix="%"),
)
st.plotly_chart(fig_yoc, use_container_width=True)

# ══════════════════════════════════════════════════
# 数据明细表
# ══════════════════════════════════════════════════
with st.expander("📋 查看逐年详细数据"):
    display_df = df[["age", "total_assets", "schd_assets",
                      "yield_on_cost", "monthly_income", "annual_dividend"]].copy()
    display_df.columns = ["年龄", "总资产($)", "SCHD部分($)",
                           "YoC(%)", "月收入($)", "年股息($)"]
    display_df = display_df.set_index("年龄")

    # 高亮达标行
    def highlight_target(row):
        if row["月收入($)"] >= target_monthly:
            return ["background-color: rgba(74,222,128,0.1)"] * len(row)
        return [""] * len(row)

    st.dataframe(
        display_df.style
            .apply(highlight_target, axis=1)
            .format({
                "总资产($)":   "${:,.0f}",
                "SCHD部分($)": "${:,.0f}",
                "YoC(%)":     "{:.1f}%",
                "月收入($)":   "${:,.0f}",
                "年股息($)":   "${:,.0f}",
            }),
        use_container_width=True,
        height=400,
    )

# ══════════════════════════════════════════════════
# 关键提示
# ══════════════════════════════════════════════════
st.divider()
st.markdown("#### 💡 关于这个模拟的重要说明")

n1, n2, n3 = st.columns(3)
n1.info("**假设基础**\n\nSCHD 历史年化总回报约 11.5%，股息增长率约 10%/年，均基于 2012–2024 历史数据。未来不保证重复历史。")
n2.warning("**未计入的成本**\n\n美国股息预提税（新加坡居民 15%）、通货膨胀对购买力的侵蚀、市场大跌期间的心理压力。")
n3.success("**最大的变量**\n\n坚持定投的纪律。模型假设每月固定投入，现实中市场下跌 30% 时能否按计划加仓，决定了最终结果。")
