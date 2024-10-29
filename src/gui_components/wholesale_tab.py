import customtkinter as ctk

def create_wholesale_tab(tab_view):
    # Create Wholesale tab
    wholesale_tab = tab_view.add("Wholesale")
    wholesale_tab.grid_columnconfigure(0, weight=1)

    wholesale_left_frame = ctk.CTkFrame(wholesale_tab)
    wholesale_left_frame.grid(row=0, column=0, pady=20, padx=0)

    output_textbox = ctk.CTkTextbox(wholesale_left_frame, width=500, height=300, wrap="word", state="disabled")
    output_textbox.pack(pady=10)

    wholesale_button = ctk.CTkButton(wholesale_left_frame, text="Start", command=lambda: print("Wholesale Automation Started"), width=200, height=50)
    wholesale_button.pack(pady=20)

    wholesale_right_frame = ctk.CTkFrame(wholesale_tab)
    wholesale_right_frame.grid(row=0, column=1, pady=20, padx=30, sticky="n")

    selected_file_var = ctk.StringVar()

    file_button = ctk.CTkButton(wholesale_right_frame, text="Select SKU File", command=lambda: print("SKU File Selected"))
    file_button.pack(pady=5)

    download_button = ctk.CTkButton(wholesale_right_frame, text="Download\nLatest Search", command=lambda: print("Downloaded Latest Search"))
    download_button.pack(pady=5)
