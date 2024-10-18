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
            page.wait_for_load_state('networkidle')
            time.sleep(3) 
            clear_storage(page)

            try:
                page.locator("#prod-ship-to-store > div > div:nth-child(1) > ul > li:nth-child(3) > button").click(timeout=60000)
                random_delay()
                random_mouse_movement(page)
            except Exception as e:
                print(f"Error clicking shipping button: {e}")
            
            # Handle shipping dropdown
            try:
                shipping_dropdown = page.locator("li").filter(has_text="ShippingArrives").locator("#select-dropdown")
                shipping_dropdown.select_option("4", timeout=60000)
                random_delay()
                random_mouse_movement(page)
            except Exception as e:
                print(f"Error selecting shipping option: {e}")
            
            # Click "Add to Cart" button for shipping
            try:
                page.wait_for_selector('#receiveing-addToCartbtn > strong', timeout=60000)
                page.locator('#receiveing-addToCartbtn > strong').nth(1).click(timeout=60000)
                random_delay()
                random_mouse_movement(page)
                print('done')
            except Exception as e:
                print(f"Error clicking 'Add to Cart' button: {e}")

            #https://www.walgreens.com/cart/view-ui
            #https://www.walgreens.com/register/regpersonalinfo?ru=%2Fcart
            try:
                page.goto("https://www.walgreens.com/register/regpersonalinfo?ru=%2Fcart")
                page.get_by_placeholder("First name").click()
                page.get_by_placeholder("First name").fill("Oscar")
                page.get_by_placeholder("Last name").click()
                page.get_by_placeholder("Last name").fill("Li")
                page.get_by_label("*Email").click()
                page.get_by_label("*Email").fill("gg@gamil.com")
                page.get_by_label("*Password").click()
                page.get_by_label("*Password").fill("Hiapsdf123!")
                page.get_by_label("I read and agree to").check()
                page.get_by_role("button", name="Continue").click()

            except Exception as e:
                print(f"Error Creating Account: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            time.sleep(2000000000) 
            browser.close()
            print("Automation has finished.")
