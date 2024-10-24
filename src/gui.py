import os
import sys
import customtkinter as ctk
from threading import Thread
import io
import contextlib
import concurrent.futures
import json
import threading
from tkinter import filedialog, messagebox
from wholesale import search_skus_from_file
import re
from backend.utils import read_json, validate_url, display_error
from backend.automation_main import start_automation
import shutil

class DualOutput:
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')

    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.console = sys.stdout
        self.text_widget.tag_config("info", foreground="cyan")
        self.text_widget.tag_config("success", foreground="green")
        self.text_widget.tag_config("warning", foreground="yellow")
        self.text_widget.tag_config("error", foreground="red")
        self.text_widget.tag_config("503", foreground="red")
        self.text_widget.tag_config("default", foreground="lightgrey")

    def write(self, message):
        stripped_message = self.ansi_escape.sub('', message)
        self.text_widget.configure(state="normal")
        if "[INFO]" in stripped_message:
            tag = "info"
            tag_text = "[INFO]"
            message_text = stripped_message.replace("[INFO]", "")
        elif "[SUCCESS]" in stripped_message:
            tag = "success"
            tag_text = "[SUCCESS]"
            message_text = stripped_message.replace("[SUCCESS]", "")
        elif "[WARNING]" in stripped_message:
            tag = "warning"
            tag_text = "[WARNING]"
            message_text = stripped_message.replace("[WARNING]", "")
        elif "[ERROR]" in stripped_message:
            tag = "error"
            tag_text = "[ERROR]"
            message_text = stripped_message.replace("[ERROR]", "")
        elif "[503]" in stripped_message:
            tag = "503"
            tag_text = "[503]"
            message_text = stripped_message.replace("[503]", "")
        else:
            tag = "default"
            tag_text = ""
            message_text = stripped_message

        if tag_text:
            self.text_widget.insert(ctk.END, tag_text, tag)
        self.text_widget.insert(ctk.END, message_text, "default")
        self.text_widget.see(ctk.END)
        self.text_widget.configure(state="disabled")
        self.console.write(message)

    def flush(self):
        self.console.flush()

def run_main_file(output_widget, sku_file_path, wholesale_button):
    dual_output = DualOutput(output_widget)
    sys.stdout = dual_output

    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        proxies_file_path = os.path.join(base_dir, '..', 'config', 'proxies.txt')
        search_skus_from_file(sku_file_path, proxies_file_path)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sys.stdout = sys.__stdout__
        wholesale_button.configure(text="Start", state="normal")

def select_skus_file(output_textbox, selected_file_var):
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        selected_file_var.set(file_path)
        output_textbox.configure(state="normal")
        output_textbox.insert(ctk.END, f"Selected SKU file: {file_path}\n")
        output_textbox.configure(state="disabled")
    else:
        output_textbox.configure(state="normal")
        output_textbox.insert(ctk.END, "No file selected.\n")
        output_textbox.configure(state="disabled")

def download_amazon_links_file(output_widget):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    oldskus_dir = os.path.join(base_dir, "oldskus")
    
    try:
        latest_file = max([f for f in os.listdir(oldskus_dir) if f.startswith("amazon_links_from_skus")], key=lambda f: os.path.getmtime(os.path.join(oldskus_dir, f)))
        latest_file_path = os.path.join(oldskus_dir, latest_file)
        download_dir = filedialog.askdirectory(title="Select Download Folder")
        
        if download_dir:
            shutil.copy(latest_file_path, os.path.join(download_dir, latest_file))
            messagebox.showinfo("Download Complete", f"Latest file {latest_file} has been downloaded successfully.")
    except ValueError:
        messagebox.showerror("Error", "No amazon_links_from_skus file found.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def start_automation_file(output_widget, selected_file_var, wholesale_button):
    skus_file_path = selected_file_var.get()
    if skus_file_path:
        wholesale_button.configure(text="WORKING", state="disabled") 
        Thread(target=run_main_file, args=(output_widget, skus_file_path, wholesale_button)).start()

def load_stores_config():
    json_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'stores.json')
    return read_json(json_path)

def start_home_automation(button):
    button.configure(text="Working", state="disabled")
    threading.Timer(2, lambda: button.configure(text="Start", state="normal")).start()

