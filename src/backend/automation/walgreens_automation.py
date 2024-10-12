import time
from playwright.sync_api import sync_playwright
from ..utils import create_driver, random_delay, random_mouse_movement

def clear_storage(page):
    try:
        page.evaluate("localStorage.clear()")
    except Exception as e:
        print(f"Error clearing localStorage: {e}")

def automate_walgreens(item_link, promotion_code, order_amount, run_amount):
    with sync_playwright() as p:
        browser, context, page = create_driver(p)

        try:
            page.goto(item_link)
            time.sleep(3)
            page.wait_for_load_state('networkidle')
            clear_storage(page)
            page.locator("#prod-ship-to-store > div > div:nth-child(1) > ul > li:nth-child(3) > button").click()
            random_delay()
            random_mouse_movement(page)
            shipping_dropdown = page.locator("li").filter(has_text="ShippingArrives").locator("#select-dropdown")
            shipping_dropdown.select_option("4")
            random_delay()
            random_mouse_movement(page)
            page.locator("#receiveing-addToCartbtn > strong").click()
            random_delay()
            random_mouse_movement(page)
            print('done')
            # page.locator("#addToCart-cart-checkout > span").click()
            # random_delay()
            # random_mouse_movement(page)
            # page.locator("#wag-cart-proceed-to-checkout").click()
            # random_delay()
            # random_mouse_movement(page)
            # page.locator("#wag-checkout-review-terms-submit-top > div.wag-checkout-continue-btn > a > span").click()
            # random_delay()
            # random_mouse_movement(page)
            
            # page.locator("li").filter(has_text="Shi1ppingArrives in 2-4 days.").get_by_label("Select item quantity in the").select_option("10")
            # random_mouse_movement
            # random_delay()
            # random_mouse_movement(page)
            # page.get_by_label("Add to cart for shipping.").click()
            # random_delay()
            # random_mouse_movement(page)
            # page.get_by_role("link", name="View cart").click()
            # random_delay()
            # random_mouse_movement(page)
            # random_mouse_movement(page)
            # page.get_by_role("button", name="Proceed to Checkout").click()
            # random_delay()
            # random_mouse_movement(page)
            # page.get_by_label("Email").click()
            # random_mouse_movement(page)
            # random_delay()
            # page.get_by_label("Email").fill("oscafjk")
            # random_mouse_movement(page)
            # random_delay()
            # page.get_by_label("Email").press("Tab")
            # random_mouse_movement(page)
            # random_delay()
            # page.get_by_test_id("password").fill("asdfjadfno")
            # random_mouse_movement(page)
            # random_delay()
            #page.get_by_label("Sign in").click()

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            time.sleep(2000000000)
            browser.close()
            print("Automation has finished.")
