import time
from playwright.sync_api import sync_playwright
from ..utils import create_driver, random_delay, random_mouse_movement

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

            page.wait_for_load_state('networkidle')

            clear_storage(page)

            try:
                page.wait_for_selector("xpath=/html/body/div[1]/div[1]/div[7]/div/div[5]/div[1]/div/div[2]/div/div[2]/div[1]/a", state="visible")

                # product_id = "23897"  # Example product ID, ensure this is dynamic if needed
                # subscribe_url = f"https://checkout.iherb.com/api/SimpleSubscribe/Bundles?productId={product_id}&quantity={order_amount}"
                # print(subscribe_url)

                # # Send the GET request
                # response = page.request.get(subscribe_url)

                # # Check the response
                # if response.status == 200:
                #     print("Subscription request succeeded.")
                # else:
                #     print(f"Subscription request failed. Status: {response.status}, Response: {response.text()}")

                plusbtn = page.locator("#one-time-purchase-tab > div.css-4baix3 > div > div.css-h1cems-OneTimePurchase > div > div > button.css-145a39a")
                plusbtn.click()
                print("clicked")
                for _ in range(int(order_amount)-2):
                    plusbtn.nth(1).click()
                    print("clicked")
                
                time.sleep(10)
                page.click("#pdp-addToCart")
                print("atc clicked")
                random_delay()
                page.goto("https://checkout.iherb.com/cart")

                time.sleep(60)

                print("Added product to cart and confirmed.")
            except Exception as e:
                print(f"Error during the subscription process: {e}")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            time.sleep(2)
            browser.close()
            print("Automation has finished.")
