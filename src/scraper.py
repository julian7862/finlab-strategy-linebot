import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class FinlabStrategyScraper:
    """
    用於抓取 Finlab 策略持股資料的爬蟲類別
    """

    def __init__(self):
        """初始化 Scraper"""
        self.driver = None

    def _setup_driver(self):
        """設定 Chrome WebDriver"""
        options = Options()
        options.add_argument('--headless')  # 無頭模式
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        # 模擬一般使用者 User-Agent，避免被簡單擋下
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

    def scrape(self, url):
        """
        抓取目標網址的持股資料

        Args:
            url (str): 目標網址

        Returns:
            dict: 包含 holdings 和 open_buy 資料的字典
                {
                    "holdings": [...],
                    "open_buy": [...]
                }
        """
        result_data = {
            "holdings": [],
            "open_buy": []
        }
        try:
            # 設定 WebDriver
            self._setup_driver()

            print(f"正在訪問: {url}")
            self.driver.get(url)

            # 等待頁面載入
            print("等待頁面載入...")
            time.sleep(5)

            # 建立 WebDriverWait 物件
            wait = WebDriverWait(self.driver, 8)

            # 切換進入 Iframe (關鍵修正)
            print("正在尋找並切換至 iframe...")
            try:
                # 等待 id="reportIframe" 出現，並且自動切換進去
                # 這是 Selenium 專門處理 iframe 的等待條件
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "reportIframe")))
                print("成功切換進入 iframe Context")
            except Exception as e:
                print(f"切換 iframe 失敗 (可能網頁結構改變或載入過慢): {e}")
                # 如果切換失敗，後面的動作大概率會錯，但我們還是讓它繼續嘗試

            # 點擊「選股」Tab (現在我們已經在 iframe 裡了)
            try:
                print("正在尋找 '選股' 分頁按鈕...")

                # 這裡維持上一版的邏輯，抓取 tablist 裡的第二個 a
                stock_tab_locator = (By.CSS_SELECTOR, "div[role='tablist'] > a:last-child")

                stock_tab = wait.until(EC.presence_of_element_located(stock_tab_locator))

                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", stock_tab)
                time.sleep(1)

                print("嘗試點擊 '選股'...")
                self.driver.execute_script("arguments[0].click();", stock_tab)

                print("已觸發點擊，等待資料載入...")
                time.sleep(3)

            except Exception as e:
                print(f"點擊 '選股' 分頁失敗: {e}")

            # 等待表格資料出現
            print("正在等待表格資料載入...")
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr")))
                print("表格資料已載入")
            except:
                print("表格載入超時，嘗試直接抓取...")

            print("抓取持股資料中...")

            # 定位表格列 (Rows)
            rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            print(f"找到 {len(rows)} 行持股資料")

            for row in rows:
                item = {}

                # 1. 股票名稱 (whitespace-nowrap font-bold text-base-content-300)
                try:
                    el = row.find_element(By.CSS_SELECTOR, ".whitespace-nowrap.font-bold.text-base-content-300")
                    item['name'] = el.text.strip()
                except:
                    item['name'] = "N/A"

                # 2. 股票代號 (font-light text-base-content-200)
                try:
                    el = row.find_element(By.CSS_SELECTOR, ".font-light.text-base-content-200")
                    item['stock_id'] = el.text.strip()
                except:
                    item['stock_id'] = "N/A"

                # 3. lining-nums svelte-1nx0ef2 (這裡特指 entryDate 下的)
                try:
                    # 使用 slot='entryDate' 定位比較準確
                    el = row.find_element(By.CSS_SELECTOR, "div[slot='entryDate'] .lining-nums.svelte-1nx0ef2")
                    item['entry_date'] = el.text.strip()
                except:
                    # 若抓不到，嘗試抓該行所有的 lining-nums
                    item['entry_date'] = "N/A"

                # 4. 抓取獲利趴數 (利用 slot="profit" 定位，無視紅綠色 class)
                try:
                    # 找 slot="profit" 裡面的第一個 span
                    profit_el = row.find_element(By.CSS_SELECTOR, "div[slot='profit'] span:first-child")
                    item['profit_percentage'] = profit_el.text.strip()
                except:
                    item['profit_percentage'] = "N/A"

                # 5. 抓取目前權重 (利用 slot="currentWeight" 定位)
                try:
                    # 找 slot="currentWeight" 裡面的 span
                    weight_el = row.find_element(By.CSS_SELECTOR, "div[slot='currentWeight'] span")
                    item['current_weight'] = weight_el.text.strip()
                except:
                    item['current_weight'] = "N/A"

                result_data["holdings"].append(item)

            print(f"成功抓取 {len(result_data['holdings'])} 筆持股資料")

            # 抓取「開盤買入」區塊
            try:
                print("正在尋找「開盤買入」區塊...")
                # 尋找是否有 h2 標題為「開盤買入」
                open_buy_headers = self.driver.find_elements(By.XPATH, "//h2[text()='開盤買入']")

                if len(open_buy_headers) > 0:
                    print("✅ 偵測到「開盤買入」區塊，開始抓取...")
                    # 定位到開盤買入下方的 grid 容器內的所有股票 div
                    items_xpath = "//h2[text()='開盤買入']/parent::div/following-sibling::div[contains(@class, 'grid')]/div"
                    stock_items = self.driver.find_elements(By.XPATH, items_xpath)

                    for item in stock_items:
                        stock_data = {}
                        try:
                            name_el = item.find_element(By.CSS_SELECTOR, ".whitespace-nowrap.font-bold.text-base-content-200")
                            stock_data['name'] = name_el.text.strip()
                        except:
                            stock_data['name'] = "N/A"

                        try:
                            id_el = item.find_element(By.CSS_SELECTOR, ".font-light.text-base-content-300")
                            stock_data['stock_id'] = id_el.text.strip()
                        except:
                            stock_data['stock_id'] = "N/A"

                        result_data["open_buy"].append(stock_data)

                    print(f"✅ 成功抓取 {len(result_data['open_buy'])} 筆開盤買入資料")
                else:
                    print("ℹ️ 畫面上未偵測到「開盤買入」區塊。")

            except Exception as e:
                print(f"抓取「開盤買入」時發生錯誤: {e}")

            return result_data

        except Exception as e:
            print(f"抓取過程發生錯誤: {e}")
            raise

        finally:
            # 關閉瀏覽器
            if self.driver:
                self.driver.quit()
                print("瀏覽器已關閉")
