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

    def __init__(self, channel_access_token, user_id):
        """
        初始化 LINE Bot API

        Args:
            channel_access_token (str): LINE Channel Access Token
            user_id (str): LINE User ID
        """
        self.line_bot_api = LineBotApi(channel_access_token)
        self.user_id = user_id

    def format_stock_message(self, data):
        """
        將股票資料格式化為 LINE 訊息

        Args:
            data (list): 股票資料列表

        Returns:
            str: 格式化後的訊息
        """
        if not data:
            return "目前無持股資料"

        message_lines = ["📊 Finlab 策略持股報告\n"]

        for index, stock in enumerate(data, 1):
            message_lines.append(f"[{index}] {stock.get('name', 'N/A')} ({stock.get('stock_id', 'N/A')})")
            message_lines.append(f"  📅 進場日期: {stock.get('entry_date', 'N/A')}")
            message_lines.append(f"  💰 獲利: {stock.get('profit_percentage', 'N/A')}")
            message_lines.append(f"  ⚖️  權重: {stock.get('current_weight', 'N/A')}")
            message_lines.append("")

        message_lines.append(f"總計: {len(data)} 檔股票")

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

            self.line_bot_api.push_message(self.user_id, message)
            print(f"成功發送訊息到 LINE (User ID: {self.user_id})")
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
            self.line_bot_api.push_message(self.user_id, message)
            print(f"成功發送文字訊息到 LINE")
            return True

        except LineBotApiError as e:
            print(f"LINE Bot API 錯誤: {e}")
            raise

        except Exception as e:
            print(f"發送訊息時發生錯誤: {e}")
            raise
