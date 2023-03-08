import os
import json
import warnings
from time import sleep
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from requests import Session, Response, exceptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ScreenshotTDV:
    def __init__(
            self, username, password, exchange, symbol,  
            interval, template=None, layout='Alert'
    ):
        self._username = username
        self._password = password
        self._exchange = exchange
        self._symbol = symbol
        self._interval = interval
        self._template = template
        self._layout = layout
        self._session = Session()
        self._endpoint = 'https://www.tradingview.com'
    
    warnings.filterwarnings("ignore")

    # Login and keep session cookies 
    def login(self):
        url = self._endpoint+'/accounts/signin/'
        headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36 RuxitSynthetic/1.0 v7321049631929259831 t6662866128547677118',
                'referer': 'https://www.tradingview.com/chart',
            }
        payload = {'username':self._username, 'password':self._password, 'remember':'off'}
        res = self._session.post(url=url, headers=headers, data=payload)
        return res

    # Select layout
    def _layout_image_url(self):
        image_url = None
        res = self._session.get(url=self._endpoint+'/my-charts', params={'limit':5})
        layouts = [lay['name'] for lay in res.json()]
        result = self._word_matching(self._layout, layouts)
        word = list(result.keys())[0]
        for lay in res.json():
            if lay['name'] == word:
                image_url = lay['image_url']
                print(f"{lay['name']}: {image_url}")
        return image_url

    # Select custom templates
    def _templates_name(self):
        res = self._session.get(url=self._endpoint+'/api/v1/study-templates')
        templates = [tem['name'] for tem in res.json()['custom']]
        result = self._word_matching(self._template, templates)
        tem_name = list(result.keys())[0]
        print(f'Select tempalte: {tem_name}')
        return tem_name

    # Use session cookies to auth selenium driver
    def auth_driver(self, driver):
        driver.maximize_window()
        # driver.set_window_size(1920, 1080) 
        driver.get(self._endpoint+'/accounts/signin/')
        for cookie in self._session.cookies:
            driver.add_cookie({
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain
            })
    
    # Set template for default template chart
    def set_template(self, driver):
        template = self._templates_name()
        try:
            action_chains = ActionChains(driver)
            driver.get(self._endpoint+'/chart')
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#header-toolbar-study-templates > div.button-reABrhVR.apply-common-tooltip > div > span"))).click()
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"[data-name='{template}']"))).click()
            sleep(3)
            action_chains.key_down(Keys.CONTROL)
            action_chains.send_keys("s").perform()
            action_chains.key_up(Keys.CONTROL)
            print('Set template successfully')
        except:
            print('Failed to set template')

    # Handle alert pop up
    def _handle_alert(self, driver):
        try:
            alert = driver.switch_to.alert
            alert.accept()
            print("Alert dismissed")
        except:
            print("No alert found")

    # Go to web page that has been wanted to scrape
    def tdv_chart_page(self, driver):
        img_url = self._layout_image_url()
        driver.get(self._endpoint+f'/chart/{img_url}?client=chart&lang=en&symbol={self._exchange.upper()}%3A{self._symbol.upper()}&interval={self._interval}')
        sleep(2)
        self._handle_alert(driver)
        print(f'Currently chart {self._exchange} {self._symbol} {self._interval}')

    # Close floating toolbar 
    def close_widgetbar(self, driver):
        try:
            driver.find_element(By.XPATH, ".//div[@title='Hide Tab']")
            element = driver.find_element(By.XPATH, "/html/body/div[2]/div[6]/div/div[3]/div")
            driver.execute_script("arguments[0].click();", element)
            print("Closed widgetber")
        except:
            print("No widgetber for closed")

    # Close floating toolbar 
    def close_toolbar(self, driver):
        try:
            driver.find_element(By.CLASS_NAME, "tv-floating-toolbar__widget-wrapper")
            element = driver.find_element(By.XPATH, "/html/body/div[2]/div[5]/div/div/div[1]/div/div/div[6]/div")
            driver.execute_script("arguments[0].click();", element)
            print('Closed toolbar')
        except:
            print('No toolbar for closed')

    # Close icon arrow
    def close_icon_arrow(self, driver):
        try:
            driver.find_element(By.XPATH, ".//div[@title='Hide Indicator Legend']")
            element = driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/div[2]/div[1]/div/table/tr[1]/td[2]/div/div[2]/div[2]/div[1]/div[1]")
            driver.execute_script("arguments[0].click();", element)
            print("Closed legend title")
        except:
            print("No legend title for closed")

    # Capture tdv chart
    def cap_screen_chart(self, driver, path:str):
        element = driver.find_element(By.CLASS_NAME, "chart-markup-table")
        element.screenshot(path+'\screenshot.png')
        print('screenshot successfully!')

    def done(self, driver):
        driver.quit()
        self._session.close()
    
    # Memo function for edit distance algo
    def memo(self):
        global memo
        memo = {}

    # Edit distance algo
    def _edit_distance(self, s, t):
        if s == "":
            return len(t)
        if t == "":
            return len(s)
        cost = 0 if s[-1] == t[-1] else 1
        
        i1 = (s[:-1], t)
        if not i1 in memo:
            memo[i1] = self._edit_distance(*i1)
        i2 = (s, t[:-1])
        if not i2 in memo:
            memo[i2] = self._edit_distance(*i2)
        i3 = (s[:-1], t[:-1])
        if not i3 in memo:
            memo[i3] = self._edit_distance(*i3)
        res = min([memo[i1]+1, memo[i2]+1, memo[i3]+cost])
        return res
    
    # Word matching
    def _word_matching(self, search:str, targets:list):
        self.memo()
        min_distance = dict()
        for target in targets:
            distance = self._edit_distance(search, target)
            min_distance[str(target)] = distance
        return dict(sorted(min_distance.items(), key=lambda item: item[1]))

    def main(self):
        # Automate find chromedriver path
        path = os.path.dirname(os.path.realpath(__file__))
        chr = "chromedriver_win\chromedriver.exe"
        chr_path = os.path.join(path, chr)

        # Start a selenium web driver
        options = Options()
        options.add_argument('--headless')
        options.add_argument("window-size=1400,800")
        driver = webdriver.Chrome(executable_path=chr_path, options=options)
        res = self.login()
        with open("captcha.json", "w") as f:
                json.dump(res.json(), f)
        if res.status_code == 200:
            if 'captcha' in res.json()['error']:
                print('Recaptcha required')
            else:
                print('Login successfully!')
                self.auth_driver(driver)
                self.set_template(driver)
                self.tdv_chart_page(driver)
                sleep(5)
                self.close_widgetbar(driver)
                self.close_toolbar(driver)
                self.close_icon_arrow(driver)
                sleep(3)
                self.cap_screen_chart(driver, path)
                self.done(driver)
        else:
            print('Login failed!')


if __name__ == '__main__':
    tdv = ScreenshotTDV(
                username='',
                password='',
                exchange='',
                symbol='',
                interval='',
                template=''
    )

    tdv.main()

    

