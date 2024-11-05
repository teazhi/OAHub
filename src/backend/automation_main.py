from backend.automation.iherb_automation import automate_iherb
from backend.automation.swanson_automation import automate_swanson
from threading import Thread

def start_automation(button, selected_store, item_link, promotion_code, order_amount, run_amount):
    button.configure(text="Working", state="disabled")
    Thread(target=lambda: button.configure(text="Start", state="normal")).start()

    automation_details = {
        "Item Link": item_link, 
        "Promo Code": promotion_code, 
        "Order Amount": order_amount, 
        "Run Amount": run_amount
    }

    print(f"Starting purchase on {selected_store} with: {automation_details}")

    automation_functions = {
        "iHerb": automate_iherb,
        "Swanson": automate_swanson,
    }

    automation_func = automation_functions[selected_store]
    
    try:
        automation_func(item_link, promotion_code, order_amount, run_amount)
    finally:
        # Ensure everything is properly closed before returning
        print(f"Automation for {selected_store} completed")
