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
    line_user_ids = config.get("line_user_ids", [])
    line_group_ids = config.get("line_group_ids", [])

    # 第二組 LINE 帳號配置
    line_channel_access_token_2 = config.get("line_channel_access_token_2")
    line_user_ids_2 = config.get("line_user_ids_2", [])
    line_group_ids_2 = config.get("line_group_ids_2", [])

    print(f"準備抓取目標網址: {target_url}")

    # 執行抓取
    scraper = FinlabStrategyScraper()
    try:
        data = scraper.scrape(target_url)
        print_scrape_results(data)

        # 發送到第一組 LINE 帳號
        if line_channel_access_token and (line_user_ids or line_group_ids):
            try:
                print("\n準備發送訊息到 LINE 帳號 1...")
                line_notifier = LineNotification(line_channel_access_token, line_user_ids, line_group_ids)
                line_notifier.send_stock_data(data)
                print("LINE 帳號 1 訊息發送完成！")
            except Exception as e:
                print(f"\nLINE 帳號 1 發送失敗（可能已達用量上限）: {e}")
                print("繼續執行帳號 2 的發送...")
        else:
            print("\n跳過 LINE 帳號 1 通知（未設定 LINE_CHANNEL_ACCESS_TOKEN 或收件者）")

        # 發送到第二組 LINE 帳號
        if line_channel_access_token_2 and (line_user_ids_2 or line_group_ids_2):
            try:
                print("\n準備發送訊息到 LINE 帳號 2...")
                line_notifier_2 = LineNotification(line_channel_access_token_2, line_user_ids_2, line_group_ids_2)
                line_notifier_2.send_stock_data(data)
                print("LINE 帳號 2 訊息發送完成！")
            except Exception as e:
                print(f"\nLINE 帳號 2 發送失敗: {e}")
        else:
            print("\n跳過 LINE 帳號 2 通知（未設定 LINE_CHANNEL_ACCESS_TOKEN_2 或收件者）")

    except Exception as e:
        print(f"執行發生錯誤: {e}")
        raise


if __name__ == "__main__":
    main()