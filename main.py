from src.config import load_config
from src.scraper import FinlabStrategyScraper
from src.formatter import print_scrape_results


def main():
    """主程式進入點"""
    # 載入配置
    config = load_config()
    target_url = config["target_url"]

    print(f"準備抓取目標網址: {target_url}")

    # 執行抓取
    scraper = FinlabStrategyScraper()
    try:
        data = scraper.scrape(target_url)
        print_scrape_results(data)
    except Exception as e:
        print(f"執行發生錯誤: {e}")
        raise


if __name__ == "__main__":
    main()