def launch_gui():
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

    title_frame = ctk.CTkFrame(root)
    title_frame.pack(pady=20)

    top_title_label = ctk.CTkLabel(title_frame, text="OAHub", font=("Roboto", 40, "bold"))
    top_title_label.pack()

    tab_view = ctk.CTkTabview(root, width=750, height=500)
    tab_view.pack(expand=True)

    home_tab = tab_view.add("Home")
    home_tab.grid_columnconfigure(0, weight=1)

    form_frame = ctk.CTkFrame(home_tab)
    form_frame.grid(row=1, column=0, pady=20, padx=20, sticky="n")

    select_store_label = ctk.CTkLabel(form_frame, text="Select store:", font=("Roboto", 14))
    select_store_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

    select_store_var = ctk.StringVar(value="Select store...")
    select_store_dropdown = ctk.CTkComboBox(form_frame, variable=select_store_var, values=["Swanson", "iHerb"], width=300)
    select_store_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky="w")

    item_link_label = ctk.CTkLabel(form_frame, text="Item Link:", font=("Roboto", 14))
    item_link_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

    item_link_var = ctk.StringVar()
    item_link_entry = ctk.CTkEntry(form_frame, textvariable=item_link_var, width=300)
    item_link_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

    promotion_label = ctk.CTkLabel(form_frame, text="Promotion:", font=("Roboto", 14))
    promotion_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")

    promotion_var = ctk.StringVar(value="Select promotion...")
    promotion_dropdown = ctk.CTkComboBox(form_frame, variable=promotion_var, values=[""], width=300)
    promotion_dropdown.grid(row=2, column=1, padx=10, pady=10, sticky="w")

    order_amt_label = ctk.CTkLabel(form_frame, text="Order amount:", font=("Roboto", 14))
    order_amt_label.grid(row=3, column=0, padx=10, pady=10, sticky="e")

    order_amt_var = ctk.StringVar(value="Select order amount...")
    order_amt_dropdown = ctk.CTkComboBox(form_frame, variable=order_amt_var, values=[""], width=300)
    order_amt_dropdown.grid(row=3, column=1, padx=10, pady=10, sticky="w")

    run_amt_label = ctk.CTkLabel(form_frame, text="Times to run:", font=("Roboto", 14))
    run_amt_label.grid(row=4, column=0, padx=10, pady=10, sticky="e")

    run_amt_var = ctk.StringVar(value="Select number of times to run")
    run_amt_dropdown = ctk.CTkComboBox(form_frame, variable=run_amt_var, values=[str(i) for i in range(1, 11)], width=300)
    run_amt_dropdown.grid(row=4, column=1, padx=10, pady=10, sticky="w")

    action_button = ctk.CTkButton(home_tab, text="Start", command=lambda: start_home_automation(action_button), width=200, height=50, font=("Roboto", 12, "bold"))
    action_button.grid(row=2, column=0, pady=20)

    error_label = ctk.CTkLabel(home_tab, text="", font=("Roboto", 12), text_color="red")
    error_label.grid(row=3, column=0, pady=5)

    wholesale_tab = tab_view.add("Wholesale")
    wholesale_tab.grid_columnconfigure(0, weight=1)

    wholesale_left_frame = ctk.CTkFrame(wholesale_tab)
    wholesale_left_frame.grid(row=0, column=0, pady=20, padx=10)

    output_textbox = ctk.CTkTextbox(wholesale_left_frame, width=450, height=250, wrap="word", state="disabled")
    output_textbox.pack(pady=10)

    wholesale_button = ctk.CTkButton(wholesale_left_frame, text="Start", command=lambda: start_automation_file(output_textbox, selected_file_var, wholesale_button), width=200, height=50)
    wholesale_button.pack(pady=20)

    wholesale_right_frame = ctk.CTkFrame(wholesale_tab)
    wholesale_right_frame.grid(row=0, column=1, pady=20, padx=10)

    selected_file_var = ctk.StringVar()

    file_button = ctk.CTkButton(wholesale_right_frame, text="Select SKU File", command=lambda: select_skus_file(output_textbox, selected_file_var))
    file_button.pack(pady=10)

    download_button = ctk.CTkButton(wholesale_right_frame, text="Download", command=lambda: download_amazon_links_file(output_textbox))
    download_button.pack(pady=10)

    root.mainloop()
