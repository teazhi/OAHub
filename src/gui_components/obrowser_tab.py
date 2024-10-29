import customtkinter as ctk

def create_obrowser_tab(tab_view):
    # Create O-Browser tab
    obrowser_tab = tab_view.add("O-Browser")
    obrowser_tab.grid_columnconfigure(0, weight=1)

    obrowser_frame = ctk.CTkFrame(obrowser_tab)
    obrowser_frame.grid(row=0, column=0, padx=20, pady=20)

    obrowser_label = ctk.CTkLabel(obrowser_frame, text="Welcome to O-Browser", font=("Roboto", 16))
    obrowser_label.grid(row=0, column=0, pady=10)

    obrowser_instructions = ctk.CTkLabel(obrowser_frame, text="This is a new page for the O-Browser feature. Add more functionalities here as needed.", font=("Roboto", 12))
    obrowser_instructions.grid(row=1, column=0, pady=5)

    # Add a search entry box
    search_entry = ctk.CTkEntry(obrowser_frame, width=300, placeholder_text="Enter search query...")
    search_entry.grid(row=2, column=0, pady=10)

    # Add a search button
    search_button = ctk.CTkButton(obrowser_frame, text="Search", command=lambda: print(f"Searching for: {search_entry.get()}"))
    search_button.grid(row=3, column=0, pady=10)
