"""
LINE Bot notification module for sending scraped stock data
"""
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError


class LineNotification:
    """
    處理 LINE Bot 訊息推送的類別
    """

    def __init__(self, channel_access_token, user_ids, group_ids=None):
        """
        初始化 LINE Bot API

        Args:
            channel_access_token (str): LINE Channel Access Token
            user_ids (list): LINE User IDs 列表
            group_ids (list): LINE Group IDs 列表 (optional)
        """
        self.line_bot_api = LineBotApi(channel_access_token)
        self.user_ids = user_ids or []
        self.group_ids = group_ids or []

    def format_stock_message(self, data):
        """
        將股票資料格式化為 LINE 訊息

        Args:
            data (dict or list): 股票資料字典 {"holdings": [...], "open_buy": [...]} 或舊格式列表

        Returns:
            str: 格式化後的訊息
        """
        # 向後兼容：如果傳入的是 list，轉換為新格式
        if isinstance(data, list):
            data = {"holdings": data, "open_buy": []}

        holdings = data.get("holdings", [])
        open_buy = data.get("open_buy", [])

        message_lines = ["📊 Finlab 策略持股報告\n"]

        # 格式化開盤買入區塊
        if open_buy:
            message_lines.append("✅ 本日新增買入")
            for stock in open_buy:
                message_lines.append(f"  • {stock.get('name', 'N/A')} ({stock.get('stock_id', 'N/A')})")
            message_lines.append("")
        else:
            message_lines.append("📭 本日無新增持股\n")

        # 格式化持股區塊
        if holdings:
            message_lines.append("📈 目前持股")
            for index, stock in enumerate(holdings, 1):
                message_lines.append(f"[{index}] {stock.get('name', 'N/A')} ({stock.get('stock_id', 'N/A')})")
                message_lines.append(f"  📅 進場日期: {stock.get('entry_date', 'N/A')}")
                message_lines.append(f"  💰 獲利: {stock.get('profit_percentage', 'N/A')}")
                message_lines.append(f"  ⚖️  權重: {stock.get('current_weight', 'N/A')}")
                message_lines.append("")

            # 計算持股與現金比例 (假設滿倉為 5 檔股票)
            holdings_count = len(holdings)
            holdings_percentage = (holdings_count / 5) * 100
            cash_percentage = 100 - holdings_percentage

            message_lines.append(f"總計: {holdings_count} 檔股票")
            message_lines.append(f"💼 持股: {holdings_percentage:.0f}% | 💵 現金: {cash_percentage:.0f}%")
        else:
            message_lines.append("目前無持股資料")

        return "\n".join(message_lines)

    def send_stock_data(self, data):
        """
        發送股票資料到 LINE

        Args:
            data (list): 股票資料列表

        Returns:
            bool: 發送成功返回 True，失敗返回 False

        Raises:
            LineBotApiError: LINE API 錯誤
        """
        try:
            message_text = self.format_stock_message(data)
            message = TextSendMessage(text=message_text)

            # 發送給所有個人用戶
            for user_id in self.user_ids:
                self.line_bot_api.push_message(user_id, message)
                print(f"成功發送訊息到 LINE (User ID: {user_id})")

            # 發送給所有群組
            for group_id in self.group_ids:
                self.line_bot_api.push_message(group_id, message)
                print(f"成功發送訊息到 LINE (Group ID: {group_id})")

            return True

        except LineBotApiError as e:
            print(f"LINE Bot API 錯誤: {e}")
            raise

        except Exception as e:
            print(f"發送訊息時發生錯誤: {e}")
            raise

    def send_text_message(self, text):
        """
        發送純文字訊息到 LINE

        Args:
            text (str): 要發送的文字訊息

        Returns:
            bool: 發送成功返回 True，失敗返回 False
        """
        try:
            message = TextSendMessage(text=text)
            for user_id in self.user_ids:
                self.line_bot_api.push_message(user_id, message)
                print(f"成功發送文字訊息到 LINE (User ID: {user_id})")
            return True

        except LineBotApiError as e:
            print(f"LINE Bot API 錯誤: {e}")
            raise

        except Exception as e:
            print(f"發送訊息時發生錯誤: {e}")
            raise
