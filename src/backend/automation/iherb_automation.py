import time
from selenium import webdriver
from selenium.webdriver.common.by import By

def automate_iherb(item_link, promotion_code, order_amount, run_amount):
    driver = webdriver.Chrome()
    driver.get(item_link)

    # Start automation
    product_element = driver.find_element(By.CLASS_NAME, "product-title")
    print("Product Found:", product_element.text)

    driver.quit()