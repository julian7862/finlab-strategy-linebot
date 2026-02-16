"""
配置與環境變數管理
"""
import os
import sys
from dotenv import load_dotenv


def load_config():
    """
    載入並驗證環境變數

    Returns:
        dict: 包含配置的字典

    Raises:
        SystemExit: 如果必要的環境變數缺失
    """
    load_dotenv()

    target_url = os.getenv("TARGET_URL")
    line_webhook_url = os.getenv("LINE_WEBHOOK_URL")

    if not target_url:
        print("錯誤：未在 .env 檔案中找到 'TARGET_URL'。")
        print("請確認 .env 檔案存在且包含 TARGET_URL=您的網址")
        sys.exit(1)

    return {
        "target_url": target_url,
        "line_webhook_url": line_webhook_url
    }
