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
                'LINE_USER_ID': 'test_user',
                'LINE_WEBHOOK_URL': 'https://webhook.com'
            }
            return env_values.get(key, default)

        mock_getenv.side_effect = getenv_side_effect

        # Act
        config = load_config()

        # Assert
        assert config['target_url'] == 'https://example.com'
        assert config['line_channel_access_token'] == 'test_token'
        assert config['line_user_id'] == 'test_user'
        assert config['line_webhook_url'] == 'https://webhook.com'
        mock_load_dotenv.assert_called_once()

    @patch('src.utils.config.load_dotenv')
    @patch.dict(os.environ, {
        'TARGET_URL': 'https://os-env.com',
        'LINE_CHANNEL_ACCESS_TOKEN': 'os_token',
        'LINE_USER_ID': 'os_user',
        'LINE_WEBHOOK_URL': 'https://os-webhook.com'
    })
    def test_load_from_os_environ(self, mock_load_dotenv):
        """Test loading from OS environment variables"""
        # Act
        config = load_config()

        # Assert
        assert config['target_url'] == 'https://os-env.com'
        assert config['line_channel_access_token'] == 'os_token'
        assert config['line_user_id'] == 'os_user'
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
        assert config['line_user_id'] is None
        assert config['line_webhook_url'] is None
