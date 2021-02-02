from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time


driver = webdriver.Chrome()
driver.get("http://localhost:5000")
assert "Flask-Scaffold" in driver.title
email = driver.find_element_by_id("email")
email.clear()
email.send_keys("leo@leog.in")
password = driver.find_element_by_id("password")
password.clear()
password.send_keys("54321")
login_button = driver.find_element_by_name("login")
actions = ActionChains(driver)
actions.click(login_button)
heading = driver.find_element_by_tag_name('h2')
assert "Dashboard Statistics Overview" in heading.text
time.sleep(5)

driver.close()