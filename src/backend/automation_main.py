from backend.automation.iherb_automation import automate_iherb
from backend.automation.swanson_automation import automate_swanson
from backend.automation.walgreens_automation import automate_walgreens
from backend.automation.petco_automation import automate_petco

def start_automation(selected_store, item_link, promotion_code, order_amount, run_amount):
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
        'Walgreens': automate_walgreens,
        "Petco": automate_petco,
    }

    automation_func = automation_functions[selected_store]
    
    try:
        automation_func(item_link, promotion_code, order_amount, run_amount)
    finally:
        # Ensure everything is properly closed before returning
        print(f"Automation for {selected_store} completed")
