import time
from playwright.sync_api import sync_playwright
from ..utils import create_driver, random_delay, random_mouse_movement
import random

def automate_swanson(item_link, promotion_code, order_amount, run_amount):
    with sync_playwright() as p:
        browser, context, page = create_driver(p)

        try:
            page.goto(item_link)
            page.wait_for_load_state('networkidle')

            try:
                random_mouse_movement(page)
                random_delay()
                try:
                    page.locator('[aria-label="Close dialog"]').click()
                except:
                    print("broken")
                print("found")
                random_delay()
                random_mouse_movement(page)
                page.get_by_test_id("addToCartForm").get_by_test_id("SelectBox").select_option("more")
                random_delay()
                page.get_by_label("Quantity").fill(order_amount)
                random_delay()
                random_mouse_movement(page)
                page.get_by_test_id("addToCartButton").click()
                random_delay()
                random_mouse_movement(page)
                page.get_by_role("button", name="Close", exact=True).click()
                random_delay()
                random_mouse_movement(page)
                page.get_by_test_id("menu-cart-anchor").click()
                random_delay()
                random_mouse_movement(page)
                page.get_by_text("Promotion code", exact=True).click()
                page.get_by_label("Promotion code").fill("TEST15")
                random_delay()
                random_mouse_movement(page)
                page.get_by_label("Promotion code").press("ControlOrMeta+a")
                random_delay()
                random_delay()
                page.get_by_label("Promotion code").fill(promotion_code)
                random_delay()
                random_mouse_movement(page)
                page.get_by_label("Promotion code").press("Enter")
                random_delay()
                random_delay()
                random_delay()
                random_delay()
                random_mouse_movement(page)
                page.get_by_role("link", name="Proceed to Checkout").click()
                print("made to checkout")
                time.sleep(180)
            except Exception as e:
                print(f"Error during the subscription process: {e}")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            time.sleep(2)
            browser.close()
            print("Automation has finished.")