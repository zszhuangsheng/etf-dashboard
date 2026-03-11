# 📈 ETF 退休规划 Dashboard

基于真实市场数据的 SCHD · SPY 分析工具，数据每日自动更新。

## 包含模块

| 页面 | 内容 |
|------|------|
| 📉 回撤分析 | 历史回撤深度、概率分布、恢复时间 |
| ⚖️ SCHD vs SPY | 总回报对比、年度收益、风险指标 |
| 🏖️ 退休规划 | 个人化参数，预测退休资产和月收入 |

---

## 🚀 部署步骤（从零到上线约 20 分钟）

### 第一步：本地测试

```bash
# 1. 克隆或下载这个项目
git clone https://github.com/你的用户名/etf-dashboard.git
cd etf-dashboard

# 2. 安装依赖
pip install -r requirements.txt

# 3. 本地运行
streamlit run app.py
# 浏览器会自动打开 http://localhost:8501
```

### 第二步：推到 GitHub

```bash
# 如果还没有 GitHub 账号，先去 github.com 注册

# 在 GitHub 创建新仓库，名字叫 etf-dashboard
# 然后：
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/你的用户名/etf-dashboard.git
git push -u origin main
```

### 第三步：Streamlit Cloud 一键部署

1. 去 **https://streamlit.io/cloud** 用 GitHub 账号登录
2. 点击 **"New app"**
3. 选择你的 `etf-dashboard` 仓库
4. Main file path 填：`app.py`
5. 点击 **Deploy**
6. 等待约 2 分钟，得到公开网址：`https://你的用户名-etf-dashboard-app-xxxxx.streamlit.app`

**完成！** 把这个网址发给朋友，手机电脑都能打开。

---

## 数据说明

- 数据来源：Yahoo Finance（通过 yfinance 库）
- 更新频率：每次访问时自动检查，缓存 1 小时
- 覆盖范围：SCHD 自 2011年 上市以来全部历史数据

## 技术栈

- **前端 + 后端**：Python + Streamlit（无需 JavaScript）
- **数据可视化**：Plotly
- **数据获取**：yfinance
- **部署**：Streamlit Cloud（免费）
