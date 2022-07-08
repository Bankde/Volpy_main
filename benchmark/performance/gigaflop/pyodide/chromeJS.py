from selenium import webdriver

driver = webdriver.Chrome()
assert "Python" in driver.title
driver.get("pyodide.html");
driver.close()
