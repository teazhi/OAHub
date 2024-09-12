import time
from playwright.sync_api import sync_playwright
from ..utils import create_driver, random_delay

def clear_storage(page):
    try:
        page.evaluate("localStorage.clear()")
    except Exception as e:
        print(f"Error clearing localStorage: {e}")

def automate_iherb(item_link, promotion_code, order_amount, run_amount):
    with sync_playwright() as p:
        browser, context, page = create_driver(p)

        try:
            page.goto(item_link)
            clear_storage(page)

            try:
                page.wait_for_selector("xpath=/html/body/div[1]/div[1]/div[7]/div/div[5]/div[1]/div/div[2]/div/div[2]/div[1]/a", state="visible")
                page.locator("xpath=/html/body/div[1]/div[1]/div[7]/div/div[5]/div[1]/div/div[2]/div/div[2]/div[1]/a").click()
                print("Subscription option found and clicked.")

                random_delay()

                add_qty_btn = page.locator("xpath=/html/body/div[1]/div[1]/div[7]/div/div[5]/div[1]/div/div[2]/div/div[2]/div[2]/div[5]/div/div/button[2]")
                
                for _ in range(int(order_amount)-1):
                    add_qty_btn.click()
                    random_delay()

                page.click("#pdp-addToCart")
                print("sub clicked")
                # page.click('#btn-add-to-cart > div > button')
                random_delay()
                page.click('div[role="button"]:has-text("Continue")') 

                print("Added product to cart and confirmed.")
            except Exception as e:
                print(f"Error during the subscription process: {e}")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            time.sleep(2)
            browser.close()
            print("Automation has finished.")
