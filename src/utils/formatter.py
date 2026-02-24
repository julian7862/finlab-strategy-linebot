"""
格式化與輸出相關的工具函數
"""


def print_scrape_results(data):
    """
    格式化並印出抓取結果

    Args:
        data (dict or list): 持股資料字典 {"holdings": [...], "open_buy": [...]} 或舊格式列表
    """
    # 向後兼容：如果傳入的是 list，轉換為新格式
    if isinstance(data, list):
        data = {"holdings": data, "open_buy": []}

    holdings = data.get("holdings", [])
    open_buy = data.get("open_buy", [])

    # 顯示開盤買入區塊
    if open_buy:
        print(f"\n=== 🔔 新增買入 ({len(open_buy)} 檔) ===")
        for index, row in enumerate(open_buy, 1):
            print(f"[{index}]")
            print(f"  股票名稱: {row.get('name')}")
            print(f"  股票代號: {row.get('stock_id')}")
            print("-" * 30)
    else:
        print("\n=== 📭 本日無新增持股 ===")

    # 顯示目前持股區塊
    if holdings:
        print(f"\n=== 📈 目前持股 ({len(holdings)} 檔) ===")
        for index, row in enumerate(holdings, 1):
            print(f"[{index}]")
            print(f"  股票名稱: {row.get('name')}")
            print(f"  股票代號: {row.get('stock_id')}")
            print(f"  進場數值: {row.get('entry_date')}")
            print(f"  獲利趴數: {row.get('profit_percentage')}")
            print(f"  目前權重: {row.get('current_weight')}")
            print("-" * 30)
    else:
        print("\n=== 目前無持股資料 ===")

    print(f"\n總計: 持股 {len(holdings)} 檔 | 新增買入 {len(open_buy)} 檔")
