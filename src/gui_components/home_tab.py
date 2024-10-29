import customtkinter as ctk

def create_home_tab(tab_view):
    # Create Home tab
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

    action_button = ctk.CTkButton(home_tab, text="Start", command=lambda: print("Home Automation Started"), width=200, height=50, font=("Roboto", 12, "bold"))
    action_button.grid(row=2, column=0, pady=20)

    error_label = ctk.CTkLabel(home_tab, text="", font=("Roboto", 12), text_color="red")
    error_label.grid(row=3, column=0, pady=5)
