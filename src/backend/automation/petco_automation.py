import time
from playwright.sync_api import sync_playwright
from ..utils import create_driver, random_delay, random_mouse_movement

def clear_storage(page):
    try:
        page.evaluate("localStorage.clear()")
    except Exception as e:
        print(f"Error clearing localStorage: {e}")

def automate_petco(item_link, promotion_code, order_amount, run_amount):
    with sync_playwright() as p:
        browser, context, page = create_driver(p)

        try:
            page.goto(item_link)

            page.wait_for_load_state('networkidle')

            clear_storage(page)

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            time.sleep(30000)
            #browser.close()
            print("Automation has finished.")
