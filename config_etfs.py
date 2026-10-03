# 嚴格對應 GICS 多層級細分行業 ETF 映射表 (含對標基準 Benchmark)
ETF_UNIVERSE = [
    # 科技與通訊 (Technology & Communication)
    {"ticker": "SMH", "name": "半導體 (VanEck)", "sector": "科技", "industry": "半導體", "issuer": "VanEck", "benchmark": "XLK"},
    {"ticker": "SOXX", "name": "半導體 (iShares)", "sector": "科技", "industry": "半導體", "issuer": "iShares", "benchmark": "XLK"},
    {"ticker": "IGV", "name": "雲端與軟件", "sector": "科技", "industry": "軟件SaaS", "issuer": "iShares", "benchmark": "XLK"},
    {"ticker": "CIBR", "name": "網絡安全", "sector": "科技", "industry": "網絡安全", "issuer": "First Trust", "benchmark": "XLK"},
    {"ticker": "HACK", "name": "網絡安全 (Amplify)", "sector": "科技", "industry": "網絡安全", "issuer": "Amplify", "benchmark": "XLK"},
    {"ticker": "FDN", "name": "互聯網指數", "sector": "科技", "industry": "互聯網", "issuer": "First Trust", "benchmark": "QQQ"},
    {"ticker": "BOTZ", "name": "AI與機器人", "sector": "科技", "industry": "人工智能", "issuer": "Global X", "benchmark": "QQQ"},
    {"ticker": "FINX", "name": "金融科技", "sector": "科技", "industry": "FinTech", "issuer": "Global X", "benchmark": "XLK"},
    {"ticker": "NXTG", "name": "5G與下一代通信", "sector": "通訊", "industry": "通信網絡", "issuer": "First Trust", "benchmark": "XLC"},
    {"ticker": "PBS", "name": "動態傳媒", "sector": "通訊", "industry": "傳媒娛樂", "issuer": "Invesco", "benchmark": "XLC"},

    # 醫療健康 (Healthcare)
    {"ticker": "XBI", "name": "生物科技 (等權)", "sector": "醫療", "industry": "生物科技", "issuer": "SPDR", "benchmark": "IBB"},
    {"ticker": "IBB", "name": "生物科技 (加權)", "sector": "醫療", "industry": "生物科技", "issuer": "iShares", "benchmark": "XLV"},
    {"ticker": "IHI", "name": "醫療設備與器材", "sector": "醫療", "industry": "醫療器械", "issuer": "iShares", "benchmark": "XLV"},
    {"ticker": "XHE", "name": "醫療裝備 (SPDR)", "sector": "醫療", "industry": "醫療裝備", "issuer": "SPDR", "benchmark": "XLV"},
    {"ticker": "XPH", "name": "製藥", "sector": "醫療", "industry": "傳統製藥", "issuer": "SPDR", "benchmark": "XLV"},
    {"ticker": "IHF", "name": "醫療服務與醫保", "sector": "醫療", "industry": "醫療保險", "issuer": "iShares", "benchmark": "XLV"},

    # 金融 (Financials)
    {"ticker": "KRE", "name": "區域銀行", "sector": "金融", "industry": "區域銀行", "issuer": "SPDR", "benchmark": "KBE"},
    {"ticker": "KBE", "name": "商業大行", "sector": "金融", "industry": "商業銀行", "issuer": "SPDR", "benchmark": "XLF"},
    {"ticker": "IAI", "name": "經紀投行", "sector": "金融", "industry": "投行券商", "issuer": "iShares", "benchmark": "XLF"},
    {"ticker": "KIE", "name": "保險", "sector": "金融", "industry": "保險", "issuer": "SPDR", "benchmark": "XLF"},

    # 工業、國防與交運 (Industrials & Infrastructure)
    {"ticker": "ITA", "name": "國防軍工 (iShares)", "sector": "工業", "industry": "軍工航天", "issuer": "iShares", "benchmark": "XLI"},
    {"ticker": "XAR", "name": "航天軍工 (SPDR)", "sector": "工業", "industry": "軍工航天", "issuer": "SPDR", "benchmark": "XLI"},
    {"ticker": "IYT", "name": "交通運輸", "sector": "工業", "industry": "交運物流", "issuer": "iShares", "benchmark": "XLI"},
    {"ticker": "XTN", "name": "標普交通運輸", "sector": "工業", "industry": "交運物流", "issuer": "SPDR", "benchmark": "XLI"},
    {"ticker": "JETS", "name": "航空航運", "sector": "工業", "industry": "民航客運", "issuer": "US Global", "benchmark": "XLI"},
    {"ticker": "PAVE", "name": "基建工程", "sector": "工業", "industry": "基礎設施", "issuer": "Global X", "benchmark": "XLI"},

    # 消費與地產 (Consumer & Real Estate)
    {"ticker": "XHB", "name": "地產建築商 (等權)", "sector": "消費地產", "industry": "房屋建築", "issuer": "SPDR", "benchmark": "ITB"},
    {"ticker": "ITB", "name": "純住宅營造", "sector": "消費地產", "industry": "住宅營造", "issuer": "iShares", "benchmark": "XLY"},
    {"ticker": "XRT", "name": "零售業 (等權)", "sector": "消費地產", "industry": "實體零售", "issuer": "SPDR", "benchmark": "XLY"},
    {"ticker": "PEJ", "name": "休閒娛樂餐飲", "sector": "消費地產", "industry": "休閒餐飲", "issuer": "Invesco", "benchmark": "XLY"},
    {"ticker": "AWAY", "name": "旅遊科技零售", "sector": "消費地產", "industry": "旅遊零售", "issuer": "ETFMG", "benchmark": "XLY"},
    {"ticker": "REZ", "name": "住宅REITs", "sector": "消費地產", "industry": "房產信託", "issuer": "iShares", "benchmark": "XLRE"},

    # 能源與原材料 (Energy & Materials)
    {"ticker": "XOP", "name": "油氣開採 (等權)", "sector": "能源材料", "industry": "上游勘探", "issuer": "SPDR", "benchmark": "XLE"},
    {"ticker": "OIH", "name": "油服與設備", "sector": "能源材料", "industry": "油田設備", "issuer": "VanEck", "benchmark": "XLE"},
    {"ticker": "AMLP", "name": "中游管網MLP", "sector": "能源材料", "industry": "中游管網", "issuer": "Alerian", "benchmark": "XLE"},
    {"ticker": "COPX", "name": "銅礦業", "sector": "能源材料", "industry": "銅礦採選", "issuer": "Global X", "benchmark": "XLB"},
    {"ticker": "GDX", "name": "金礦股", "sector": "能源材料", "industry": "大型金礦", "issuer": "VanEck", "benchmark": "GLD"},
    {"ticker": "GDXJ", "name": "初級中小型金礦", "sector": "能源材料", "industry": "中小型金礦", "issuer": "VanEck", "benchmark": "GDX"},
    {"ticker": "XME", "name": "金屬採礦", "sector": "能源材料", "industry": "金屬冶煉", "issuer": "SPDR", "benchmark": "XLB"},
    {"ticker": "URA", "name": "鈾礦與核能", "sector": "能源材料", "industry": "鈾礦能源", "issuer": "Global X", "benchmark": "URA"},

    # 公用事業與新能源 (Utilities & Clean Energy)
    {"ticker": "GRID", "name": "智能電網與輸配電", "sector": "公用事業", "industry": "電網設備", "issuer": "First Trust", "benchmark": "XLU"},
    {"ticker": "ICLN", "name": "清潔能源", "sector": "公用事業", "industry": "新能源", "issuer": "iShares", "benchmark": "XLU"},
    {"ticker": "PBW", "name": "清潔能源 (Invesco)", "sector": "公用事業", "industry": "新能源", "issuer": "Invesco", "benchmark": "XLU"},
    {"ticker": "TAN", "name": "太陽能", "sector": "公用事業", "industry": "光伏太陽能", "issuer": "Invesco", "benchmark": "ICLN"}
]

# 11大板塊基準代號
SECTOR_BENCHMARKS = ["XLK", "XLV", "XLF", "XLI", "XLY", "XLP", "XLE", "XLB", "XLU", "XLRE", "XLC", "SPY", "QQQ", "GLD"]
