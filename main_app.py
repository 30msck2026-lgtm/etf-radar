import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import os

st.set_page_config(page_title="美股細分行業 ETF 深度監控與轉勢雷達", page_icon="📈", layout="wide")
DB_FILE = os.path.join(os.path.dirname(__file__), "data", "etf_system.db")

@st.cache_data(ttl=120)
def load_all_dashboard_data():
    conn = sqlite3.connect(DB_FILE)
    date_df = pd.read_sql("SELECT MAX(date) as max_date FROM market_daily_metrics", conn)
    latest_date = date_df["max_date"].iloc[0]
    if not latest_date:
        conn.close()
        return None, None, None, None
        
    # 讀取當日 metrics
    q_metrics = f"""
    SELECT m.*, meta.name, meta.sector, meta.sub_industry, meta.benchmark
    FROM market_daily_metrics m
    JOIN etf_metadata meta ON m.symbol = meta.symbol
    WHERE m.date = '{latest_date}'
    """
    df_metrics = pd.read_sql(q_metrics, conn)
    
    # 讀取大盤宏觀寬度 (S&P 500, Nasdaq 100 歷史與當日)
    df_macro = pd.read_sql("SELECT * FROM macro_breadth ORDER BY date ASC", conn)
    
    # 讀取 11 大板塊代表 ETF 當日走勢
    sectors_q = f"""
    SELECT symbol, close_price, pct_change, momentum_5d, dist_20ma
    FROM market_daily_metrics 
    WHERE symbol IN ('XLK','XLV','XLF','XLI','XLY','XLP','XLE','XLB','XLU','XLRE','XLC') 
      AND date = '{latest_date}'
    """
    df_sectors = pd.read_sql(sectors_q, conn)
    conn.close()
    return df_metrics, df_macro, df_sectors, latest_date

st.title("🏛️ 美股細分行業 ETF 深度監控與市場寬度雷達")
df_metrics, df_macro, df_sectors, latest_date = load_all_dashboard_data()

if df_metrics is None or df_metrics.empty:
    st.info("💡 資料庫尚無數據。請先運行後台腳本：\n1. `python db_manager.py`\n2. `python update_holdings.py`\n3. `python daily_batch.py`")
    st.stop()

# ==========================================
# 圖片 3.A 全局市場層 (Macro Breadth)
# ==========================================
st.markdown(f"## 🌐 A. 全局市場層 (Macro Breadth) — 基準日: `{latest_date}`")

# 1. 標普 500 與 Nasdaq 每日破 52 週新高與新低 (NH - NL)
if df_macro is not None and not df_macro.empty:
    latest_macro = df_macro[df_macro["date"] == latest_date]
    m_cols = st.columns(4)
    for _, row in latest_macro.iterrows():
        idx_n = row["index_name"]
        nh = row["new_highs_count"]
        nl = row["new_lows_count"]
        net = row["net_highs_lows"]
        p50 = row["pct_above_50ma"]
        if "S&P" in idx_n:
            m_cols[0].metric("標普 500 (52週新高 / 新低)", f"{nh} 隻 / {nl} 隻", delta=f"淨新高: {net:+d}")
            m_cols[1].metric("標普 500 站上 50MA 比例", f"{p50}%")
        else:
            m_cols[2].metric("納指 100 (52週新高 / 新低)", f"{nh} 隻 / {nl} 隻", delta=f"淨新高: {net:+d}")
            m_cols[3].metric("納指 100 站上 50MA 比例", f"{p50}%")
            
    # 歷史淨新高淨低走勢曲線
    if len(df_macro["date"].unique()) > 1:
        st.caption("📈 S&P 500 & Nasdaq 每日淨新高 (NH - NL) 走勢曲線")
        fig_macro = px.line(df_macro, x="date", y="net_highs_lows", color="index_name", markers=True)
        fig_macro.add_hline(y=0, line_dash="dash", line_color="gray")
        fig_macro.update_layout(height=260, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_macro, use_container_width=True)

