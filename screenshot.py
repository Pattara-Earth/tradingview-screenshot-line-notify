import os
import warnings
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from requests import Session, Response, exceptions
from selenium.webdriver.chrome.options import Options

warnings.filterwarnings("ignore")

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

    # Login and keep session cookies 
    def login(self):
        url = self._endpoint+'/accounts/signin/'
        headers = {
                'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.3) AppleWebKit/535.0.2 \
                (KHTML, like Gecko) Chrome/31.0.824.0 Safari/535.0.2',
                'referer': 'https://www.tradingview.com/chart',
            }
        payload = {'username':self._username, 'password':self._password, 'remember':'off'}
        res = self._session.post(url=url, headers=headers, data=payload)
        return res

    # Select layout
    def layout_image_url(self):
        image_url = None
        res = self._session.get(url=self._endpoint+'/my-charts', params={'limit':5})
        for lay in res.json(): 
            # print("{}:{}".format(lay['name'], lay['image_url']))
            if lay['name'] == self._layout: 
                image_url = lay['image_url']
        return image_url

    # Select custom templates
    def templates_id(self):
        id = None
        res = self._session.get(url=self._endpoint+'/api/v1/study-templates')
        for tem in res.json()['custom']:
            # print("{}:{}".format(id['name'], id['id']))
            if tem['name'] == self._template:
                id = tem['id']
        return id

    # Use session cookies to auth selenium driver
    def auth_driver(self, driver):
        # driver.maximize_window()
        # driver.set_window_size(1920, 1080) 
        driver.get(self._endpoint+'/accounts/signin/')
        for cookie in self._session.cookies:
            driver.add_cookie({
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain
            })

    # Go to web page that has been wanted to scrape
    def tdv_chart_page(self, driver):
        img_url = self.layout_image_url()
        driver.get(self._endpoint+f'/chart/{img_url}?client=chart&lang=en&symbol={self._exchange.upper()}%3A{self._symbol.upper()}&interval={self._interval}')
        
    # Close floating toolbar right side
    def close_toolbar1(self, driver):
        if driver.find_element(By.CLASS_NAME, "tv-floating-toolbar__widget-wrapper"):
            element = driver.find_element(By.XPATH, "/html/body/div[2]/div[5]/div/div/div[1]/div/div/div[6]/div")
            driver.execute_script("arguments[0].click();", element)

    # Close floating toolbar mini
    def close_toolbar2(self, driver):
        if driver.find_element(By.CLASS_NAME, "iconArrow-G1_Pfvwd"):
            element = driver.find_element(By.XPATH, " /html/body/div[2]/div[1]/div[2]/div[1]/div/table/tr[1]/td[2]/div/div[2]/div[2]/div[1]/div[1]")
            driver.execute_script("arguments[0].click();", element)

    # Capture tdv chart
    def cap_screen_chart(self, driver, path):
        element = driver.find_element(By.CLASS_NAME, "chart-markup-table")
        element.screenshot(path+'\screenshot.png')

    def done(self, driver):
        driver.quit()
        self._session.close()

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

        if self.login().status_code == 200:
            print('Login successfully!')
            self.auth_driver(driver)
            self.tdv_chart_page(driver)
            sleep(5)
            self.close_toolbar1(driver)
            self.close_toolbar2(driver)
            sleep(1)
            self.cap_screen_chart(driver, path)
            print('screenshot successfully!')
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
    )

    tdv.main()

    
