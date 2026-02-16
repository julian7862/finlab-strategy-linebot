"""
格式化與輸出相關的工具函數
"""


def print_scrape_results(data):
    """
    格式化並印出抓取結果

    Args:
        data (list): 持股資料列表
    """
    print(f"\n=== 抓取完成，共 {len(data)} 筆資料 ===")

    if not data:
        print("無資料")
        return

    for index, row in enumerate(data, 1):
        print(f"[{index}]")
        print(f"  股票名稱: {row.get('name')}")
        print(f"  股票代號: {row.get('stock_id')}")
        print(f"  進場數值: {row.get('entry_date')}")
        print(f"  獲利趴數: {row.get('profit_percentage')}")
        print(f"  目前權重: {row.get('current_weight')}")
        print("-" * 30)
