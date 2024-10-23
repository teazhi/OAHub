import os
import sys
import customtkinter as ctk
from threading import Thread
import io
import contextlib
import concurrent.futures
import json
from wsmain import search_skus_from_file
import re
from backend.utils import read_json, validate_url, display_error
from backend.automation_main import start_automation


class DualOutput:
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')

    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.console = sys.stdout
        self.text_widget.tag_config("info", foreground="cyan")
        self.text_widget.tag_config("warning", foreground="yellow")
        self.text_widget.tag_config("error", foreground="red")
        self.text_widget.tag_config("default", foreground="lightgrey")

    def write(self, message):
        stripped_message = self.ansi_escape.sub('', message)
        if "[INFO]" in stripped_message:
            tag = "info"
            tag_text = "[INFO]"
            message_text = stripped_message.replace("[INFO]", "")
        elif "[WARNING]" in stripped_message:
            tag = "warning"
            tag_text = "[WARNING]"
            message_text = stripped_message.replace("[WARNING]", "")
        elif "[ERROR]" in stripped_message:
            tag = "error"
            tag_text = "[ERROR]"
            message_text = stripped_message.replace("[ERROR]", "")
        else:
            tag = "default"
            tag_text = ""
            message_text = stripped_message

        if tag_text:
            self.text_widget.insert(ctk.END, tag_text, tag)
        self.text_widget.insert(ctk.END, message_text, "default")
        self.text_widget.see(ctk.END)
        self.console.write(message)

    def flush(self):
        self.console.flush()

def run_main_file(output_widget):
    dual_output = DualOutput(output_widget)
    sys.stdout = dual_output

    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        sku_file_path = os.path.join(base_dir, 'skus.txt')
        proxies_file_path = os.path.join(base_dir, '..', 'config', 'proxies.txt')
        search_skus_from_file(sku_file_path, proxies_file_path)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sys.stdout = sys.__stdout__

def load_stores_config():
    json_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'stores.json')
    return read_json(json_path)

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
            error_label.configure(text=f"Error: The item link must start with {base_url}")
            return

    action_button.configure(text="WORKING", state="disabled")
    error_label.configure(text="")

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

    top_title_label = ctk.CTkLabel(root, text="OAHub", font=("Roboto", 40, "bold"))
    top_title_label.pack(pady=(30, 20))

    tab_view = ctk.CTkTabview(root, width=800, height=500)
    tab_view.pack(expand=True, fill="both")

    home_tab = tab_view.add("Home")

    home_tab.grid_columnconfigure(0, weight=1)
    home_tab.grid_rowconfigure(0, weight=1)

    form_frame = ctk.CTkFrame(home_tab)
    form_frame.grid(row=0, column=0, pady=20, padx=20, sticky="n")

    stores = load_stores_config()

    select_store_label = ctk.CTkLabel(form_frame, text="Select store:", font=("Roboto", 14))
    select_store_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

    select_store_var = ctk.StringVar(value="Select store...")
    select_store_dropdown = ctk.CTkComboBox(form_frame, variable=select_store_var, values=list(stores.keys()), width=300)
    select_store_dropdown.grid(row=1, column=1, padx=10, pady=10, sticky="w")
    
    select_store_dropdown.configure(command=lambda _: update_selection(select_store_var.get()))

    item_link_label = ctk.CTkLabel(form_frame, text="Item Link:", font=("Roboto", 14))
    item_link_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")

    item_link_var = ctk.StringVar()
    item_link_entry = ctk.CTkEntry(form_frame, textvariable=item_link_var, width=300)
    item_link_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

    promotion_label = ctk.CTkLabel(form_frame, text="Promotion:", font=("Roboto", 14))
    promotion_label.grid(row=3, column=0, padx=10, pady=10, sticky="e")

    promotion_var = ctk.StringVar(value="Select promotion...")
    promotion_dropdown = ctk.CTkComboBox(form_frame, variable=promotion_var, values=[""], width=300)
    promotion_dropdown.grid(row=3, column=1, padx=10, pady=10, sticky="w")

    order_amt_label = ctk.CTkLabel(form_frame, text="Order amount:", font=("Roboto", 14))
    order_amt_label.grid(row=4, column=0, padx=10, pady=10, sticky="e")

    order_amt_var = ctk.StringVar(value="Select order amount...")
    order_amt_dropdown = ctk.CTkComboBox(form_frame, variable=order_amt_var, values=[""], width=300)
    order_amt_dropdown.grid(row=4, column=1, padx=10, pady=10, sticky="w")

    run_amt_label = ctk.CTkLabel(form_frame, text="Times to run:", font=("Roboto", 14))
    run_amt_label.grid(row=5, column=0, padx=10, pady=10, sticky="e")

    run_amt_var = ctk.StringVar(value="Select number of times to run")
    run_amt_dropdown = ctk.CTkComboBox(form_frame, variable=run_amt_var, values=[str(i) for i in range(1, 11)], width=300)
    run_amt_dropdown.grid(row=5, column=1, padx=10, pady=10, sticky="w")

    action_button = ctk.CTkButton(form_frame, text="Start", font=("Roboto", 12, "bold"), width=200, height=50, command=start_action)
    action_button.grid(row=6, column=0, columnspan=2, pady=20, sticky="n")

    error_label = ctk.CTkLabel(form_frame, text="", text_color="red", font=("Roboto", 10))
    error_label.grid(row=7, column=0, columnspan=2, pady=(10, 10), sticky="n")  # Positioned below the Start button

    wholesale_tab = tab_view.add("Wholesale")

    wholesale_tab.grid_columnconfigure(0, weight=1)
    wholesale_tab.grid_rowconfigure(0, weight=1)

    output_text = ctk.CTkTextbox(wholesale_tab, width=700, height=400)
    output_text.grid(row=0, column=0, padx=10, pady=10, sticky="n")

    wholesale_button = ctk.CTkButton(wholesale_tab, text="Start", font=("Roboto", 12, "bold"),
                                     command=lambda: Thread(target=run_main_file, args=(output_text,)).start())
    wholesale_button.grid(row=1, column=0, pady=20, sticky="n")

    root.mainloop()


