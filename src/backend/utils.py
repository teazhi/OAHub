import json
import os

def read_json(file_path):
    """Read a JSON file and return its content."""
    with open(file_path, 'r') as file:
        return json.load(file)
    
def validate_url(base_url, url):
    """Check if the provided URL starts with the base URL."""
    return url.startswith(base_url)

def apply_hover_effect(button, hover_bg, hover_fg, normal_bg, normal_fg):
    """Apply a hover effect to the provided button."""
    def on_hover(event):
        button.config(bg=hover_bg, fg=hover_fg)
    
    def off_hover(event):
        button.config(bg=normal_bg, fg=normal_fg)
    
    button.bind("<Enter>", on_hover)
    button.bind("<Leave>", off_hover)

def display_error(label, message):
    """Display an error message on the provided label."""
    label.config(text=message)

def configure_grid(root, rows, columns):
    """Configure grid layout for the root window."""
    for row in rows:
        root.grid_rowconfigure(row, weight=1)
    for col in columns:
        root.grid_columnconfigure(col, weight=1)