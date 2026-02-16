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
            list: 包含持股資料的字典列表
        """
        data_list = []
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

            print("抓取資料中...")

            # 定位表格列 (Rows)
            rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            print(f"找到 {len(rows)} 行資料")

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

                # 4. text-error svelte-1nx0ef2 (獲利趴數 & 權重)
                try:
                    # 這兩個通常都是紅色字體，順序通常是: 獲利 -> 權重
                    error_items = row.find_elements(By.CSS_SELECTOR, ".text-error.svelte-1nx0ef2")

                    if len(error_items) >= 1:
                        item['profit_percentage'] = error_items[0].text.strip()
                    else:
                        item['profit_percentage'] = "N/A"

                    if len(error_items) >= 2:
                        item['current_weight'] = error_items[1].text.strip()
                    else:
                        item['current_weight'] = "N/A"
                except:
                    item['profit_percentage'] = "N/A"
                    item['current_weight'] = "N/A"

                data_list.append(item)

            print(f"成功抓取 {len(data_list)} 筆資料")
            return data_list

        except Exception as e:
            print(f"抓取過程發生錯誤: {e}")
            raise

        finally:
            # 關閉瀏覽器
            if self.driver:
                self.driver.quit()
                print("瀏覽器已關閉")
