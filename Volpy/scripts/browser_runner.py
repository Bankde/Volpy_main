from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys

if len(sys.argv) < 2:
    raise Exception("Please specify the URL of web to open")
URL = sys.argv[1]

d = DesiredCapabilities.CHROME
d['goog:loggingPrefs'] = {'browser': 'ALL'}
d['pageLoadStrategy'] = "none"

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=chrome_options, desired_capabilities=d)
driver.set_script_timeout(10000000);
driver.execute("get", {'url': URL})
print("Open the web")

if len(sys.argv) == 3:
    print("worker count: %s" % sys.argv[2])
    coreInput = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "workerNum")))
    coreInput.send_keys(sys.argv[2])
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "runNodeBtn"))).click()
print("Connection started")

input("Press enter to exit")

driver.close()
driver.quit()