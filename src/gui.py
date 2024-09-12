import tkinter as tk
from tkinter import ttk
import os
from backend.automation_main import start_automation
from backend.utils import read_json, validate_url, apply_hover_effect, display_error, configure_grid
import concurrent.futures

def load_stores_config():
    json_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'stores.json')
    return read_json(json_path)

def launch_gui():
    root = tk.Tk()
    root.title("OAHub")
    
    root.geometry("800x600")
    root.resizable(False, False)

    root.config(bg="#2C3E50")

    title_label = tk.Label(root, text="OAHub", font=("Roboto", 30, "bold"), bg="#2C3E50", fg="#FFD700")
    title_label.grid(row=0, column=0, columnspan=2, pady=(30, 20), sticky="n")

    form_frame = tk.Frame(root, bg="#2C3E50")
    form_frame.grid(row=1, column=0, columnspan=2, pady=10)

    # Error label to display validation errors (initially hidden)
    error_label = tk.Label(root, text="", fg="red", bg="#2C3E50", font=("Roboto", 10))
    error_label.grid(row=5, column=0, columnspan=2, pady=10)

    # Load promotions and base URLs from the JSON file
    stores = load_stores_config()

    # Select store
    select_store_label = tk.Label(form_frame, text="Select store:", bg="#2C3E50", fg="white", font=("Roboto", 12))
    select_store_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

    select_store_var = tk.StringVar()
    select_store_dropdown = ttk.Combobox(form_frame, textvariable=select_store_var, state="readonly", width=25)
    select_store_dropdown['values'] = list(stores.keys())  # Use the keys from the promotions JSON
    select_store_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky="w")

    # Item link
    item_link_label = tk.Label(form_frame, text="Item Link", bg="#2C3E50", fg="white", font=("Roboto", 12))
    item_link_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

    item_link_var = tk.StringVar()
    item_link_entry = tk.Entry(form_frame, textvariable=item_link_var, width=28)
    item_link_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

    # Promotion
    promotion_label = tk.Label(form_frame, text="Promotion:", bg="#2C3E50", fg="white", font=("Roboto", 12))
    promotion_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")

    promotion_var = tk.StringVar()
    promotion_dropdown = ttk.Combobox(form_frame, textvariable=promotion_var, state="readonly", width=25)
    promotion_dropdown.grid(row=2, column=1, padx=10, pady=10, sticky="w")

    # Order amount
    order_amt_label = tk.Label(form_frame, text="Order amount:", bg="#2C3E50", fg="white", font=("Roboto", 12))
    order_amt_label.grid(row=3, column=0, padx=10, pady=10, sticky="e")

    order_amt_var = tk.StringVar()
    order_amt_dropdown = ttk.Combobox(form_frame, textvariable=order_amt_var, state="readonly", width=25)
    order_amt_dropdown.grid(row=3, column=1, padx=10, pady=10, sticky="w")

    # Number of times to run
    run_amt_label = tk.Label(form_frame, text="Times to run:", bg="#2C3E50", fg="white", font=("Roboto", 12))
    run_amt_label.grid(row=4, column=0, padx=10, pady=10, sticky="e")

    run_amt_var = tk.StringVar()
    run_amt_dropdown = ttk.Combobox(form_frame, textvariable=run_amt_var, state="readonly", width=25)
    run_amt_dropdown['values'] = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10")
    run_amt_dropdown.grid(row=4, column=1, padx=10, pady=10, sticky="w")

    def update_selection(event):
        selected_store = select_store_var.get()

        # Update promotions
        if selected_store in stores:
            promotion_dropdown['values'] = stores[selected_store]["promotions"]
            promotion_var.set('')

        # Update order amount
        if selected_store in stores:
            order_amt_dropdown['values'] = [str(i) for i in range(1, int(stores[selected_store]["max_order_qty"]) + 1)]
            order_amt_var.set('')

    # Bind the select_store_dropdown to update promotions and order amt when a store is selected
    select_store_dropdown.bind("<<ComboboxSelected>>", update_selection)

    # concurrency
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    def start_action():
        # Clear any previous error message
        error_label.config(text="")

        selected_store = select_store_var.get()
        item_link = item_link_var.get()
        promotion_code = promotion_var.get()
        order_amount = order_amt_var.get()
        run_amount = run_amt_var.get()

        # Validate the item link
        if selected_store in stores:
            base_url = stores[selected_store]["base_url"]
            if not validate_url(base_url, item_link):
                display_error(error_label, f"Error: The item link must start with {base_url}")
                return

        action_button.config(text="WORKING", state="disabled")

        def reset_button():
            action_button.config(text="START", state="normal")

        # Run automation in a background thread
        def run_automation():
            future = executor.submit(start_automation, selected_store, item_link, promotion_code, order_amount, run_amount)
            root.after(100, check_future, future)

        def check_future(future):
            if future.done():
                reset_button()
            else:
                root.after(100, check_future, future)  # Poll every 100ms if thread is still running

        run_automation()  # Run the automation in a background thread

    # Submit button
    action_button = tk.Button(root, text="START", font=("Roboto", 12, "bold"), bg="#FFD700", fg="#2C3E50", bd=0, padx=20, pady=10, relief="flat", highlightthickness=0, command=start_action)
    
    apply_hover_effect(action_button, hover_bg="#E0B800", hover_fg="#2C3E50", normal_bg="#FFD700", normal_fg="#2C3E50")

    action_button.grid(row=3, column=0, columnspan=2, pady=30)

    # responsive grid layout
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(3, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

    form_frame.grid_columnconfigure(0, weight=1)
    form_frame.grid_columnconfigure(1, weight=1)

    root.mainloop()
