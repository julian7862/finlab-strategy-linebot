"""
配置與環境變數管理
"""
import os
import sys
from dotenv import load_dotenv


def load_config():
    """
    載入並驗證環境變數
    優先從 OS 環境變數讀取，若無則從 .env 檔案讀取

    Returns:
        dict: 包含配置的字典

    Raises:
        SystemExit: 如果必要的環境變數缺失
    """
    # 載入 .env 檔案（作為後備）
    load_dotenv()

    # 優先從 OS 環境變數讀取，若為 None 則從 .env 讀取
    target_url = os.environ.get('TARGET_URL') or os.getenv("TARGET_URL")
    line_channel_access_token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN') or os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    line_user_id = os.environ.get('LINE_USER_ID') or os.getenv("LINE_USER_ID")
    line_webhook_url = os.environ.get('LINE_WEBHOOK_URL') or os.getenv("LINE_WEBHOOK_URL")

    if not target_url:
        print("錯誤：未在環境變數或 .env 檔案中找到 'TARGET_URL'。")
        print("請確認已設定 TARGET_URL 環境變數或 .env 檔案存在且包含 TARGET_URL")
        sys.exit(1)

    return {
        "target_url": target_url,
        "line_channel_access_token": line_channel_access_token,
        "line_user_id": line_user_id,
        "line_webhook_url": line_webhook_url
    }
