import os
from time import sleep
from selenium import webdriver
from requests import Session, Response, exceptions

class RequestApi:
    def __init__(self, endpoint, **kwargs):
        self._endpoint = endpoint
        self._session = Session()

    # Handle erroring
    def _process_response(self, res:Response):
        try:
            res.raise_for_status() 
        except exceptions.HTTPError as err:
            print(f'HTTP error occurred: {err}')  
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        return res

    def post(self, url, **kwargs):
        res = self._session.post(self._endpoint+url, **kwargs)
        return self._process_response(res)

    def get(self, url, **kwargs):
        res = self._session.get(self._endpoint+url, **kwargs)
        return self._process_response(res)


def tradingview_screenshot(username, password, symbol=None, exchange=None):
    tv = RequestApi(endpoint='https://www.tradingview.com')

    # Define login credentials
    login_header = {
    'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 RuxitSynthetic/1.0 v5127394012308686022 t7015169992710824681 athe94ac249 altpriv cvcv=2 cexpw=1 smf=0',
    # 'cookies': 'cookiePrivacyPreferenceBannerProduction=notApplicable; cookiesSettings={"analytics":true,"advertising":true}; _ga=GA1.2.1842261804.1676872804; __gads=ID=4ec6edbe23c30ecf:T=1676883671:S=ALNI_MbToT4qcFeW-adxBI7S9pQbPN5pnw; g_state={"i_p":1676913037581,"i_l":1}; _gid=GA1.2.718277533.1677042602; tv_ecuid_sign_in_popup=1; __gpi=UID=00000bc776ccc779:T=1676883671:RT=1677043041:S=ALNI_MZYatGd7yPzYdSUArAf17dYgIe0Vg; device_t=dG9rTEF3OjE.SzJ6Q_gOuAJIClmzrDQ3AfxivbXAS2Qvh2_pU_-pNqw; _sp_ses.cf1a=*; png=227913b5-406e-4876-9187-a389b21e5c7d; etg=227913b5-406e-4876-9187-a389b21e5c7d; cachec=227913b5-406e-4876-9187-a389b21e5c7d; tv_ecuid=227913b5-406e-4876-9187-a389b21e5c7d; _gat_gtag_UA_24278967_1=1; _sp_id.cf1a=3232cd49-95ff-41c7-8249-e188be6d24ae.1676872799.8.1677047011.1677043484.eefa6567-5c8a-4abc-98a3-ad6b0147eead',
    'referer': 'https://www.tradingview.com/chart',
    }

    login_data = {'username': username, 'password': password, 'remember': 'off'}

    r = tv.post(
            url='/accounts/signin/', 
            headers=login_header, 
            data=login_data    
    )
    if r.status_code == 200:
        print('Login successful!')

        # Automate find chromedriver path
        path = os.path.dirname(os.path.realpath(__file__))
        chr = "chromedriver\chromedriver.exe"
        chr_path = os.path.join(path, chr)

        # Start a selenium web driver
        driver = webdriver.Chrome(executable_path=chr_path)

        # Use session cookies to auth selenium driver
        driver.get(tv._endpoint+'/accounts/signin/')
        driver.maximize_window()
        for cookie in tv._session.cookies:
            driver.add_cookie({
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain
            })

        # Go to web page we want to scrape
        # driver.get('https://www.tradingview.com/chart/')
        driver.get(tv._endpoint+'/chart?client=chart&lang=en&symbol=FX%3A'+symbol)
        sleep(6)
        driver.save_screenshot(path+'\screenshot.png')
        driver.quit()
        tv._session.close()

    else:
        print('Login failed!')

if __name__ == "__main__":

    tradingview_screenshot(
            username='test.eaforex@gmail.com',
            password='123456789zz**',
            symbol='AUDUSD'
    )

