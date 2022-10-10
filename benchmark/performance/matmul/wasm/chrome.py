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
driver.set_script_timeout(10000000);
driver.execute_script(open("./wasmJS.js").read())

with open("result.txt", "w") as f:
    while driver.title != "Done":
        for entry in driver.get_log('browser'):
            print(entry)
            f.write(entry + "\n")
        time.sleep(3)

driver.close()
