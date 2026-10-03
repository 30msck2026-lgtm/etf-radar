import io
import requests
import pandas as pd
from db_manager import get_connection
from config_etfs import ETF_UNIVERSE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def sync_spdr_holdings(ticker):
    url = f"https://www.ssga.com/us/en/intermediary/etfs/library-content/products/fund-data/etfs/us/holdings-daily-us-en-{ticker.lower()}.csv"
    resp = requests.get(url, headers=HEADERS, timeout=12)
    if resp.status_code != 200:
        return []
    lines = resp.text.splitlines()
    start_idx = 0
    for idx, l in enumerate(lines[:15]):
        if "Ticker" in l:
            start_idx = idx
            break
    df = pd.read_csv(io.StringIO("\n".join(lines[start_idx:])))
    df = df.dropna(subset=["Ticker"])
    df = df[df["Ticker"] != "-"]
    holdings = []
    for _, row in df.iterrows():
        t = str(row["Ticker"]).strip().replace(".", "-")
        w = 0.0
        if "Weight" in row and pd.notna(row["Weight"]):
            try:
                w = float(str(row["Weight"]).replace("%", "")) / 100.0
            except:
                w = 0.0
        holdings.append((ticker, t, w))
    return holdings

def sync_all_holdings():
    conn = get_connection()
    cur = conn.cursor()
    
    # 填充 etf_metadata
    for item in ETF_UNIVERSE:
        cur.execute("""
        INSERT OR REPLACE INTO etf_metadata (symbol, name, sector, sub_industry, issuer, benchmark)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (item["ticker"], item["name"], item["sector"], item["industry"], item["issuer"], item["benchmark"]))
    conn.commit()
    
    today_str = pd.Timestamp.now().strftime("%Y-%m-%d")
    print(f"[*] 執行每週/每月定時持股同步 (更新至 etf_holdings)...")
    
    for item in ETF_UNIVERSE:
        ticker = item["ticker"]
        issuer = item["issuer"]
        holdings = []
        try:
            if issuer == "SPDR":
                holdings = sync_spdr_holdings(ticker)
            if not holdings:
                import yfinance as yf
                t = yf.Ticker(ticker)
                try:
                    top_df = t.funds_data.top_holdings
                    if top_df is not None and not top_df.empty:
                        for s_ticker, row in top_df.iterrows():
                            clean_s = str(s_ticker).replace(".", "-")
                            holdings.append((ticker, clean_s, float(row.get("Holding Percent", 0.0))))
                except:
                    pass
            
            for h in holdings:
                cur.execute("""
                INSERT OR REPLACE INTO etf_holdings (etf_symbol, stock_symbol, weight, updated_date)
                VALUES (?, ?, ?, ?)
                """, (h[0], h[1], h[2], today_str))
            conn.commit()
            print(f"[+] {ticker}: 更新 {len(holdings)} 隻持股")
        except Exception as e:
            print(f"[-] {ticker} 同步跳過或出錯: {e}")
            
    conn.close()

if __name__ == "__main__":
    sync_all_holdings()
