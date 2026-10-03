import datetime
import pandas as pd
import numpy as np
import yfinance as yf
from db_manager import get_connection
from config_etfs import SECTOR_BENCHMARKS

def update_macro_breadth(conn, today_str):
    """計算大盤層 (Macro Breadth): S&P 500 與 Nasdaq 每日破 52 週新高新低淨值 (NH - NL)"""
    print("[*] [A. 全局市場層] 正在計算 S&P 500 與 Nasdaq 100 每日新高新低與 50MA/200MA 寬度...")
    
    indices = {
        "S&P 500": "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        "Nasdaq 100": "https://en.wikipedia.org/wiki/Nasdaq-100"
    }
    cur = conn.cursor()
    
    for idx_name, url in indices.items():
        try:
            tables = pd.read_html(url)
            if idx_name == "S&P 500":
                tickers = tables[0]["Symbol"].str.replace(".", "-", regex=False).tolist()
            else:
                tickers = tables[4]["Ticker"].str.replace(".", "-", regex=False).tolist() if len(tables) > 4 else tables[3]["Ticker"].str.replace(".", "-", regex=False).tolist()
            
            # 批次下載數據
            data = yf.download(tickers, period="1y", interval="1d", group_by="ticker", auto_adjust=True, progress=False)
            
            nh_cnt = 0
            nl_cnt = 0
            ab_50 = 0
            ab_200 = 0
            valid = 0
            
            for sym in tickers:
                if sym in data.columns.levels[0]:
                    df_c = data[sym]["Close"].dropna()
                    if len(df_c) >= 200:
                        valid += 1
                        curr = df_c.iloc[-1]
                        max_1y = df_c.max()
                        min_1y = df_c.min()
                        if curr >= max_1y * 0.995:
                            nh_cnt += 1
                        if curr <= min_1y * 1.005:
                            nl_cnt += 1
                        if curr > df_c.rolling(50).mean().iloc[-1]:
                            ab_50 += 1
                        if curr > df_c.rolling(200).mean().iloc[-1]:
                            ab_200 += 1
                            
            pct_50 = round(ab_50 / valid * 100, 1) if valid > 0 else 0.0
            pct_200 = round(ab_200 / valid * 100, 1) if valid > 0 else 0.0
            net_hl = nh_cnt - nl_cnt
            
            cur.execute("""
            INSERT OR REPLACE INTO macro_breadth VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (today_str, idx_name, nh_cnt, nl_cnt, net_hl, pct_50, pct_200))
            conn.commit()
            print(f"[+] {idx_name}: 52W新高={nh_cnt}隻, 52W新低={nl_cnt}隻, 淨新高={net_hl}, 站上50MA={pct_50}%")
        except Exception as e:
            print(f"[-] 計算 {idx_name} 失敗: {e}")

def run_daily_pipeline():
    conn = get_connection()
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    print(f"==================================================")
    print(f"啟動盤後自動化批次計算: {today_str}")
    print(f"==================================================")
    
    # 1. 計算大盤新高新低淨值
    update_macro_breadth(conn, today_str)
    
    # 2. 獲取所有 ETF 及 benchmark
    meta_df = pd.read_sql("SELECT symbol, benchmark FROM etf_metadata", conn)
    holdings_df = pd.read_sql("SELECT etf_symbol, stock_symbol FROM etf_holdings", conn)
    
    etf_symbols = meta_df["symbol"].tolist()
    benchmarks = [b for b in meta_df["benchmark"].dropna().unique().tolist() if b]
    benchmarks += SECTOR_BENCHMARKS
    
    # 持股解耦與去重 (Unique Tickers)
    stock_symbols = holdings_df["stock_symbol"].dropna().unique().tolist()
    download_pool = list(set(etf_symbols + benchmarks + stock_symbols))
    
    print(f"[*] [優化去重] 批次拉取 {len(download_pool)} 隻股票與 ETF 歷史行情 (避免逐隻重複抓取)...")
    raw_data = yf.download(download_pool, period="15mo", interval="1d", group_by="ticker", auto_adjust=True, progress=False)
    
    cur = conn.cursor()
    
    for _, meta_row in meta_df.iterrows():
        etf = meta_row["symbol"]
        bench = meta_row["benchmark"]
        try:
            if etf not in raw_data.columns.levels[0]:
                continue
            hist = raw_data[etf]
            close = hist["Close"].dropna()
            volume = hist["Volume"].dropna() if "Volume" in hist else None
            
            if len(close) < 25:
                continue
                
            curr_c = float(close.iloc[-1])
            prev_c = float(close.iloc[-2])
            pct_change = round(((curr_c - prev_c) / prev_c) * 100.0, 2)
            
            # 動量排行: 5 日動量、20 日動量
            c_5d_ago = close.iloc[-6] if len(close) >= 6 else close.iloc[0]
            c_20d_ago = close.iloc[-21] if len(close) >= 21 else close.iloc[0]
            momentum_5d = round(((curr_c - c_5d_ago) / c_5d_ago) * 100.0, 2)
            momentum_20d = round(((curr_c - c_20d_ago) / c_20d_ago) * 100.0, 2)
            
            # 均線離散度 (MA Bias): 20MA, 50MA, 200MA
            ma20 = close.rolling(20).mean().iloc[-1]
            ma50 = close.rolling(50).mean().iloc[-1] if len(close) >= 50 else np.nan
            ma200 = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else np.nan
            
            dist_20 = round(((curr_c - ma20) / ma20) * 100.0, 2) if pd.notna(ma20) else 0.0
            dist_50 = round(((curr_c - ma50) / ma50) * 100.0, 2) if pd.notna(ma50) else 0.0
            dist_200 = round(((curr_c - ma200) / ma200) * 100.0, 2) if pd.notna(ma200) else 0.0
            
            # 成交量放大倍數 (當日 Volume / 20日均量)
            vol_ratio = 1.0
            if volume is not None and len(volume) >= 20:
                v_curr = volume.iloc[-1]
                v_20ma = volume.rolling(20).mean().iloc[-1]
                vol_ratio = round(float(v_curr / v_20ma), 2) if v_20ma > 0 else 1.0
                
            # 與基準對標強弱比 (Ratio Spread = ETF / Benchmark)
            ratio_spread = 1.0
            if bench and bench in raw_data.columns.levels[0]:
                bench_c = raw_data[bench]["Close"].dropna()
                if len(bench_c) >= 2:
                    ratio_spread = round(float(curr_c / bench_c.iloc[-1]), 4)
                    
            # 成分股內部寬度與等權升幅計算
            sub_stocks = holdings_df[holdings_df["etf_symbol"] == etf]["stock_symbol"].tolist()
            stock_pcts = []
            ab_20 = 0
            ab_50 = 0
            ab_20_prev = 0
            
            for s in sub_stocks:
                if s in raw_data.columns.levels[0]:
                    s_close = raw_data[s]["Close"].dropna()
                    if len(s_close) >= 22:
                        sc = s_close.iloc[-1]
                        sp = s_close.iloc[-2]
                        stock_pcts.append(((sc - sp) / sp) * 100.0)
                        
                        m20_curr = s_close.rolling(20).mean().iloc[-1]
                        m20_prev = s_close.rolling(20).mean().iloc[-2]
                        if sc > m20_curr:
                            ab_20 += 1
                        if sp > m20_prev:
                            ab_20_prev += 1
                        if len(s_close) >= 50 and sc > s_close.rolling(50).mean().iloc[-1]:
                            ab_50 += 1
                            
            if stock_pcts:
                ew_return = round(float(np.mean(stock_pcts)), 2)
                adv_cnt = int(np.sum(np.array(stock_pcts) > 0))
                dec_cnt = int(np.sum(np.array(stock_pcts) < 0))
                adv_ratio = round(adv_cnt / len(stock_pcts) * 100.0, 1)
                above_20_ratio = round(ab_20 / len(stock_pcts) * 100.0, 1)
                above_20_prev_ratio = round(ab_20_prev / len(stock_pcts) * 100.0, 1)
                above_50_ratio = round(ab_50 / len(stock_pcts) * 100.0, 1)
                ab_20_jump = above_20_ratio - above_20_prev_ratio  # 單日激增幅度
            else:
                # 雙軌制: 輕量化模式直接對標基準
                ew_return = pct_change
                adv_cnt, dec_cnt = 0, 0
                adv_ratio, above_20_ratio, above_50_ratio = 50.0, 50.0, 50.0
                ab_20_jump = 0.0
                
            spread = round(ew_return - pct_change, 2)
            
            # --- 嚴格執行圖片 3.C 轉勢雷達 (Reversal Radar) 判定 ---
            signals = []
            
            # 1. 右側爆發：站上 20MA 且內部站上 20MA 股票比例單日激增 20% 以上
            if curr_c > ma20 and ab_20_jump >= 20.0:
                signals.append("右側爆發(內部激增>20%)")
            elif 0.0 <= dist_20 <= 2.5 and above_20_ratio >= 60.0 and pct_change > 0:
                signals.append("突破20MA右側啟動")
                
            # 2. 左側反轉：連續 5 日跌幅超過歷史波動區間，且當日出現「成交量放大 + 等權率先翻紅 + 內部上漲比率 > 60%」
            if momentum_5d <= -5.0 and vol_ratio >= 1.25 and ew_return > 0.0 and adv_ratio >= 60.0:
                signals.append("左側反轉(放量+等權翻紅)")
                
            # 3. 內外背離信號：隱形強勢 vs 虛胖拉升
            if -0.2 <= pct_change <= 0.6 and adv_ratio >= 75.0:
                signals.append("隱形強勢(資金全面進場蓄勢)")
            if pct_change >= 1.2 and ew_return <= 0.2 and adv_ratio < 45.0:
                signals.append("虛胖拉升(巨頭拉指數內部下跌)")
                
            sig_text = " | ".join(signals) if signals else "常規波動"
            
            cur.execute("""
            INSERT OR REPLACE INTO market_daily_metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (today_str, etf, curr_c, pct_change, dist_20, dist_50, dist_200, ew_return, spread,
                  adv_cnt, dec_cnt, adv_ratio, above_20_ratio, above_50_ratio, momentum_5d, momentum_20d,
                  vol_ratio, ratio_spread, sig_text))
                  
        except Exception as e:
            print(f"[-] 計算 {etf} 出錯: {e}")
            
    conn.commit()
    conn.close()
    print("[+] market_daily_metrics 每日指標更新完成！")

if __name__ == "__main__":
    run_daily_pipeline()
