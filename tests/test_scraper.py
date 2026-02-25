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
        assert '--disable-gpu' in options.arguments
        # Check user-agent is set
        assert any('user-agent=' in arg for arg in options.arguments)

    @patch('src.scraper.ChromeDriverManager')
    @patch('src.scraper.webdriver.Chrome')
    @patch('src.scraper.time.sleep')
    def test_scrape_success(self, mock_sleep, mock_chrome, mock_driver_manager):
        """Test successful scraping flow"""
        # Arrange
        mock_driver = Mock()
        mock_driver.find_elements.return_value = []  # Return empty list for rows
        mock_chrome.return_value = mock_driver
        mock_driver_manager.return_value.install.return_value = '/path/to/chromedriver'

        scraper = FinlabStrategyScraper()
        test_url = "https://example.com"

        # Act
        result = scraper.scrape(test_url)

        # Assert
        mock_driver.get.assert_called_once_with(test_url)
        mock_driver.quit.assert_called_once()
        assert isinstance(result, dict)
        assert "holdings" in result
        assert "open_buy" in result
        assert result["holdings"] == []
        assert result["open_buy"] == []

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
        mock_driver.find_elements.return_value = []  # Return empty list for rows
        mock_chrome.return_value = mock_driver
        mock_driver_manager.return_value.install.return_value = '/path/to/chromedriver'

        scraper = FinlabStrategyScraper()
        test_url = "https://finlab.tw/strategy/12345"

        # Act
        scraper.scrape(test_url)

        # Assert
        mock_driver.get.assert_called_once_with(test_url)
        # Verify that sleep was called with 5 (initial page load wait)
        assert any(call[0][0] == 5 for call in mock_sleep.call_args_list)

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
        mock_driver.find_elements.return_value = []  # Return empty list for rows
        mock_chrome.return_value = mock_driver
        mock_driver_manager.return_value.install.return_value = '/path/to/chromedriver'

        scraper = FinlabStrategyScraper()
        test_url = "https://example.com"

        # Act
        scraper.scrape(test_url)

        # Assert - driver should have been set (but then quit in finally)
        mock_chrome.assert_called_once()

    @patch('src.scraper.ChromeDriverManager')
    @patch('src.scraper.webdriver.Chrome')
    @patch('src.scraper.time.sleep')
    def test_scrape_with_open_buy_section(self, mock_sleep, mock_chrome, mock_driver_manager):
        """Test scraping when 開盤買入 section exists with data"""
        # Arrange
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_driver_manager.return_value.install.return_value = '/path/to/chromedriver'

        # Mock holdings table rows (empty for simplicity)
        mock_driver.find_elements.return_value = []

        # Create mock for open_buy section
        mock_h2_element = Mock()
        mock_open_buy_item = Mock()

        # Mock stock name and ID elements
        mock_name_el = Mock()
        mock_name_el.text = "測試股票"
        mock_id_el = Mock()
        mock_id_el.text = "1234"

        mock_open_buy_item.find_element.side_effect = lambda by, selector: {
            ".whitespace-nowrap.font-bold.text-base-content-200": mock_name_el,
            ".font-light.text-base-content-300": mock_id_el
        }.get(selector, Mock())

        # Configure find_elements to return different values based on XPath
        def find_elements_side_effect(by, selector):
            if selector == "table tbody tr":
                return []  # No holdings
            elif selector == "//h2[text()='開盤買入']":
                return [mock_h2_element]  # Header exists
            elif "//h2[text()='開盤買入']/parent::div/following-sibling::div" in selector:
                return [mock_open_buy_item]  # One stock item
            return []

        mock_driver.find_elements.side_effect = find_elements_side_effect

        scraper = FinlabStrategyScraper()
        test_url = "https://example.com"

        # Act
        result = scraper.scrape(test_url)

        # Assert
        assert isinstance(result, dict)
        assert "holdings" in result
        assert "open_buy" in result
        assert len(result["open_buy"]) == 1
        assert result["open_buy"][0]["name"] == "測試股票"
        assert result["open_buy"][0]["stock_id"] == "1234"

    @patch('src.scraper.ChromeDriverManager')
    @patch('src.scraper.webdriver.Chrome')
    @patch('src.scraper.time.sleep')
    def test_scrape_without_open_buy_section(self, mock_sleep, mock_chrome, mock_driver_manager):
        """Test scraping when 開盤買入 section doesn't exist"""
        # Arrange
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_driver_manager.return_value.install.return_value = '/path/to/chromedriver'

        # Configure find_elements to return empty for open_buy header
        def find_elements_side_effect(by, selector):
            if selector == "table tbody tr":
                return []  # No holdings
            elif selector == "//h2[text()='開盤買入']":
                return []  # Header doesn't exist
            return []

        mock_driver.find_elements.side_effect = find_elements_side_effect

        scraper = FinlabStrategyScraper()
        test_url = "https://example.com"

        # Act
        result = scraper.scrape(test_url)

        # Assert
        assert isinstance(result, dict)
        assert "holdings" in result
        assert "open_buy" in result
        assert result["open_buy"] == []  # Empty when section doesn't exist

    @patch('src.scraper.ChromeDriverManager')
    @patch('src.scraper.webdriver.Chrome')
    @patch('src.scraper.time.sleep')
    def test_scrape_with_multiple_open_buy_stocks(self, mock_sleep, mock_chrome, mock_driver_manager):
        """Test scraping when 開盤買入 section has multiple stocks"""
        # Arrange
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_driver_manager.return_value.install.return_value = '/path/to/chromedriver'

        # Create mock elements for two stocks
        mock_h2_element = Mock()

        # First stock
        mock_item1 = Mock()
        mock_name1 = Mock()
        mock_name1.text = "科嶠"
        mock_id1 = Mock()
        mock_id1.text = "4542"

        mock_item1.find_element.side_effect = lambda by, selector: {
            ".whitespace-nowrap.font-bold.text-base-content-200": mock_name1,
            ".font-light.text-base-content-300": mock_id1
        }.get(selector, Mock())

        # Second stock
        mock_item2 = Mock()
        mock_name2 = Mock()
        mock_name2.text = "青雲"
        mock_id2 = Mock()
        mock_id2.text = "5386"

        mock_item2.find_element.side_effect = lambda by, selector: {
            ".whitespace-nowrap.font-bold.text-base-content-200": mock_name2,
            ".font-light.text-base-content-300": mock_id2
        }.get(selector, Mock())

        # Configure find_elements
        def find_elements_side_effect(by, selector):
            if selector == "table tbody tr":
                return []  # No holdings
            elif selector == "//h2[text()='開盤買入']":
                return [mock_h2_element]  # Header exists
            elif "//h2[text()='開盤買入']/parent::div/following-sibling::div" in selector:
                return [mock_item1, mock_item2]  # Two stock items
            return []

        mock_driver.find_elements.side_effect = find_elements_side_effect

        scraper = FinlabStrategyScraper()
        test_url = "https://example.com"

        # Act
        result = scraper.scrape(test_url)

        # Assert
        assert isinstance(result, dict)
        assert len(result["open_buy"]) == 2
        assert result["open_buy"][0]["name"] == "科嶠"
        assert result["open_buy"][0]["stock_id"] == "4542"
        assert result["open_buy"][1]["name"] == "青雲"
        assert result["open_buy"][1]["stock_id"] == "5386"

    @patch('src.scraper.ChromeDriverManager')
    @patch('src.scraper.webdriver.Chrome')
    @patch('src.scraper.time.sleep')
    def test_scrape_open_buy_with_missing_fields(self, mock_sleep, mock_chrome, mock_driver_manager):
        """Test scraping 開盤買入 when fields are missing"""
        # Arrange
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_driver_manager.return_value.install.return_value = '/path/to/chromedriver'

        mock_h2_element = Mock()
        mock_open_buy_item = Mock()

        # Mock find_element to raise exception (simulating missing elements)
        mock_open_buy_item.find_element.side_effect = Exception("Element not found")

        # Configure find_elements
        def find_elements_side_effect(by, selector):
            if selector == "table tbody tr":
                return []
            elif selector == "//h2[text()='開盤買入']":
                return [mock_h2_element]
            elif "//h2[text()='開盤買入']/parent::div/following-sibling::div" in selector:
                return [mock_open_buy_item]
            return []

        mock_driver.find_elements.side_effect = find_elements_side_effect

        scraper = FinlabStrategyScraper()
        test_url = "https://example.com"

        # Act
        result = scraper.scrape(test_url)

        # Assert
        assert isinstance(result, dict)
        assert len(result["open_buy"]) == 1
        assert result["open_buy"][0]["name"] == "N/A"
        assert result["open_buy"][0]["stock_id"] == "N/A"

    @patch('src.scraper.ChromeDriverManager')
    @patch('src.scraper.webdriver.Chrome')
    @patch('src.scraper.time.sleep')
    def test_scrape_holdings_with_positive_and_negative_profits(self, mock_sleep, mock_chrome, mock_driver_manager):
        """Test scraping holdings with both positive and negative profit percentages using slot attributes"""
        # Arrange
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_driver_manager.return_value.install.return_value = '/path/to/chromedriver'

        # Create mock rows - one with positive profit, one with negative profit
        mock_row1 = Mock()
        mock_row2 = Mock()

        # Row 1: Positive profit (+15.5%)
        mock_name1 = Mock()
        mock_name1.text = "台積電"
        mock_id1 = Mock()
        mock_id1.text = "2330"
        mock_date1 = Mock()
        mock_date1.text = "2024-01-15"
        mock_profit1 = Mock()
        mock_profit1.text = "+15.5%"
        mock_weight1 = Mock()
        mock_weight1.text = "25.3%"

        def row1_find_element(by, selector):
            if selector == ".whitespace-nowrap.font-bold.text-base-content-300":
                return mock_name1
            elif selector == ".font-light.text-base-content-200":
                return mock_id1
            elif selector == "div[slot='entryDate'] .lining-nums.svelte-1nx0ef2":
                return mock_date1
            elif selector == "div[slot='profit'] span:first-child":
                return mock_profit1
            elif selector == "div[slot='currentWeight'] span":
                return mock_weight1
            raise Exception(f"Element not found: {selector}")

        mock_row1.find_element.side_effect = row1_find_element

        # Row 2: Negative profit (-8.2%)
        mock_name2 = Mock()
        mock_name2.text = "聯發科"
        mock_id2 = Mock()
        mock_id2.text = "2454"
        mock_date2 = Mock()
        mock_date2.text = "2024-02-10"
        mock_profit2 = Mock()
        mock_profit2.text = "-8.2%"
        mock_weight2 = Mock()
        mock_weight2.text = "18.7%"

        def row2_find_element(by, selector):
            if selector == ".whitespace-nowrap.font-bold.text-base-content-300":
                return mock_name2
            elif selector == ".font-light.text-base-content-200":
                return mock_id2
            elif selector == "div[slot='entryDate'] .lining-nums.svelte-1nx0ef2":
                return mock_date2
            elif selector == "div[slot='profit'] span:first-child":
                return mock_profit2
            elif selector == "div[slot='currentWeight'] span":
                return mock_weight2
            raise Exception(f"Element not found: {selector}")

        mock_row2.find_element.side_effect = row2_find_element

        # Configure find_elements to return our mock rows
        def find_elements_side_effect(by, selector):
            if selector == "table tbody tr":
                return [mock_row1, mock_row2]
            elif selector == "//h2[text()='開盤買入']":
                return []  # No open buy section for this test
            return []

        mock_driver.find_elements.side_effect = find_elements_side_effect

        scraper = FinlabStrategyScraper()
        test_url = "https://example.com"

        # Act
        result = scraper.scrape(test_url)

        # Assert
        assert isinstance(result, dict)
        assert "holdings" in result
        assert len(result["holdings"]) == 2

        # Verify first holding (positive profit)
        assert result["holdings"][0]["name"] == "台積電"
        assert result["holdings"][0]["stock_id"] == "2330"
        assert result["holdings"][0]["entry_date"] == "2024-01-15"
        assert result["holdings"][0]["profit_percentage"] == "+15.5%"
        assert result["holdings"][0]["current_weight"] == "25.3%"

        # Verify second holding (negative profit)
        assert result["holdings"][1]["name"] == "聯發科"
        assert result["holdings"][1]["stock_id"] == "2454"
        assert result["holdings"][1]["entry_date"] == "2024-02-10"
        assert result["holdings"][1]["profit_percentage"] == "-8.2%"
        assert result["holdings"][1]["current_weight"] == "18.7%"

    @patch('src.scraper.ChromeDriverManager')
    @patch('src.scraper.webdriver.Chrome')
    @patch('src.scraper.time.sleep')
    def test_scrape_holdings_with_missing_profit_weight(self, mock_sleep, mock_chrome, mock_driver_manager):
        """Test scraping holdings when profit or weight elements are missing"""
        # Arrange
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_driver_manager.return_value.install.return_value = '/path/to/chromedriver'

        mock_row = Mock()

        # Mock basic fields but profit and weight will throw exceptions
        mock_name = Mock()
        mock_name.text = "測試股票"
        mock_id = Mock()
        mock_id.text = "1234"
        mock_date = Mock()
        mock_date.text = "2024-03-01"

        def row_find_element(by, selector):
            if selector == ".whitespace-nowrap.font-bold.text-base-content-300":
                return mock_name
            elif selector == ".font-light.text-base-content-200":
                return mock_id
            elif selector == "div[slot='entryDate'] .lining-nums.svelte-1nx0ef2":
                return mock_date
            elif selector == "div[slot='profit'] span:first-child":
                raise Exception("Profit element not found")
            elif selector == "div[slot='currentWeight'] span":
                raise Exception("Weight element not found")
            raise Exception(f"Element not found: {selector}")

        mock_row.find_element.side_effect = row_find_element

        # Configure find_elements
        def find_elements_side_effect(by, selector):
            if selector == "table tbody tr":
                return [mock_row]
            elif selector == "//h2[text()='開盤買入']":
                return []
            return []

        mock_driver.find_elements.side_effect = find_elements_side_effect

        scraper = FinlabStrategyScraper()
        test_url = "https://example.com"

        # Act
        result = scraper.scrape(test_url)

        # Assert
        assert isinstance(result, dict)
        assert len(result["holdings"]) == 1
        assert result["holdings"][0]["name"] == "測試股票"
        assert result["holdings"][0]["stock_id"] == "1234"
        assert result["holdings"][0]["entry_date"] == "2024-03-01"
        assert result["holdings"][0]["profit_percentage"] == "N/A"
        assert result["holdings"][0]["current_weight"] == "N/A"
