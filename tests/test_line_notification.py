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
        """Test formatting stock message with valid data (backward compatible with list)"""
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
        """Test formatting stock message with empty data (backward compatible with list)"""
        token = "test_token"
        user_id = "test_user_id"

        with patch('src.line_notification.LineBotApi'):
            notifier = LineNotification(token, user_id)

            message = notifier.format_stock_message([])

            # Empty list is converted to dict with empty holdings and open_buy
            assert '📊 Finlab 策略持股報告' in message
            assert '📭 本日無新增持股' in message
            assert '目前無持股資料' in message

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

    def test_init_with_group_ids(self):
        """Test LineNotification initialization with group IDs"""
        token = "test_token"
        user_id = "test_user_id"
        group_ids = ["group1", "group2"]

        with patch('src.line_notification.LineBotApi') as mock_api:
            notifier = LineNotification(token, user_id, group_ids)

            assert notifier.user_id == user_id
            assert notifier.group_ids == group_ids
            mock_api.assert_called_once_with(token)

    def test_init_without_group_ids(self):
        """Test LineNotification initialization without group IDs"""
        token = "test_token"
        user_id = "test_user_id"

        with patch('src.line_notification.LineBotApi') as mock_api:
            notifier = LineNotification(token, user_id)

            assert notifier.user_id == user_id
            assert notifier.group_ids == []
            mock_api.assert_called_once_with(token)

    @patch('src.line_notification.LineBotApi')
    @patch('src.line_notification.TextSendMessage')
    def test_send_stock_data_to_groups(self, mock_text_msg, mock_api):
        """Test sending stock data to multiple groups"""
        # Arrange
        token = "test_token"
        user_id = "test_user_id"
        group_ids = ["group1", "group2", "group3"]
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

        notifier = LineNotification(token, user_id, group_ids)

        # Act
        result = notifier.send_stock_data(test_data)

        # Assert
        assert result is True
        # Should call push_message for user + 3 groups = 4 times
        assert mock_api_instance.push_message.call_count == 4

        # Verify calls to user and all groups
        calls = mock_api_instance.push_message.call_args_list
        assert calls[0][0][0] == user_id
        assert calls[1][0][0] == "group1"
        assert calls[2][0][0] == "group2"
        assert calls[3][0][0] == "group3"

    @patch('src.line_notification.LineBotApi')
    @patch('src.line_notification.TextSendMessage')
    def test_send_stock_data_empty_groups(self, mock_text_msg, mock_api):
        """Test sending stock data with empty group list"""
        # Arrange
        token = "test_token"
        user_id = "test_user_id"
        group_ids = []
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

        notifier = LineNotification(token, user_id, group_ids)

        # Act
        result = notifier.send_stock_data(test_data)

        # Assert
        assert result is True
        # Should only call push_message once for user
        mock_api_instance.push_message.assert_called_once()
        assert mock_api_instance.push_message.call_args[0][0] == user_id

    def test_format_stock_message_with_new_dict_format(self):
        """Test formatting stock message with new dict format"""
        token = "test_token"
        user_id = "test_user_id"

        with patch('src.line_notification.LineBotApi'):
            notifier = LineNotification(token, user_id)

            test_data = {
                "holdings": [
                    {
                        'name': '科嶠',
                        'stock_id': '4542',
                        'entry_date': '2026/2/6',
                        'profit_percentage': '▴ 10.00%',
                        'current_weight': '20.0%'
                    }
                ],
                "open_buy": [
                    {
                        'name': '青雲',
                        'stock_id': '5386'
                    }
                ]
            }

            message = notifier.format_stock_message(test_data)

            assert '📊 Finlab 策略持股報告' in message
            assert '✅ 本日新增買入' in message
            assert '青雲' in message
            assert '5386' in message
            assert '📈 目前持股' in message
            assert '科嶠' in message
            assert '4542' in message
            assert '總計: 1 檔股票' in message

    def test_format_stock_message_with_no_open_buy(self):
        """Test formatting stock message when no open_buy stocks"""
        token = "test_token"
        user_id = "test_user_id"

        with patch('src.line_notification.LineBotApi'):
            notifier = LineNotification(token, user_id)

            test_data = {
                "holdings": [
                    {
                        'name': '科嶠',
                        'stock_id': '4542',
                        'entry_date': '2026/2/6',
                        'profit_percentage': '▴ 10.00%',
                        'current_weight': '20.0%'
                    }
                ],
                "open_buy": []
            }

            message = notifier.format_stock_message(test_data)

            assert '📊 Finlab 策略持股報告' in message
            assert '📭 本日無新增持股' in message
            assert '📈 目前持股' in message
            assert '科嶠' in message
            assert '總計: 1 檔股票' in message

    def test_format_stock_message_with_only_open_buy(self):
        """Test formatting stock message with only open_buy stocks"""
        token = "test_token"
        user_id = "test_user_id"

        with patch('src.line_notification.LineBotApi'):
            notifier = LineNotification(token, user_id)

            test_data = {
                "holdings": [],
                "open_buy": [
                    {
                        'name': '青雲',
                        'stock_id': '5386'
                    },
                    {
                        'name': '科嶠',
                        'stock_id': '4542'
                    }
                ]
            }

            message = notifier.format_stock_message(test_data)

            assert '📊 Finlab 策略持股報告' in message
            assert '✅ 本日新增買入' in message
            assert '青雲' in message
            assert '5386' in message
            assert '科嶠' in message
            assert '4542' in message
            assert '目前無持股資料' in message

    def test_format_stock_message_with_no_data(self):
        """Test formatting stock message when both holdings and open_buy are empty"""
        token = "test_token"
        user_id = "test_user_id"

        with patch('src.line_notification.LineBotApi'):
            notifier = LineNotification(token, user_id)

            test_data = {
                "holdings": [],
                "open_buy": []
            }

            message = notifier.format_stock_message(test_data)

            assert '📊 Finlab 策略持股報告' in message
            assert '📭 本日無新增持股' in message
            assert '目前無持股資料' in message

    def test_format_stock_message_with_multiple_open_buy(self):
        """Test formatting stock message with multiple open_buy stocks"""
        token = "test_token"
        user_id = "test_user_id"

        with patch('src.line_notification.LineBotApi'):
            notifier = LineNotification(token, user_id)

            test_data = {
                "holdings": [],
                "open_buy": [
                    {'name': '股票1', 'stock_id': '1111'},
                    {'name': '股票2', 'stock_id': '2222'},
                    {'name': '股票3', 'stock_id': '3333'}
                ]
            }

            message = notifier.format_stock_message(test_data)

            assert '✅ 本日新增買入' in message
            assert '股票1' in message
            assert '1111' in message
            assert '股票2' in message
            assert '2222' in message
            assert '股票3' in message
            assert '3333' in message
