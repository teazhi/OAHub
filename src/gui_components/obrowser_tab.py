import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import customtkinter as ctk
import os
import shutil
import asyncio
from playwright.async_api import async_playwright
import threading

def create_obrowser_tab(tab_view):
    # Create O-Browser tab
    obrowser_tab = tab_view.add("O-Browser")
    obrowser_tab.grid_columnconfigure(0, weight=1)

    create_profile_button = ctk.CTkButton(
        obrowser_tab, 
        text="Create Profile", 
        width=100, 
        command=lambda: create_profile_popup(obrowser_tab)
    )
    create_profile_button.grid(row=0, column=0, padx=100, pady=20, sticky="nw")  

    profile_display_frame = ctk.CTkFrame(obrowser_tab)
    profile_display_frame.grid(row=1, column=0, padx=100, pady=20, sticky="nsew") 
    profile_display_frame.grid_columnconfigure(0, weight=1)
    
    obrowser_tab.profile_display_frame = profile_display_frame

    load_profiles(obrowser_tab)

    return obrowser_tab  

def create_profile_popup(obrowser_tab):
    popup = ctk.CTkToplevel()
    popup.title("Create Profile")
    popup.geometry("280x160") 
    popup.resizable(False, False)

    main_window = obrowser_tab.winfo_toplevel() 
    main_window_x = main_window.winfo_x()
    main_window_y = main_window.winfo_y()
    main_window_width = main_window.winfo_width()
    main_window_height = main_window.winfo_height()
    x_cordinate = main_window_x + (main_window_width // 2) - (popup.winfo_reqwidth() // 2)
    y_cordinate = main_window_y + (main_window_height // 2) - (popup.winfo_reqheight() // 2)
    popup.geometry(f"+{x_cordinate}+{y_cordinate}")

    popup.attributes("-topmost", True)  
    popup.configure(bg="#333333") 

    search_entry = ctk.CTkEntry(popup, width=220, placeholder_text="Enter profile name...", font=("Roboto", 12))
    search_entry.pack(pady=(20, 5))
    search_entry.focus_set()

    error_label = ctk.CTkLabel(popup, text="", font=("Roboto", 10), text_color="red")
    error_label.pack(pady=(5, 5))

    search_button = ctk.CTkButton(
        popup, 
        text="Create", 
        width=80, 
        command=lambda: validate_and_create_profile(obrowser_tab, search_entry.get(), popup, error_label)
    )
    search_button.pack(pady=(0, 10))

def validate_and_create_profile(obrowser_tab, profile_name, popup, error_label):
    if not profile_name.strip():
        error_label.configure(text="Error: Profile name cannot be empty.")
        return

    folder_path = os.path.join("o_browser_profiles", profile_name)
    if os.path.exists(folder_path):
        error_label.configure(text="Error: Profile already exists.")
        return

    add_profile_to_display(obrowser_tab, profile_name, popup)

def show_settings_popup(profile_frame):
    popup = ctk.CTkToplevel()
    popup.title("Settings")
    popup.geometry("200x150")
    popup.resizable(False, False)

    main_window = profile_frame.winfo_toplevel()
    main_window_x = main_window.winfo_x()
    main_window_y = main_window.winfo_y()
    main_window_width = main_window.winfo_width()
    main_window_height = main_window.winfo_height()
    popup.geometry(f"+{main_window_x + (main_window_width // 2) - 100}+{main_window_y + (main_window_height // 2) - 75}")

    popup.configure(bg="#333333")

    # Delete Profile button
    delete_button = ctk.CTkButton(
        popup,
        text="Delete Profile",
        command=lambda: delete_profile(profile_frame, popup)
    )
    delete_button.pack(pady=(20, 10))  # Add spacing

    # Rename Profile button
    rename_button = ctk.CTkButton(
        popup,
        text="Rename Profile",
        command=lambda: show_rename_popup(profile_frame, popup)
    )
    rename_button.pack(pady=(10, 20))

    popup.attributes("-topmost", True)

def show_rename_popup(profile_frame, settings_menu):
    settings_menu.destroy()

    rename_popup = ctk.CTkToplevel()
    rename_popup.title("Rename Profile")
    rename_popup.geometry("300x150")
    rename_popup.resizable(False, False)

    main_window = profile_frame.winfo_toplevel()
    main_window_x = main_window.winfo_x()
    main_window_y = main_window.winfo_y()
    main_window_width = main_window.winfo_width()
    main_window_height = main_window.winfo_height()
    rename_popup.geometry(f"+{main_window_x + (main_window_width // 2) - 150}+{main_window_y + (main_window_height // 2) - 75}")

    rename_popup.configure(bg="#333333")

    # new profile name
    new_name_entry = ctk.CTkEntry(rename_popup, width=250, placeholder_text="Enter new profile name...")
    new_name_entry.pack(pady=(20, 10))
    new_name_entry.focus_set()

    error_label = ctk.CTkLabel(rename_popup, text="", font=("Roboto", 10), text_color="red")
    error_label.pack(pady=(5, 5))

    # Rename button
    rename_button = ctk.CTkButton(
        rename_popup,
        text="Rename",
        command=lambda: rename_profile(profile_frame, new_name_entry.get(), error_label, rename_popup)
    )
    rename_button.pack(pady=(10, 20))

def rename_profile(profile_frame, new_name, error_label, rename_popup):
    if not new_name.strip():
        error_label.configure(text="Error: Profile name cannot be empty.")
        return

    old_folder_path = profile_frame.folder_path
    new_folder_path = os.path.join("o_browser_profiles", new_name)

    if os.path.exists(new_folder_path):
        error_label.configure(text="Error: Profile name already exists.")
        return

    try:
        os.rename(old_folder_path, new_folder_path)
        profile_frame.folder_path = new_folder_path
        profile_label = profile_frame.grid_slaves(row=0, column=0)[0]
        profile_label.configure(text=new_name)
        rename_popup.destroy() 
    except Exception as e:
        error_label.configure(text=f"Error: {str(e)}")


def delete_profile(profile_frame, settings_menu):
    folder_path = profile_frame.folder_path
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)  
    
    profile_frame.destroy()
    settings_menu.destroy()

def load_profiles(obrowser_tab):
    profiles_dir = "o_browser_profiles"

    if not os.path.exists(profiles_dir):
        os.makedirs(profiles_dir)

    for profile_name in os.listdir(profiles_dir):
        profile_path = os.path.join(profiles_dir, profile_name)

        if os.path.isdir(profile_path):
            add_profile_to_display(obrowser_tab, profile_name, popup=None)


async def open_browser(profile_name, status_label, run_button):
    profile_dir = os.path.join(os.getcwd(), f"o_browser_profiles/{profile_name}")

    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir)

    status_label.configure(text="Running")
    run_button.configure(state=tk.DISABLED)

    async with async_playwright() as p:
        browser_type = p.chromium
        context = await browser_type.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False
        )

        if not context.pages:
            page = await context.new_page()
        else:
            page = context.pages[0]

        await page.goto("https://www.google.com")

        try:
            while len(context.pages) > 0:
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Error during browser check: {e}")

    status_label.configure(text="Ready")
    run_button.configure(state=tk.NORMAL) 