# 2. 板塊強弱分佈：11 大 Sectors 資金流向熱力圖
if df_sectors is not None and not df_sectors.empty:
    st.markdown("#### 🧭 11 大核心板塊 (Sectors) 當日資金流向熱力分佈")
    fig_sector_heat = px.bar(
        df_sectors.sort_values(by="pct_change", ascending=False),
        x="symbol", y="pct_change",
        color="pct_change",
        color_continuous_scale="RdYlGn",
        text="pct_change",
        labels={"pct_change": "漲跌幅 (%)", "symbol": "板塊 ETF"}
    )
    fig_sector_heat.update_traces(texttemplate="%{text:+.2f}%", textposition="outside")
    fig_sector_heat.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_sector_heat, use_container_width=True)

st.markdown("---")

# ==========================================
# 圖片 3.C 轉勢雷達 (Reversal Radar)
# ==========================================
st.markdown("## 🚨 C. 轉勢雷達 (Reversal Radar)")
st.caption("• **右側爆發**：站上 20MA 且內部站上 20MA 股票比例單日激增 20% 以上\n• **左側反轉**：連續 5 日超跌，且當日出現「成交量放大 + 等權率先翻紅 + 內部上漲比率 > 60%」")

radar_alerts = df_metrics[df_metrics["reversal_signal_flag"] != "常規波動"]
if not radar_alerts.empty:
    alert_cols = st.columns(min(len(radar_alerts), 4))
    for i, (_, r) in enumerate(radar_alerts.head(4).iterrows()):
        with alert_cols[i % 4]:
            st.error(f"⚡ **{r['symbol']} ({r['name']})**\n\n"
                     f"• 觸發信號: **{r['reversal_signal_flag']}**\n"
                     f"• ETF 漲跌: `{r['pct_change']:+.2f}%` | 內部等權: `{r['equal_weight_return']:+.2f}%`\n"
                     f"• 距 20MA: `{r['dist_20ma']:+.2f}%` | 內部上漲佔比: `{r['advancing_ratio']}%`\n"
                     f"• 成交量放量比: `{r['volume_ratio']}x`")
else:
    st.success("✅ 今日 Universe 內暫未發現極端轉勢異動，市場維持現有趨勢。")

st.markdown("---")

# ==========================================
# 圖片 3.B 細分子行業篩選層 (Sub-Industry Screener)
# ==========================================
st.markdown("## 🔬 B. 細分子行業篩選層 (Sub-Industry Screener)")

# 側邊欄篩選控件
st.sidebar.header("🎯 複合條件篩選 (Screener Filters)")
all_sectors = list(df_metrics["sector"].unique())
sel_sectors = st.sidebar.multiselect("選擇大板塊 (Sector):", all_sectors, default=all_sectors)

# 排序維度
sort_by = st.sidebar.selectbox("動量 / 均線排行 (Sort By):", [
    "當日升幅 (pct_change)", "5 日動量 (momentum_5d)", "20 日動量 (momentum_20d)",
    "距離 20MA 偏離度 (dist_20ma)", "內部上漲比率 (advancing_ratio)"
])

# 內外背離信號快速過濾
divergence_filter = st.sidebar.selectbox("背離與轉勢過濾:", ["全部", "隱形強勢", "虛胖拉升", "右側爆發", "左側反轉"])
min_adv = st.sidebar.slider("內部最低上漲比例 (%):", 0, 100, 0)
ma20_bias_range = st.sidebar.slider("距 20MA 偏離範圍 (%):", -20.0, 20.0, (-15.0, 15.0))

# 執行篩選
view_df = df_metrics[df_metrics["sector"].isin(sel_sectors)]
view_df = view_df[
    (view_df["advancing_ratio"] >= min_adv) &
    (view_df["dist_20ma"] >= ma20_bias_range[0]) &
    (view_df["dist_20ma"] <= ma20_bias_range[1])
]
if divergence_filter != "全部":
    view_df = view_df[view_df["reversal_signal_flag"].str.contains(divergence_filter, na=False)]

# 映射排序欄位
sort_map = {
    "當日升幅 (pct_change)": "pct_change",
    "5 日動量 (momentum_5d)": "momentum_5d",
    "20 日動量 (momentum_20d)": "momentum_20d",
    "距離 20MA 偏離度 (dist_20ma)": "dist_20ma",
    "內部上漲比率 (advancing_ratio)": "advancing_ratio"
}
view_df = view_df.sort_values(by=sort_map[sort_by], ascending=False)

