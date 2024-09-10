import time
from selenium import webdriver
from selenium.webdriver.common.by import By

def automate_swanson(item_link, promotion_code, order_amount, run_amount):
    driver = webdriver.Chrome()
    driver.quit()