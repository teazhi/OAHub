import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os
from backend.automation_main import start_automation
from backend.utils import read_json, validate_url, display_error
import concurrent.futures

def load_stores_config():
    json_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'stores.json')
    return read_json(json_path)

def launch_gui():
    global form_frame, action_button, root, select_store_var, promotion_dropdown, stores, promotion_var, order_amt_dropdown, run_amt_var, error_label, item_link_var, order_amt_var
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("OAHub")

    window_width = 800
    window_height = 600
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_x = int((screen_width / 2) - (window_width / 2))
    position_y = int((screen_height / 2) - (window_height / 2))
    root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
    root.resizable(False, False)

    # Set weights for centering
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(2, weight=1)

    # OAHub Logo at the Top (Increased Size)
    top_title_label = ctk.CTkLabel(root, text="OAHub", font=("Roboto", 40, "bold"))
    top_title_label.grid(row=0, column=0, columnspan=2, pady=(40, 20), sticky="n")

    form_frame = ctk.CTkFrame(root)
    form_frame.grid(row=1, column=0, columnspan=2, pady=20, padx=20, sticky="n")

    stores = load_stores_config()

    # Error Label
    error_label = ctk.CTkLabel(root, text="", fg_color="red", font=("Roboto", 10))
    error_label.grid(row=5, column=0, columnspan=2, pady=10)

    # Store Dropdown
    select_store_label = ctk.CTkLabel(form_frame, text="Select store:", font=("Roboto", 14))
    select_store_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

    select_store_var = ctk.StringVar(value="Select store...")
    select_store_dropdown = ctk.CTkComboBox(form_frame, variable=select_store_var, values=list(stores.keys()), width=300)
    select_store_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky="w")

    select_store_dropdown.configure(command=lambda _: update_selection(select_store_var.get()))

    # Item Link Entry
    item_link_label = ctk.CTkLabel(form_frame, text="Item Link:", font=("Roboto", 14))
    item_link_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

    item_link_var = ctk.StringVar()
    item_link_entry = ctk.CTkEntry(form_frame, textvariable=item_link_var, width=300)
    item_link_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

    # Promotion Dropdown
    promotion_label = ctk.CTkLabel(form_frame, text="Promotion:", font=("Roboto", 14))
    promotion_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")

    promotion_var = ctk.StringVar(value="Select promotion...")
    promotion_dropdown = ctk.CTkComboBox(form_frame, variable=promotion_var, values=[""], width=300)
    promotion_dropdown.grid(row=2, column=1, padx=10, pady=10, sticky="w")

    # Order Amount Dropdown
    order_amt_label = ctk.CTkLabel(form_frame, text="Order amount:", font=("Roboto", 14))
    order_amt_label.grid(row=3, column=0, padx=10, pady=10, sticky="e")

    order_amt_var = ctk.StringVar(value="Select order amount...")
    order_amt_dropdown = ctk.CTkComboBox(form_frame, variable=order_amt_var, values=[""], width=300)
    order_amt_dropdown.grid(row=3, column=1, padx=10, pady=10, sticky="w")

    # Times to Run Dropdown
    run_amt_label = ctk.CTkLabel(form_frame, text="Times to run:", font=("Roboto", 14))
    run_amt_label.grid(row=4, column=0, padx=10, pady=10, sticky="e")

    run_amt_var = ctk.StringVar(value="Select number of times to run")
    run_amt_dropdown = ctk.CTkComboBox(form_frame, variable=run_amt_var, values=[str(i) for i in range(1, 11)], width=300)
    run_amt_dropdown.grid(row=4, column=1, padx=10, pady=10, sticky="w")

    # Start Button
    action_button = ctk.CTkButton(root, text="START", font=("Roboto", 12, "bold"), width=200, height=50, command=start_action)
    action_button.grid(row=2, column=0, pady=30, sticky="n")

    root.mainloop()

def update_selection(selected_store):
    global stores, promotion_var, promotion_dropdown, order_amt_dropdown, order_amt_var

    if selected_store in stores:
        promotions = stores[selected_store].get("promotions", [])
        if promotions:
            promotion_dropdown.configure(values=promotions)
            promotion_var.set(promotions[0])
        else:
            promotion_dropdown.configure(values=["Select promotion..."])
            promotion_var.set("Select promotion...")

        max_order_qty = stores[selected_store].get("max_order_qty", 1)
        order_qty_values = [str(i) for i in range(1, int(max_order_qty) + 1)]
        if order_qty_values:
            order_amt_dropdown.configure(values=order_qty_values)
            order_amt_var.set(order_qty_values[0])
        else:
            order_amt_dropdown.configure(values=["Select order amount..."])
            order_amt_var.set("Select order amount...")

def start_action():
    global stores, error_label, order_amt_var
    selected_store = select_store_var.get()
    item_link = item_link_var.get()
    promotion_code = promotion_var.get()
    order_amount = order_amt_var.get()
    run_amount = run_amt_var.get()

    if selected_store in stores:
        base_url = stores[selected_store]["base_url"]
        if not validate_url(base_url, item_link):
            display_error(error_label, f"Error: The item link must start with {base_url}")
            return

    action_button.configure(text="WORKING", state="disabled")

    def reset_button():
        action_button.configure(text="START", state="normal")

    def run_automation():
        future = executor.submit(start_automation, selected_store, item_link, promotion_code, order_amount, run_amount)
        root.after(100, check_future, future)

    def check_future(future):
        if future.done():
            reset_button()
        else:
            root.after(100, check_future, future)

    run_automation()

executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
