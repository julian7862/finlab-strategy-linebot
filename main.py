from src.utils.config import load_config
from src.utils.formatter import print_scrape_results
from src.scraper import FinlabStrategyScraper
from src.line_notification import LineNotification


def main():
    """主程式進入點"""
    # 載入配置
    config = load_config()
    target_url = config["target_url"]
    line_channel_access_token = config.get("line_channel_access_token")
    line_user_id = config.get("line_user_id")

    print(f"準備抓取目標網址: {target_url}")

    # 執行抓取
    scraper = FinlabStrategyScraper()
    try:
        data = scraper.scrape(target_url)
        print_scrape_results(data)

        # 發送到 LINE
        if line_channel_access_token and line_user_id:
            print("\n準備發送訊息到 LINE...")
            line_notifier = LineNotification(line_channel_access_token, line_user_id)
            line_notifier.send_stock_data(data)
            print("LINE 訊息發送完成！")
        else:
            print("\n跳過 LINE 通知（未設定 LINE_CHANNEL_ACCESS_TOKEN 或 LINE_USER_ID）")

    except Exception as e:
        print(f"執行發生錯誤: {e}")
        raise


if __name__ == "__main__":
    main()