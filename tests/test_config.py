"""
Unit tests for config module
"""
import os
import pytest
from unittest.mock import patch
from src.utils.config import load_config


class TestConfig:
    """Test suite for config loading"""

    @patch.dict(os.environ, {}, clear=True)
    @patch('src.utils.config.load_dotenv')
    @patch('src.utils.config.os.getenv')
    def test_load_from_env_file(self, mock_getenv, mock_load_dotenv):
        """Test loading from .env file when OS env vars not set"""
        # Arrange
        def getenv_side_effect(key, default=None):
            env_values = {
                'TARGET_URL': 'https://example.com',
                'LINE_CHANNEL_ACCESS_TOKEN': 'test_token',
                'LINE_USER_IDS': 'test_user',
                'LINE_WEBHOOK_URL': 'https://webhook.com'
            }
            return env_values.get(key, default)

        mock_getenv.side_effect = getenv_side_effect

        # Act
        config = load_config()

        # Assert
        assert config['target_url'] == 'https://example.com'
        assert config['line_channel_access_token'] == 'test_token'
        assert config['line_user_ids'] == ['test_user']
        assert config['line_webhook_url'] == 'https://webhook.com'
        mock_load_dotenv.assert_called_once()

    @patch('src.utils.config.load_dotenv')
    @patch.dict(os.environ, {
        'TARGET_URL': 'https://os-env.com',
        'LINE_CHANNEL_ACCESS_TOKEN': 'os_token',
        'LINE_USER_IDS': 'os_user',
        'LINE_WEBHOOK_URL': 'https://os-webhook.com'
    })
    def test_load_from_os_environ(self, mock_load_dotenv):
        """Test loading from OS environment variables"""
        # Act
        config = load_config()

        # Assert
        assert config['target_url'] == 'https://os-env.com'
        assert config['line_channel_access_token'] == 'os_token'
        assert config['line_user_ids'] == ['os_user']
        assert config['line_webhook_url'] == 'https://os-webhook.com'

    @patch('src.utils.config.load_dotenv')
    @patch('src.utils.config.os.getenv')
    @patch.dict(os.environ, {'TARGET_URL': 'https://os-priority.com'})
    def test_os_environ_takes_priority(self, mock_getenv, mock_load_dotenv):
        """Test that OS environment variables take priority over .env file"""
        # Arrange - .env file has different values
        def getenv_side_effect(key, default=None):
            env_file_values = {
                'TARGET_URL': 'https://dotenv-file.com',
                'LINE_CHANNEL_ACCESS_TOKEN': 'dotenv_token'
            }
            return env_file_values.get(key, default)

        mock_getenv.side_effect = getenv_side_effect

        # Act
        config = load_config()

        # Assert - OS environ should win
        assert config['target_url'] == 'https://os-priority.com'

    @patch.dict(os.environ, {}, clear=True)
    @patch('src.utils.config.load_dotenv')
    @patch('src.utils.config.os.getenv')
    def test_missing_target_url_raises_error(self, mock_getenv, mock_load_dotenv):
        """Test that missing TARGET_URL raises SystemExit"""
        # Arrange
        mock_getenv.return_value = None

        # Act & Assert
        with pytest.raises(SystemExit):
            load_config()

    @patch('src.utils.config.load_dotenv')
    @patch('src.utils.config.os.getenv')
    @patch.dict(os.environ, {'TARGET_URL': 'https://test.com'}, clear=True)
    def test_optional_line_credentials(self, mock_getenv, mock_load_dotenv):
        """Test that LINE credentials are optional"""
        # Arrange - only TARGET_URL is set, no LINE credentials
        def getenv_side_effect(key, default=None):
            if key == 'TARGET_URL':
                return None  # OS environ already has it
            return None  # No LINE credentials

        mock_getenv.side_effect = getenv_side_effect

        # Act
        config = load_config()

        # Assert
        assert config['target_url'] == 'https://test.com'
        assert config['line_channel_access_token'] is None
        assert config['line_user_ids'] == []
        assert config['line_webhook_url'] is None

    @patch('src.utils.config.load_dotenv')
    @patch('src.utils.config.os.getenv')
    @patch.dict(os.environ, {
        'TARGET_URL': 'https://test.com',
        'LINE_GROUP_IDS': 'group1,group2,group3'
    }, clear=True)
    def test_parse_line_group_ids(self, mock_getenv, mock_load_dotenv):
        """Test parsing comma-separated LINE_GROUP_IDS"""
        # Arrange
        mock_getenv.return_value = None

        # Act
        config = load_config()

        # Assert
        assert config['line_group_ids'] == ['group1', 'group2', 'group3']

    @patch('src.utils.config.load_dotenv')
    @patch('src.utils.config.os.getenv')
    @patch.dict(os.environ, {
        'TARGET_URL': 'https://test.com',
        'LINE_GROUP_IDS': 'group1 , group2 , group3 '
    }, clear=True)
    def test_parse_line_group_ids_with_whitespace(self, mock_getenv, mock_load_dotenv):
        """Test parsing LINE_GROUP_IDS with whitespace"""
        # Arrange
        mock_getenv.return_value = None

        # Act
        config = load_config()

        # Assert
        assert config['line_group_ids'] == ['group1', 'group2', 'group3']

    @patch('src.utils.config.load_dotenv')
    @patch('src.utils.config.os.getenv')
    @patch.dict(os.environ, {'TARGET_URL': 'https://test.com'}, clear=True)
    def test_empty_line_group_ids(self, mock_getenv, mock_load_dotenv):
        """Test that empty LINE_GROUP_IDS returns empty list"""
        # Arrange
        mock_getenv.return_value = None

        # Act
        config = load_config()

        # Assert
        assert config['line_group_ids'] == []

    @patch('src.utils.config.load_dotenv')
    @patch('src.utils.config.os.getenv')
    @patch.dict(os.environ, {
        'TARGET_URL': 'https://test.com',
        'LINE_GROUP_IDS': 'Ce8baec57b9b59c0b19766c6988ccd0b9,Cae25addef5acd7a43e1a075dc8e01728'
    }, clear=True)
    def test_parse_real_line_group_ids(self, mock_getenv, mock_load_dotenv):
        """Test parsing real LINE group IDs"""
        # Arrange
        mock_getenv.return_value = None

        # Act
        config = load_config()

        # Assert
        assert config['line_group_ids'] == [
            'Ce8baec57b9b59c0b19766c6988ccd0b9',
            'Cae25addef5acd7a43e1a075dc8e01728'
        ]

    @patch('src.utils.config.load_dotenv')
    @patch('src.utils.config.os.getenv')
    @patch.dict(os.environ, {
        'TARGET_URL': 'https://test.com',
        'LINE_USER_IDS': 'user1,user2,user3'
    }, clear=True)
    def test_parse_line_user_ids(self, mock_getenv, mock_load_dotenv):
        """Test parsing comma-separated LINE_USER_IDS"""
        # Arrange
        mock_getenv.return_value = None

        # Act
        config = load_config()

        # Assert
        assert config['line_user_ids'] == ['user1', 'user2', 'user3']

    @patch('src.utils.config.load_dotenv')
    @patch('src.utils.config.os.getenv')
    @patch.dict(os.environ, {
        'TARGET_URL': 'https://test.com',
        'LINE_USER_IDS': 'user1 , user2 , user3 '
    }, clear=True)
    def test_parse_line_user_ids_with_whitespace(self, mock_getenv, mock_load_dotenv):
        """Test parsing LINE_USER_IDS with whitespace"""
        # Arrange
        mock_getenv.return_value = None

        # Act
        config = load_config()

        # Assert
        assert config['line_user_ids'] == ['user1', 'user2', 'user3']

    @patch('src.utils.config.load_dotenv')
    @patch('src.utils.config.os.getenv')
    @patch.dict(os.environ, {'TARGET_URL': 'https://test.com'}, clear=True)
    def test_empty_line_user_ids(self, mock_getenv, mock_load_dotenv):
        """Test that empty LINE_USER_IDS returns empty list"""
        # Arrange
        mock_getenv.return_value = None

        # Act
        config = load_config()

        # Assert
        assert config['line_user_ids'] == []

    @patch('src.utils.config.load_dotenv')
    @patch('src.utils.config.os.getenv')
    @patch.dict(os.environ, {
        'TARGET_URL': 'https://test.com',
        'LINE_USER_IDS': 'Uce142fc90e26599eb9df68c2cef86449,U9ab8c3592aea16310b037f9084cef854'
    }, clear=True)
    def test_parse_real_line_user_ids(self, mock_getenv, mock_load_dotenv):
        """Test parsing real LINE user IDs"""
        # Arrange
        mock_getenv.return_value = None

        # Act
        config = load_config()

        # Assert
        assert config['line_user_ids'] == [
            'Uce142fc90e26599eb9df68c2cef86449',
            'U9ab8c3592aea16310b037f9084cef854'
        ]

    @patch('src.utils.config.load_dotenv')
    @patch('src.utils.config.os.getenv')
    @patch.dict(os.environ, {
        'TARGET_URL': 'https://test.com',
        'LINE_CHANNEL_ACCESS_TOKEN_2': 'test_token_2',
        'LINE_USER_IDS_2': 'user1,user2',
        'LINE_GROUP_IDS_2': 'group1,group2'
    }, clear=True)
    def test_load_second_line_account_config(self, mock_getenv, mock_load_dotenv):
        """Test loading second LINE account configuration"""
        # Arrange
        mock_getenv.return_value = None

        # Act
        config = load_config()

        # Assert
        assert config['line_channel_access_token_2'] == 'test_token_2'
        assert config['line_user_ids_2'] == ['user1', 'user2']
        assert config['line_group_ids_2'] == ['group1', 'group2']

    @patch('src.utils.config.load_dotenv')
    @patch('src.utils.config.os.getenv')
    @patch.dict(os.environ, {'TARGET_URL': 'https://test.com'}, clear=True)
    def test_optional_second_line_account(self, mock_getenv, mock_load_dotenv):
        """Test that second LINE account credentials are optional"""
        # Arrange
        mock_getenv.return_value = None

        # Act
        config = load_config()

        # Assert
        assert config['line_channel_access_token_2'] is None
        assert config['line_user_ids_2'] == []
        assert config['line_group_ids_2'] == []
