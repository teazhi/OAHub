import json
import os
from playwright.sync_api import Playwright, sync_playwright
import random
import time
from fake_useragent import UserAgent

def random_delay(min_time=0.5, max_time=2.5):
    time.sleep(random.uniform(min_time, max_time))

def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def validate_url(base_url, url):
    return url.startswith(base_url)

def apply_hover_effect(button, hover_bg, hover_fg, normal_bg, normal_fg):
    def on_hover(event):
        button.config(bg=hover_bg, fg=hover_fg)
    
    def off_hover(event):
        button.config(bg=normal_bg, fg=normal_fg)
    
    button.bind("<Enter>", on_hover)
    button.bind("<Leave>", off_hover)

def display_error(label, message):
    label.config(text=message)

def random_mouse_movement(page):
    for _ in range(10):
        x = random.randint(0, 1280)
        y = random.randint(0, 800)
        page.mouse.move(x, y)
        random_delay(0.1, 0.3)

def configure_grid(root, rows, columns):
    for row in rows:
        root.grid_rowconfigure(row, weight=1)
    for col in columns:
        root.grid_columnconfigure(col, weight=1)

def load_proxies_from_file(file_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, '..', '..', 'config', file_name)

    print(f"Looking for proxies file at: {file_path}")

    with open(file_path, 'r') as file:
        proxies = [line.strip() for line in file if line.strip()]
    return proxies

def load_proxies_from_file(file_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, '..', '..', 'config', file_name)
    
    with open(file_path, 'r') as file:
        proxies = [line.strip() for line in file if line.strip()]
    return proxies

def create_driver(playwright):
    try:
        # Load proxies from file
        proxy_list = load_proxies_from_file('proxies.txt')
        selected_proxy = random.choice(proxy_list)
        print(f"Using proxy: {selected_proxy}")

        proxy_ip, proxy_port, proxy_username, proxy_password = selected_proxy.split(":")
        proxy = {
            "server": f"http://{proxy_ip}:{proxy_port}",
            "username": proxy_username,
            "password": proxy_password
        }

        user_agent = UserAgent().random
        print(f"Using user agent: {user_agent}")

        # Launch the browser with proxy settings
        browser = playwright.chromium.launch(
            headless=False,
            #proxy=proxy,
            args=[
                "--disable-web-security",
                "--disable-blink-features=AutomationControlled"  # Disable automation features
            ]
        )

        # Create a new context with user agent and other settings
        context = browser.new_context(
            user_agent=user_agent,
            viewport={"width": 1280, "height": 844},  # Example desktop resolution
            permissions=["geolocation"],
            geolocation={"latitude": 37.7749, "longitude": -122.4194},  # Example: San Francisco
            locale="en-US",
            accept_downloads=True,
            bypass_csp=True,
            java_script_enabled=True
        )

        # Stealth mode: remove WebDriver and other detection features
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
            window.chrome = { runtime: {} };
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({ state: 'denied' }) :
                originalQuery(parameters)
            );
            delete navigator.__proto__.webdriver;
            delete navigator.webdriver;
        """)

        # Headers randomization
        def random_headers(route):
            headers = {
                'User-Agent': user_agent,
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.google.com/',
                'Content-Type': 'application/json',
                'DNT': '1',  # Do Not Track
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            route.continue_(headers=headers)

        # Apply random headers to each request
        context.route("**/*", random_headers)

        print("Driver created successfully")
        page = context.new_page()

        return browser, context, page

    except Exception as e:
        print(f"Error in create_driver: {e}")
        return None, None, None
