"""
Unit tests for FinlabStrategyScraper
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.scraper import FinlabStrategyScraper


class TestFinlabStrategyScraper:
    """Test suite for FinlabStrategyScraper class"""

    def test_init(self):
        """Test scraper initialization"""
        scraper = FinlabStrategyScraper()
        assert scraper.driver is None

    @patch('src.scraper.ChromeDriverManager')
    @patch('src.scraper.webdriver.Chrome')
    def test_setup_driver(self, mock_chrome, mock_driver_manager):
        """Test WebDriver setup with correct options"""
        # Arrange
        mock_driver_instance = Mock()
        mock_chrome.return_value = mock_driver_instance
        mock_driver_manager.return_value.install.return_value = '/path/to/chromedriver'

        scraper = FinlabStrategyScraper()

        # Act
        scraper._setup_driver()

        # Assert
        assert scraper.driver == mock_driver_instance
        mock_chrome.assert_called_once()

        # Verify Chrome options were set
        call_args = mock_chrome.call_args
        options = call_args.kwargs['options']

        # Check that headless mode and other options are set
        assert '--headless' in options.arguments
        assert '--no-sandbox' in options.arguments
        assert '--disable-dev-shm-usage' in options.arguments
        assert '--disable-gpu' in options.arguments

    @patch('src.scraper.ChromeDriverManager')
    @patch('src.scraper.webdriver.Chrome')
    @patch('src.scraper.time.sleep')
    def test_scrape_success(self, mock_sleep, mock_chrome, mock_driver_manager):
        """Test successful scraping flow"""
        # Arrange
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_driver_manager.return_value.install.return_value = '/path/to/chromedriver'

        scraper = FinlabStrategyScraper()
        test_url = "https://example.com"

        # Act
        result = scraper.scrape(test_url)

        # Assert
        mock_driver.get.assert_called_once_with(test_url)
        mock_driver.quit.assert_called_once()
        assert isinstance(result, list)
        assert result == []  # Current implementation returns empty list

    @patch('src.scraper.ChromeDriverManager')
    @patch('src.scraper.webdriver.Chrome')
    def test_scrape_exception_handling(self, mock_chrome, mock_driver_manager):
        """Test scraper handles exceptions properly"""
        # Arrange
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_driver_manager.return_value.install.return_value = '/path/to/chromedriver'

        # Simulate an error during scraping
        mock_driver.get.side_effect = Exception("Network error")

        scraper = FinlabStrategyScraper()
        test_url = "https://example.com"

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            scraper.scrape(test_url)

        assert "Network error" in str(exc_info.value)
        # Verify driver was still closed
        mock_driver.quit.assert_called_once()

    @patch('src.scraper.ChromeDriverManager')
    @patch('src.scraper.webdriver.Chrome')
    def test_scrape_driver_cleanup_on_error(self, mock_chrome, mock_driver_manager):
        """Test that driver is cleaned up even when errors occur"""
        # Arrange
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_driver_manager.return_value.install.return_value = '/path/to/chromedriver'

        # Simulate error after driver setup
        mock_driver.get.side_effect = RuntimeError("Page load failed")

        scraper = FinlabStrategyScraper()
        test_url = "https://example.com"

        # Act & Assert
        with pytest.raises(RuntimeError):
            scraper.scrape(test_url)

        # Verify cleanup happened
        mock_driver.quit.assert_called_once()

    @patch('src.scraper.ChromeDriverManager')
    @patch('src.scraper.webdriver.Chrome')
    @patch('src.scraper.time.sleep')
    def test_scrape_url_is_accessed(self, mock_sleep, mock_chrome, mock_driver_manager):
        """Test that the correct URL is accessed"""
        # Arrange
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_driver_manager.return_value.install.return_value = '/path/to/chromedriver'

        scraper = FinlabStrategyScraper()
        test_url = "https://finlab.tw/strategy/12345"

        # Act
        scraper.scrape(test_url)

        # Assert
        mock_driver.get.assert_called_once_with(test_url)
        mock_sleep.assert_called_once_with(3)  # Verify wait time

    @patch('src.scraper.ChromeDriverManager')
    @patch('src.scraper.webdriver.Chrome')
    def test_scrape_no_driver_before_setup(self, mock_chrome, mock_driver_manager):
        """Test that driver is None before setup"""
        # Arrange
        scraper = FinlabStrategyScraper()

        # Assert
        assert scraper.driver is None

    @patch('src.scraper.ChromeDriverManager')
    @patch('src.scraper.webdriver.Chrome')
    @patch('src.scraper.time.sleep')
    def test_scrape_sets_driver_after_setup(self, mock_sleep, mock_chrome, mock_driver_manager):
        """Test that driver is set after _setup_driver is called"""
        # Arrange
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_driver_manager.return_value.install.return_value = '/path/to/chromedriver'

        scraper = FinlabStrategyScraper()
        test_url = "https://example.com"

        # Act
        scraper.scrape(test_url)

        # Assert - driver should have been set (but then quit in finally)
        mock_chrome.assert_called_once()
