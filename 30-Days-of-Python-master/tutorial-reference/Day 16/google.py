import time
from selenium import webdriver

browser = webdriver.Chrome() # Firefox()

url = 'https://google.com'
browser.get(url)

"""
<input type='text' class='' id='' name='??' />
<textarea name='??'><textarea>
<input name="q" type="text">
"""
time.sleep(2)
name = 'q'
search_el = browser.find_element_by_name("q")
# print(search_el)
# search_el = browser.find_elements_by_css_selector("h1")
search_el.send_keys("selenium python")

"""
<input type='submit' />
<button type='submit' />
<form></form>

<input type="submit">
"""
submit_btn_el = browser.find_element_by_css_selector("input[type='submit']")
print(submit_btn_el.get_attribute('name'))
time.sleep(2)
submit_btn_el.click()