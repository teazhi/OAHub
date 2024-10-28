import os
import sys
import customtkinter as ctk
from threading import Thread
from tkinter import filedialog, messagebox, ttk
import webbrowser
from wholesale import search_skus_from_file, get_search_results
import re
import shutil
from backend.utils import read_json
from backend.automation_main import start_automation
from tksheet import Sheet

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
        tag, tag_text, message_text = ("default", "", stripped_message)
        if "[INFO]" in stripped_message:
            tag, tag_text, message_text = "info", "[INFO]", stripped_message.replace("[INFO]", "")
        elif "[SUCCESS]" in stripped_message:
            tag, tag_text, message_text = "success", "[SUCCESS]", stripped_message.replace("[SUCCESS]", "")
        elif "[WARNING]" in stripped_message:
            tag, tag_text, message_text = "warning", "[WARNING]", stripped_message.replace("[WARNING]", "")
        elif "[ERROR]" in stripped_message:
            tag, tag_text, message_text = "error", "[ERROR]", stripped_message.replace("[ERROR]", "")
        elif "[503]" in stripped_message:
            tag, tag_text, message_text = "503", "[503]", stripped_message.replace("[503]", "")
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
    Thread(target=lambda: button.configure(text="Start", state="normal")).start()

def launch_gui():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.title("OAHub")
    root.geometry("1000x700")

    def update_store_dropdown():
        store_data = load_stores_config()
        store_names = list(store_data.keys())
        select_store_dropdown.configure(values=store_names)

    def update_dropdown_values(store):
        store_data = load_stores_config().get(store, {})
        promotions = store_data.get("promotions", ["No promotions available"])
        max_order_qty = int(store_data.get("max_order_qty", "1"))
        order_amounts = [str(i) for i in range(1, max_order_qty + 1)]
        promotion_dropdown.configure(values=promotions)
        order_amount_dropdown.configure(values=order_amounts)

    ctk.CTkLabel(root, text="OAHub", font=("Roboto", 45, "bold")).pack(pady=15)

    tab_view = ctk.CTkTabview(root, width=900, height=580)
    tab_view.pack(pady=(0, 20))

    home_tab = tab_view.add("Home")

    home_wrapper = ctk.CTkFrame(home_tab, width=850, height=500, fg_color="transparent")
    home_wrapper.pack(expand=True, padx=30, pady=20)
    
    form_frame = ctk.CTkFrame(home_wrapper, width=850, height=500)
    form_frame.pack(expand=True)

    form_frame.grid_columnconfigure(0, weight=1)
    form_frame.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(form_frame, text="Select store:", font=("Roboto", 18)).grid(row=0, column=0, padx=15, pady=15, sticky="e")
    select_store_var = ctk.StringVar(value="Select store...")
    select_store_dropdown = ctk.CTkComboBox(form_frame, variable=select_store_var, width=400, height=40, font=("Roboto", 14))
    select_store_dropdown.grid(row=0, column=1, padx=15, pady=15, sticky="w")
    update_store_dropdown()

    ctk.CTkLabel(form_frame, text="Item Link:", font=("Roboto", 18)).grid(row=1, column=0, padx=15, pady=15, sticky="e")
    item_link_var = ctk.StringVar()
    ctk.CTkEntry(form_frame, textvariable=item_link_var, width=400, height=40, font=("Roboto", 14)).grid(row=1, column=1, padx=15, pady=15, sticky="w")

    ctk.CTkLabel(form_frame, text="Promotion:", font=("Roboto", 18)).grid(row=2, column=0, padx=15, pady=15, sticky="e")
    promotion_var = ctk.StringVar(value="Select promotion...")
    promotion_dropdown = ctk.CTkComboBox(form_frame, variable=promotion_var, width=400, height=40, font=("Roboto", 14))
    promotion_dropdown.grid(row=2, column=1, padx=15, pady=15, sticky="w")

    ctk.CTkLabel(form_frame, text="Order amount:", font=("Roboto", 18)).grid(row=3, column=0, padx=15, pady=15, sticky="e")
    order_amount_var = ctk.StringVar(value="Select order amount...")
    order_amount_dropdown = ctk.CTkComboBox(form_frame, variable=order_amount_var, width=400, height=40, font=("Roboto", 14))
    order_amount_dropdown.grid(row=3, column=1, padx=15, pady=15, sticky="w")

    ctk.CTkLabel(form_frame, text="Times to run:", font=("Roboto", 18)).grid(row=4, column=0, padx=15, pady=15, sticky="e")
    times_to_run_var = ctk.StringVar(value="Select number of times to run")
    times_to_run_dropdown = ctk.CTkComboBox(form_frame, variable=times_to_run_var, values=["1", "2", "3", "4", "5"], width=400, height=40, font=("Roboto", 14))
    times_to_run_dropdown.grid(row=4, column=1, padx=15, pady=15, sticky="w")

    start_button = ctk.CTkButton(form_frame, text="Start", font=("Roboto", 18), width=200, height=50, command=lambda: start_home_automation(start_button))
    start_button.grid(row=5, column=0, columnspan=2, pady=(20, 10), sticky="ew")

    wholesale_tab = tab_view.add("Wholesale")
    wholesale_tab.grid_columnconfigure(0, weight=1)
    wholesale_tab.grid_columnconfigure(1, weight=1)

    wholesale_left_frame = ctk.CTkFrame(wholesale_tab, width=850, height=500)
    wholesale_left_frame.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")

    output_textbox = ctk.CTkTextbox(wholesale_left_frame, width=400, height=250, font=("Roboto", 12))
    output_textbox.grid(row=0, column=0, columnspan=2, pady=(5, 15), padx=15)
    output_textbox.configure(state="disabled")

    selected_file_var = ctk.StringVar()

    select_file_button = ctk.CTkButton(
        wholesale_left_frame, text="Select SKU File", anchor="center", width=180, height=40,
        command=lambda: select_skus_file(output_textbox, selected_file_var)
    )
    select_file_button.grid(row=1, column=0, padx=(10, 5), pady=5, sticky="ew")

    download_button = ctk.CTkButton(
        wholesale_left_frame, text="Download Latest Search", anchor="center", width=180, height=40,
        command=lambda: download_amazon_links_file(output_textbox)
    )
    download_button.grid(row=1, column=1, padx=(5, 10), pady=5, sticky="ew")

    wholesale_start_button = ctk.CTkButton(
        wholesale_left_frame, text="Start", anchor="center", width=380, height=40,
        command=lambda: start_automation_file(output_textbox, selected_file_var, wholesale_start_button)
    )
    wholesale_start_button.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

    show_results_button = ctk.CTkButton(
        wholesale_left_frame, text="Show Results", anchor="center", width=380, height=40,
        command=lambda: display_results_table(get_search_results())
    )
    show_results_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

    results_frame = ctk.CTkFrame(wholesale_tab, width=400, height=500)
    results_frame.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")

    table_frame = ctk.CTkFrame(results_frame, width=400, height=400)
    table_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

    results_frame.grid_columnconfigure(0, weight=1)
    results_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)
    table_frame.grid_rowconfigure(0, weight=1)

    results_table = ttk.Treeview(table_frame, columns=("SKU", "Amazon Link"), show="headings", height=18)
    results_table.heading("SKU", text="SKU")
    results_table.heading("Amazon Link", text="Amazon Link")
    results_table.column("SKU", anchor="center", width=150)
    results_table.column("Amazon Link", anchor="center", width=200)
    results_table.grid(row=0, column=0, sticky="nsew")

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=results_table.yview)
    results_table.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky="ns")

    def display_results_table(results):
        for widget in results_frame.winfo_children():
            widget.destroy()
        data = [[item["SKU"], item["Amazon Link"] if item["Amazon Link"] not in ["Not Found", "Bad Link"] else item["Amazon Link"]] for item in results]
        sheet = Sheet(results_frame, headers=["SKU", "Amazon Link"], data=data, width=400, height=300)
        sheet.column_width(column=0, width=150)
        sheet.column_width(column=1, width=200)

        sheet.enable_bindings("single_select", "column_select", "row_select", "cell_select", "copy")
        sheet.set_options(header_background="#444444", header_foreground="cyan", index_background="#333333", index_foreground="white", top_left_background="#333333", table_bg="#222222", table_fg="white", selected_cells_border_fg="cyan", selected_cells_bg="#555555", selected_cells_fg="white", table_selected_rows_bg="#444444", table_selected_rows_fg="white")
        sheet.grid(row=0, column=0, sticky="nsew")
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)

        def open_link(event):
            selected = sheet.get_currently_selected()
            if selected:
                row, col = selected[0], selected[1]
                if col == 1:
                    link_text = sheet.get_cell_data(row, col)
                    if link_text.startswith("https://www.amazon.com"):
                        webbrowser.open(link_text)

        sheet.bind("<Double-1>", open_link)

    select_store_dropdown.configure(command=lambda choice: update_dropdown_values(choice))
    root.mainloop()