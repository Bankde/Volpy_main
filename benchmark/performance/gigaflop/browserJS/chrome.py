from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

d = DesiredCapabilities.CHROME
d['goog:loggingPrefs'] = {'browser': 'ALL'}

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=chrome_options, desired_capabilities=d)
driver.execute_script(open("./nativeJS.js").read())

for entry in driver.get_log('browser'):
    print(entry)

driver.close()
