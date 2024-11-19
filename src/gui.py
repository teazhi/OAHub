import os
import sys
import requests
import customtkinter as ctk
from threading import Thread
from tkinter import filedialog, messagebox, simpledialog, ttk
import webbrowser
import re
import shutil
from wholesale import search_skus_on_amazon, get_search_results, walmart_search_concurrently
from backend.utils import read_json
from backend.automation_main import start_automation
from tksheet import Sheet
import fitz
import state_manager
from auth import SUPABASE_URL, SUPABASE_KEY, supabase

ctk.set_appearance_mode("dark")

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

class OAHubApp:
    def __init__(self, root):
        self.root = root
        self.token = None
        self.sheet = None
        self.root.title("OAHub")
        self.root.geometry("1000x700")
        self.show_login_screen()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.root.destroy()
        sys.exit()

    def show_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        login_frame = ctk.CTkFrame(self.root, width=400, height=300, corner_radius=10)
        login_frame.pack(expand=True)

        ctk.CTkLabel(login_frame, text="Login", font=("Roboto", 24, "bold")).pack(pady=20)

        self.token_var = ctk.StringVar()
        ctk.CTkEntry(login_frame, textvariable=self.token_var, placeholder_text="Enter your access token", width=250).pack(pady=10)

        ctk.CTkButton(login_frame, text="Login", command=self.handle_login).pack(pady=10)

    def handle_login(self):
        self.token = self.token_var.get().strip()
        if self.token:
            if self.verify_token():
                messagebox.showinfo("Login Successful", "You have successfully logged in.")
                self.show_main_interface()
            else:
                messagebox.showerror("Login Failed", "Invalid token. Please try again.")
        else:
            messagebox.showwarning("No Token", "Please enter a token to continue.")

    def verify_token(self):
        response = requests.post(f"{SUPABASE_URL}/login", headers={"Authorization": self.token})
        return response.status_code == 200

    def show_main_interface(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.root, text="OAHub", font=("Roboto", 45, "bold")).pack(pady=15)

        tab_view = ctk.CTkTabview(self.root, width=900, height=580)
        tab_view.pack(pady=(0, 20))

        home_tab = tab_view.add("Home")
        wholesale_tab = tab_view.add("Wholesale")

        self.create_home_tab(home_tab)
        self.create_wholesale_tab(wholesale_tab)

    def create_home_tab(self, tab):
        home_wrapper = ctk.CTkFrame(tab, width=850, height=500, fg_color="transparent")
        home_wrapper.pack(expand=True, padx=30, pady=20)

        form_frame = ctk.CTkFrame(home_wrapper, width=850, height=500)
        form_frame.pack(expand=True)

        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form_frame, text="Select store:", font=("Roboto", 18)).grid(row=0, column=0, padx=15, pady=15, sticky="e")
        select_store_var = ctk.StringVar(value="Select store...")
        select_store_dropdown = ctk.CTkComboBox(form_frame, variable=select_store_var, width=400, height=40, font=("Roboto", 14))
        select_store_dropdown.grid(row=0, column=1, padx=15, pady=15, sticky="w")
        self.update_store_dropdown(select_store_dropdown)

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

        start_button = ctk.CTkButton(form_frame, text="Start", font=("Roboto", 18), width=200, height=50,
                                    command=lambda: start_automation(start_button, select_store_var.get(), item_link_var.get(), promotion_var.get(), order_amount_var.get(), times_to_run_var.get()))
        start_button.grid(row=5, column=0, columnspan=2, pady=(20, 10), sticky="ew")

    def update_store_dropdown(self, select_store_dropdown):
        store_data = self.load_stores_config()
        store_names = list(store_data.keys())
        select_store_dropdown.configure(values=store_names)

    def load_stores_config(self):
        json_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'stores.json')
        return read_json(json_path)

    def create_wholesale_tab(self, tab):
        wholesale_left_frame = ctk.CTkFrame(tab, width=425, height=500)
        wholesale_left_frame.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")

        output_textbox = ctk.CTkTextbox(wholesale_left_frame, width=400, height=300, font=("Roboto", 12))
        output_textbox.grid(row=0, column=0, columnspan=2, pady=(5, 15), padx=15)
        output_textbox.configure(state="disabled")

        selected_file_var = ctk.StringVar()

        ctk.CTkButton(wholesale_left_frame, text="Select SKU File", anchor="center", width=180, height=40,
                      command=lambda: self.select_skus_file(output_textbox, selected_file_var)).grid(row=1, column=0, padx=(10, 5), pady=5, sticky="ew")
        ctk.CTkButton(wholesale_left_frame, text="Select PDF File", anchor="center", width=180, height=40,
                      command=lambda: self.select_pdf_file(output_textbox, selected_file_var)).grid(row=1, column=1, padx=(5, 10), pady=5, sticky="ew")
        ctk.CTkButton(wholesale_left_frame, text="Download Latest Search", anchor="center", width=180, height=40,
                      command=lambda: self.download_amazon_links_file(output_textbox)).grid(row=3, column=0, padx=(10, 5), pady=5, sticky="ew")

        ctk.CTkButton(wholesale_left_frame, text="Start Amazon", anchor="center", width=180, height=40, fg_color="#228B22",
                      command=lambda: self.start_amazon_search(output_textbox, selected_file_var, wholesale_button=None)).grid(row=2, column=1, padx=(5, 10), pady=5, sticky="ew")
        ctk.CTkButton(wholesale_left_frame, text="Start Walmart", anchor="center", width=180, height=40, fg_color="#228B22",
                      command=lambda: self.start_walmart_search(output_textbox, selected_file_var, wholesale_button=None)).grid(row=2, column=0, padx=(10, 5), pady=5, sticky="ew")

        wholesale_right_frame = ctk.CTkFrame(tab, width=425, height=500)
        wholesale_right_frame.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")

        self.sheet = Sheet(wholesale_right_frame, width=400, height=400)
        self.sheet.pack(fill="both", expand=True)
        self.sheet.headers(["SKU", "Details"])
        self.sheet.set_sheet_data([])

        ctk.CTkButton(wholesale_left_frame, text="Show Results", anchor="center", width=180, height=40,
                      command=lambda: self.show_results(output_textbox)).grid(row=3, column=1, padx=(5, 10), pady=10, sticky="ew")

    def select_pdf_file(self, output_textbox, selected_file_var):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.extracted_skus = self.extract_skus_from_pdf(file_path)
            output_textbox.configure(state="normal")
            output_textbox.insert(ctk.END, f"Extracted {len(self.extracted_skus)} SKUs from PDF.\n")
            output_textbox.configure(state="disabled")
        else:
            output_textbox.configure(state="normal")
            output_textbox.insert(ctk.END, "No file selected.\n")
            output_textbox.configure(state="disabled")

    def extract_skus_from_pdf(self, file_path):
        skus = []
        with fitz.open(file_path) as doc:
            for page_num in range(doc.page_count):
                text = doc.load_page(page_num).get_text("text")
                skus.extend(re.findall(r'\b\d{7,14}\b', text))
        return skus

    def show_results(self, output_textbox):
        try:
            output_textbox.configure(state="normal")
            output_textbox.delete("1.0", ctk.END)
            output_textbox.configure(state="disabled")

            if not isinstance(sys.stdout, DualOutput):
                sys.stdout = DualOutput(output_textbox)

            results = get_search_results()
            if not results:
                messagebox.showinfo("No Results", "No results found.")
                return

            data = [[result['SKU'], result.get('Details', 'N/A')] for result in results]
            self.sheet.set_sheet_data(data)

            output_textbox.configure(state="normal")
            output_textbox.insert(ctk.END, "Results successfully loaded into the table.\n")
            output_textbox.configure(state="disabled")
        except Exception as e:
            output_textbox.configure(state="normal")
            output_textbox.insert(ctk.END, f"Error: {e}\n")
            output_textbox.configure(state="disabled")
            messagebox.showerror("Error", f"Failed to fetch results: {e}")

    def select_skus_file(self, output_textbox, selected_file_var):
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

    def select_pdf_file(self, output_textbox, selected_file_var):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.extracted_skus = self.extract_skus_from_pdf(file_path)
            output_textbox.configure(state="normal")
            output_textbox.insert(ctk.END, f"Extracted {len(self.extracted_skus)} SKUs from PDF.\n")
            output_textbox.configure(state="disabled")
        else:
            output_textbox.configure(state="normal")
            output_textbox.insert(ctk.END, "No file selected.\n")
            output_textbox.configure(state="disabled")

    def extract_skus_from_pdf(self, file_path):
        skus = []
        with fitz.open(file_path) as doc:
            for page_num in range(doc.page_count):
                text = doc.load_page(page_num).get_text("text")
                skus.extend(re.findall(r'\b\d{7,14}\b', text))
        return skus

    def download_amazon_links_file(self, output_textbox):
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

    def start_amazon_search(self, output_widget, selected_file_var, wholesale_button):
        output_widget.configure(state="normal")
        output_widget.delete("1.0", ctk.END)
        output_widget.configure(state="disabled")

        if not isinstance(sys.stdout, DualOutput):
            sys.stdout = DualOutput(output_widget)

        if not state_manager.is_running:
            state_manager.is_running = True
            wholesale_button.configure(text="STOP", fg_color="red")

            proxies_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'proxies.txt')
            skus_file_path = selected_file_var.get()
            if skus_file_path:
                thread = Thread(target=lambda: search_skus_on_amazon(file_path=skus_file_path, proxies_file=proxies_file_path))
                thread.start()
            else:
                state_manager.is_running = False
                messagebox.showwarning("Warning", "Please select a SKU file first.")
        else:
            state_manager.is_running = False
            wholesale_button.configure(text="Start Amazon", fg_color="#228B22")

    def start_walmart_search(self, output_widget, selected_file_var, wholesale_button):
        output_widget.configure(state="normal")
        output_widget.delete("1.0", ctk.END)
        output_widget.configure(state="disabled")

        if not isinstance(sys.stdout, DualOutput):
            sys.stdout = DualOutput(output_widget)

        if not state_manager.is_running:
            state_manager.is_running = True
            wholesale_button.configure(text="STOP", fg_color="red")

            proxies_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'proxies.txt')
            skus_file_path = selected_file_var.get()
            if skus_file_path:
                with open(skus_file_path, 'r') as file:
                    skus = [line.strip() for line in file.readlines()]
                thread = Thread(target=lambda: walmart_search_concurrently(skus, proxies_file_path))
                thread.start()
            else:
                state_manager.is_running = False
                messagebox.showwarning("Warning", "Please select a SKU file first.")
        else:
            state_manager.is_running = False
            wholesale_button.configure(text="Start Walmart", fg_color="#228B22")

def launch_gui():
    root = ctk.CTk()
    app = OAHubApp(root)
    root.mainloop()