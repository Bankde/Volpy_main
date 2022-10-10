from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
import time

d = DesiredCapabilities.CHROME
d['goog:loggingPrefs'] = {'browser': 'ALL'}
d['pageLoadStrategy'] = "none"

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=chrome_options, desired_capabilities=d)
driver.set_script_timeout(10000000);
driver.get("file:///home/bankde/benchmark/performance/matmul/pyodide/pyodide.html")

while driver.title != "Done":
    time.sleep(3)

with open("result.txt", "w") as f:
    data = driver.find_element(By.TAG_NAME, "body").text
    print(data)
    f.write(data)

driver.close()
driver.quit()