def run_browser_in_thread(profile_name, status_label, run_button):
    def browser_task():
        asyncio.run(open_browser(profile_name, status_label, run_button))
    
    threading.Thread(target=browser_task, daemon=True).start()

def add_profile_to_display(obrowser_tab, profile_name, popup=None):
    if popup:
        popup.destroy()

    folder_path = os.path.join("o_browser_profiles", profile_name)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    profile_frame = ctk.CTkFrame(obrowser_tab.profile_display_frame)
    profile_frame.grid_columnconfigure(0, weight=1)
    profile_frame.grid_columnconfigure(1, weight=0)
    profile_frame.grid_columnconfigure(2, weight=0)
    profile_frame.grid_columnconfigure(3, weight=0)

    # Profile label
    profile_label = ctk.CTkLabel(profile_frame, text=profile_name, font=("Roboto", 12))
    profile_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

    # Status label
    status_label = ctk.CTkLabel(profile_frame, text="Ready", font=("Roboto", 10))
    status_label.grid(row=0, column=2, padx=10, pady=5, sticky="e")

    run_button = ctk.CTkButton(
        profile_frame,
        text="Run",
        width=50,
        command=lambda: run_browser_in_thread(profile_name, status_label, run_button)
    )
    run_button.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="e")

    # Triple dot settings button
    settings_button = ctk.CTkLabel(profile_frame, text="⋮", font=("Roboto", 14), cursor="hand2")
    settings_button.grid(row=0, column=3, padx=10, pady=5, sticky="e")
    settings_button.bind("<Button-1>", lambda event: show_settings_popup(profile_frame))


    profile_frame.pack(fill="x", expand=True, pady=5)

    profile_frame.folder_path = folder_path
