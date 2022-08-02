from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import os

d = DesiredCapabilities.CHROME
d['goog:loggingPrefs'] = {'browser': 'ALL'}
d['acceptInsecureCerts'] = True

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('ignore-certificate-errors')
driver = webdriver.Chrome(options=chrome_options, desired_capabilities=d)
driver.get("https://" + os.environ["SERVER"] + ":8443/index.html")

for i in range(40):
    for entry in driver.get_log('browser'):
        print(entry)
    time.sleep(2)

driver.close()
