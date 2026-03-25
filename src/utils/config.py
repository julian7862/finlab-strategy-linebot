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
    line_user_ids_str = os.environ.get('LINE_USER_IDS') or os.getenv("LINE_USER_IDS")
    line_group_ids_str = os.environ.get('LINE_GROUP_IDS') or os.getenv("LINE_GROUP_IDS")
    line_webhook_url = os.environ.get('LINE_WEBHOOK_URL') or os.getenv("LINE_WEBHOOK_URL")

    # 第二組 LINE 帳號配置
    line_channel_access_token_2 = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN_2') or os.getenv("LINE_CHANNEL_ACCESS_TOKEN_2")
    line_user_ids_str_2 = os.environ.get('LINE_USER_IDS_2') or os.getenv("LINE_USER_IDS_2")
    line_group_ids_str_2 = os.environ.get('LINE_GROUP_IDS_2') or os.getenv("LINE_GROUP_IDS_2")

    # 解析逗號分隔的 LINE_USER_IDS
    line_user_ids = []
    if line_user_ids_str:
        # 分割字串，移除空白，過濾空值
        line_user_ids = [uid.strip() for uid in line_user_ids_str.split(',') if uid.strip()]

    # 解析逗號分隔的 LINE_GROUP_IDS
    line_group_ids = []
    if line_group_ids_str:
        # 分割字串，移除空白，過濾空值
        line_group_ids = [gid.strip() for gid in line_group_ids_str.split(',') if gid.strip()]

    # 解析第二組 LINE_USER_IDS_2
    line_user_ids_2 = []
    if line_user_ids_str_2:
        line_user_ids_2 = [uid.strip() for uid in line_user_ids_str_2.split(',') if uid.strip()]

    # 解析第二組 LINE_GROUP_IDS_2
    line_group_ids_2 = []
    if line_group_ids_str_2:
        line_group_ids_2 = [gid.strip() for gid in line_group_ids_str_2.split(',') if gid.strip()]

    if not target_url:
        print("錯誤：未在環境變數或 .env 檔案中找到 'TARGET_URL'。")
        print("請確認已設定 TARGET_URL 環境變數或 .env 檔案存在且包含 TARGET_URL")
        sys.exit(1)

    return {
        "target_url": target_url,
        "line_channel_access_token": line_channel_access_token,
        "line_user_ids": line_user_ids,
        "line_group_ids": line_group_ids,
        "line_webhook_url": line_webhook_url,
        "line_channel_access_token_2": line_channel_access_token_2,
        "line_user_ids_2": line_user_ids_2,
        "line_group_ids_2": line_group_ids_2
    }