# 顯示明細表格
disp_cols = [
    "symbol", "name", "sector", "sub_industry", "close_price",
    "pct_change", "momentum_5d", "momentum_20d",
    "equal_weight_return", "ew_vs_cap_spread",
    "dist_20ma", "dist_50ma", "dist_200ma",
    "advancing_ratio", "above_20ma_ratio", "reversal_signal_flag"
]
rename_map = {
    "symbol": "代號", "name": "名稱", "sector": "大板塊", "sub_industry": "細分子行業",
    "close_price": "收盤價", "pct_change": "當日升幅", "momentum_5d": "5日動量", "momentum_20d": "20日動量",
    "equal_weight_return": "等權升幅", "ew_vs_cap_spread": "等權差額",
    "dist_20ma": "距20MA", "dist_50ma": "距50MA", "dist_200ma": "距200MA",
    "advancing_ratio": "內部上漲家數%", "above_20ma_ratio": "站上20MA%", "reversal_signal_flag": "轉勢信號"
}

def style_screener(st_df):
    return st_df.format({
        "收盤價": "${:.2f}",
        "當日升幅": "{:+.2f}%",
        "5日動量": "{:+.2f}%",
        "20日動量": "{:+.2f}%",
        "等權升幅": "{:+.2f}%",
        "等權差額": "{:+.2f}%",
        "距20MA": "{:+.2f}%",
        "距50MA": "{:+.2f}%",
        "距200MA": "{:+.2f}%",
        "內部上漲家數%": "{:.1f}%",
        "站上20MA%": "{:.1f}%"
    })

styled_table = style_screener(view_df[disp_cols].rename(columns=rename_map).style)
st.dataframe(styled_table, use_container_width=True, height=400)

# ==========================================
# 圖片 2.① 與 2.② 數據解耦散佈圖與穿透
# ==========================================
st.markdown("---")
st.subheader("💡 內外背離雷達圖 (ETF 當日升幅 vs 等權升幅)")
st.caption("散佈點大小代表等權與市值差額絕對值。綠色代表內部上漲家數佔比高。")

fig_scat = px.scatter(
    view_df,
    x="pct_change", y="equal_weight_return",
    text="symbol", color="advancing_ratio",
    color_continuous_scale="RdYlGn",
    size=np.abs(view_df["ew_vs_cap_spread"]) + 2,
    hover_data=["name", "sub_industry", "reversal_signal_flag", "momentum_5d"],
    labels={"pct_change": "ETF 當日升幅 (%)", "equal_weight_return": "內部等權升幅 (%)"}
)
min_v = min(view_df["pct_change"].min(), view_df["equal_weight_return"].min(), -2)
max_v = max(view_df["pct_change"].max(), view_df["equal_weight_return"].max(), 2)
fig_scat.add_trace(go.Scatter(x=[min_v, max_v], y=[min_v, max_v], mode="lines", line=dict(dash="dash", color="gray"), name="等權 = 市值"))
fig_scat.update_traces(textposition="top center")
fig_scat.update_layout(height=480)
st.plotly_chart(fig_scat, use_container_width=True)

# 成分股持股穿透
st.markdown("---")
st.subheader("🔎 單一細分 ETF 成分股持股穿透 (Holdings Drill-Down)")
target_etf = st.selectbox("選擇要穿透的 ETF:", view_df["symbol"].tolist())
if target_etf:
    conn = sqlite3.connect(DB_FILE)
    h_df = pd.read_sql(f"SELECT stock_symbol, weight, updated_date FROM etf_holdings WHERE etf_symbol='{target_etf}' ORDER BY weight DESC", conn)
    conn.close()
    if not h_df.empty:
        st.write(f"**{target_etf}** 底層持股名單 (共 {len(h_df)} 隻，顯示前 25 隻)：")
        st.dataframe(h_df.head(25).rename(columns={"stock_symbol": "成分股代號", "weight": "權重", "updated_date": "持股更新日期"}), use_container_width=True)
