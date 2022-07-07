from selenium import webdriver

driver = webdriver.Chrome()
assert "Python" in driver.title
driver.execute_script(open("./nativeJS.js").read())
driver.close()
