"""
Unit tests for LineNotification
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.line_notification import LineNotification


class TestLineNotification:
    """Test suite for LineNotification class"""

    def test_init(self):
        """Test LineNotification initialization"""
        token = "test_token"
        user_id = "test_user_id"

        with patch('src.line_notification.LineBotApi') as mock_api:
            notifier = LineNotification(token, user_id)

            assert notifier.user_id == user_id
            mock_api.assert_called_once_with(token)

    def test_format_stock_message_with_data(self):
        """Test formatting stock message with valid data"""
        token = "test_token"
        user_id = "test_user_id"

        with patch('src.line_notification.LineBotApi'):
            notifier = LineNotification(token, user_id)

            test_data = [
                {
                    'name': '科嶠',
                    'stock_id': '4542',
                    'entry_date': '2026/2/6',
                    'profit_percentage': '▴ 10.00%',
                    'current_weight': '20.0%'
                },
                {
                    'name': '青雲',
                    'stock_id': '5386',
                    'entry_date': '2026/2/4',
                    'profit_percentage': '▴ 42.31%',
                    'current_weight': '20.0%'
                }
            ]

            message = notifier.format_stock_message(test_data)

            assert '📊 Finlab 策略持股報告' in message
            assert '科嶠' in message
            assert '4542' in message
            assert '青雲' in message
            assert '5386' in message
            assert '總計: 2 檔股票' in message

    def test_format_stock_message_empty_data(self):
        """Test formatting stock message with empty data"""
        token = "test_token"
        user_id = "test_user_id"

        with patch('src.line_notification.LineBotApi'):
            notifier = LineNotification(token, user_id)

            message = notifier.format_stock_message([])

            assert message == "目前無持股資料"

    def test_format_stock_message_missing_fields(self):
        """Test formatting stock message with missing fields"""
        token = "test_token"
        user_id = "test_user_id"

        with patch('src.line_notification.LineBotApi'):
            notifier = LineNotification(token, user_id)

            test_data = [
                {
                    'name': '測試股票'
                    # Missing other fields
                }
            ]

            message = notifier.format_stock_message(test_data)

            assert '測試股票' in message
            assert 'N/A' in message  # Should have N/A for missing fields
            assert '總計: 1 檔股票' in message

    @patch('src.line_notification.LineBotApi')
    @patch('src.line_notification.TextSendMessage')
    def test_send_stock_data_success(self, mock_text_msg, mock_api):
        """Test successful stock data sending"""
        # Arrange
        token = "test_token"
        user_id = "test_user_id"
        mock_api_instance = Mock()
        mock_api.return_value = mock_api_instance

        test_data = [
            {
                'name': '科嶠',
                'stock_id': '4542',
                'entry_date': '2026/2/6',
                'profit_percentage': '▴ 10.00%',
                'current_weight': '20.0%'
            }
        ]

        notifier = LineNotification(token, user_id)

        # Act
        result = notifier.send_stock_data(test_data)

        # Assert
        assert result is True
        mock_api_instance.push_message.assert_called_once()
        mock_text_msg.assert_called_once()

    @patch('src.line_notification.LineBotApi')
    def test_send_stock_data_api_error(self, mock_api):
        """Test sending stock data with LINE API error"""
        # Arrange
        token = "test_token"
        user_id = "test_user_id"
        mock_api_instance = Mock()
        mock_api.return_value = mock_api_instance

        # Simulate Exception (simpler than creating full LineBotApiError)
        mock_api_instance.push_message.side_effect = Exception("API Error")

        test_data = [{'name': 'test'}]

        notifier = LineNotification(token, user_id)

        # Act & Assert
        with pytest.raises(Exception):
            notifier.send_stock_data(test_data)

    @patch('src.line_notification.LineBotApi')
    @patch('src.line_notification.TextSendMessage')
    def test_send_text_message_success(self, mock_text_msg, mock_api):
        """Test successful text message sending"""
        # Arrange
        token = "test_token"
        user_id = "test_user_id"
        mock_api_instance = Mock()
        mock_api.return_value = mock_api_instance

        notifier = LineNotification(token, user_id)

        # Act
        result = notifier.send_text_message("Hello World!!!")

        # Assert
        assert result is True
        mock_api_instance.push_message.assert_called_once_with(
            user_id,
            mock_text_msg.return_value
        )
        mock_text_msg.assert_called_once_with(text="Hello World!!!")

    @patch('src.line_notification.LineBotApi')
    def test_send_text_message_api_error(self, mock_api):
        """Test sending text message with LINE API error"""
        # Arrange
        token = "test_token"
        user_id = "test_user_id"
        mock_api_instance = Mock()
        mock_api.return_value = mock_api_instance

        # Simulate Exception (simpler than creating full LineBotApiError)
        mock_api_instance.push_message.side_effect = Exception("API Error")

        notifier = LineNotification(token, user_id)

        # Act & Assert
        with pytest.raises(Exception):
            notifier.send_text_message("Test")

    @patch('src.line_notification.LineBotApi')
    @patch('src.line_notification.TextSendMessage')
    def test_send_stock_data_with_empty_list(self, mock_text_msg, mock_api):
        """Test sending empty stock data list"""
        # Arrange
        token = "test_token"
        user_id = "test_user_id"
        mock_api_instance = Mock()
        mock_api.return_value = mock_api_instance

        notifier = LineNotification(token, user_id)

        # Act
        result = notifier.send_stock_data([])

        # Assert
        assert result is True
        # Should still send a message saying no data
        mock_text_msg.assert_called_once()
        call_args = mock_text_msg.call_args
        assert "目前無持股資料" in call_args.kwargs['text']
