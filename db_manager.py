import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "data", "etf_system.db")

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_database():
    conn = get_connection()
    cur = conn.cursor()
    
    # 1. etf_metadata: symbol, name, sector, sub_industry, benchmark
    cur.execute("""
    CREATE TABLE IF NOT EXISTS etf_metadata (
        symbol TEXT PRIMARY KEY,
        name TEXT,
        sector TEXT,
        sub_industry TEXT,
        issuer TEXT,
        benchmark TEXT
    )
    """)
    
    # 2. etf_holdings (定時每週或每月同步一次): etf_symbol, stock_symbol, weight, updated_date
    cur.execute("""
    CREATE TABLE IF NOT EXISTS etf_holdings (
        etf_symbol TEXT,
        stock_symbol TEXT,
        weight REAL,
        updated_date TEXT,
        PRIMARY KEY (etf_symbol, stock_symbol)
    )
    """)
    
    # 3. market_daily_metrics (每日收市計算存入):
    # date, symbol, close_price, pct_change, dist_20ma, dist_50ma, dist_200ma,
    # equal_weight_return, advancing_ratio, above_20ma_ratio, above_50ma_ratio,
    # momentum_5d, momentum_20d, volume_ratio, ratio_vs_benchmark, reversal_signals
    cur.execute("""
    CREATE TABLE IF NOT EXISTS market_daily_metrics (
        date TEXT,
        symbol TEXT,
        close_price REAL,
        pct_change REAL,
        dist_20ma REAL,
        dist_50ma REAL,
        dist_200ma REAL,
        equal_weight_return REAL,
        ew_vs_cap_spread REAL,
        advancing_count INTEGER,
        declining_count INTEGER,
        advancing_ratio REAL,
        above_20ma_ratio REAL,
        above_50ma_ratio REAL,
        momentum_5d REAL,
        momentum_20d REAL,
        volume_ratio REAL,
        ratio_vs_benchmark REAL,
        reversal_signal_flag TEXT,
        PRIMARY KEY (date, symbol)
    )
    """)
    
    # 4. macro_breadth: S&P 500 & Nasdaq 每日破新高、破新低淨值曲線及 11 大 Sectors 資金流向
    cur.execute("""
    CREATE TABLE IF NOT EXISTS macro_breadth (
        date TEXT,
        index_name TEXT,
        new_highs_count INTEGER,
        new_lows_count INTEGER,
        net_highs_lows INTEGER,
        pct_above_50ma REAL,
        pct_above_200ma REAL,
        PRIMARY KEY (date, index_name)
    )
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
    print("Database initialized successfully matching schema requirements.")
