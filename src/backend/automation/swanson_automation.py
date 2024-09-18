import time
from playwright.sync_api import sync_playwright
from ..utils import create_driver, random_delay, random_mouse_movement

def automate_swanson(item_link, promotion_code, order_amount, run_amount):
    with sync_playwright() as p:
        browser, context, page = create_driver(p)

        try:
            page.goto(item_link)
            page.wait_for_load_state('networkidle')

            try:
                random_mouse_movement()
                random_delay()
                page.wait_for_selector("xpath=/html/body/div[8]/div/div[2]/div/div/div/div/div/button")
                print("found")
                page.locator("xpath=/html/body/div[8]/div/div[2]/div/div/div/div/div/button").click()
                random_delay()
                random_mouse_movement()
                page.locator("#quantity").click()
                random_delay()
                page.select_option("id=quantity", value=order_amount)
                random_delay()
                random_mouse_movement()
                page.locator("xpath=/html/body/div[1]/div/section/section/section/section/section[1]/section/div[4]/section/div/button").click()
                time.sleep(180)

                print("Added product to cart and confirmed.")
            except Exception as e:
                print(f"Error during the subscription process: {e}")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            time.sleep(2)
            browser.close()
            print("Automation has finished.")