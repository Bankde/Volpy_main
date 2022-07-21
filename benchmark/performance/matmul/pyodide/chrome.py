from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time

d = DesiredCapabilities.CHROME
d['goog:loggingPrefs'] = {'browser': 'ALL'}
d['pageLoadStrategy'] = "none"

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=chrome_options, desired_capabilities=d)
driver.get("file:///home/bankde/benchmark/performance/matmul/pyodide/pyodide.html")

while True:
    if driver.title == "Done": break
    time.sleep(5)

for entry in driver.get_log('browser'):
    print(entry)

driver.close()
