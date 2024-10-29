import customtkinter as ctk

def create_obrowser_tab(tab_view):
    # Create O-Browser tab
    obrowser_tab = tab_view.add("O-Browser")
    obrowser_tab.grid_columnconfigure(0, weight=1)

    # Create Profile button 
    create_profile_button = ctk.CTkButton(obrowser_tab, text="Create Profile", width=100, command=lambda: create_profile_popup(obrowser_tab))
    create_profile_button.grid(row=0, column=0, padx=20, pady=20, sticky="nw")

    profile_display_frame = ctk.CTkFrame(obrowser_tab)
    profile_display_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
    profile_display_frame.grid_columnconfigure(0, weight=1)

    obrowser_tab.profile_display_frame = profile_display_frame

def create_profile_popup(obrowser_tab):
    popup = ctk.CTkToplevel()
    popup.title("Create Profile")
    popup.geometry("280x120")  
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

    # search bar
    search_entry = ctk.CTkEntry(popup, width=220, placeholder_text="Enter profile name...", font=("Roboto", 12))
    search_entry.pack(pady=(20, 5))  

    # search button
    search_button = ctk.CTkButton(popup, text="Create", width=80, command=lambda: add_profile_to_display(obrowser_tab, search_entry.get(), popup))
    search_button.pack(pady=(0, 10))

    search_entry.focus_set()

def add_profile_to_display(obrowser_tab, profile_name, popup):
    if profile_name:
        popup.destroy()

        # frame
        profile_frame = ctk.CTkFrame(obrowser_tab.profile_display_frame)
        profile_frame.grid_columnconfigure(0, weight=1)  # Allow profile name column to expand
        profile_frame.grid_columnconfigure(1, weight=0)
        profile_frame.grid_columnconfigure(2, weight=0)
        
        # profile label 
        profile_label = ctk.CTkLabel(profile_frame, text=profile_name, font=("Roboto", 12))
        profile_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Run button
        run_button = ctk.CTkButton(profile_frame, text="Run", width=50)
        run_button.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="e")

        # ready status
        status_label = ctk.CTkLabel(profile_frame, text="ready", font=("Roboto", 10))
        status_label.grid(row=0, column=2, padx=10, pady=5, sticky="e")

        profile_frame.pack(fill="x", expand=True, pady=5)