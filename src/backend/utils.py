import json
import os
from playwright.sync_api import Playwright, sync_playwright
import random
import time
from fake_useragent import UserAgent
import shutil
import datetime
import urllib.parse

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
    label.configure(text=message)

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

def is_valid_amazon_link(link):
    return link.startswith("https://www.amazon.com/") and "aax-us-iad" not in link and "sspa/click" not in link and "gp/help" not in link

def get_next_file_number(directory, base_filename, extension):
    i = 1
    while os.path.exists(f"{directory}/{base_filename} {i}{extension}"):
        i += 1
    return i

def move_and_rename_files(old_sku_dir, filename):
    os.makedirs(old_sku_dir, exist_ok=True)
    
    base_name = os.path.splitext(filename)[0]
    new_csv_name = f"{base_name}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    
    try:
        shutil.move(filename, os.path.join(old_sku_dir, new_csv_name))
        print(f"[INFO] Moved {filename} to {old_sku_dir} as {new_csv_name}")
    except FileNotFoundError:
        print(f"[ERROR] File {filename} not found, skipping move.")

def get_proxy_and_headers(proxies, user_agent):
    proxy_config = random.choice(proxies)
    headers = {
        "User-Agent": user_agent.random,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    
    if 'username' in proxy_config and 'password' in proxy_config:
        proxy = {
            'http': f"http://{proxy_config['username']}:{urllib.parse.quote(proxy_config['password'])}@{proxy_config['address']}",
            'https': f"http://{proxy_config['username']}:{urllib.parse.quote(proxy_config['password'])}@{proxy_config['address']}"
        }
    else:
        proxy = {
            'http': f"http://{proxy_config['address']}",
            'https': f"http://{proxy_config['address']}"
        }
        
    return proxy, headers

def load_proxies(file_path):
    proxies = []
    with open(file_path, 'r') as f:
        for line in f:
            proxy_parts = line.strip().split(':')
            if len(proxy_parts) == 4:
                ip, port, username, password = proxy_parts
                proxies.append({
                    'username': username,
                    'password': password,
                    'address': f"{ip}:{port}"
                })
            elif len(proxy_parts) == 2:
                ip, port = proxy_parts
                proxies.append({
                    'address': f"{ip}:{port}"
                })
    return proxies


def create_driver(playwright):
    try:
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

        browser = playwright.chromium.launch(
            headless=False,
            proxy=proxy,
            args=[
                "--disable-web-security",
                "--disable-blink-features=AutomationControlled" 
            ]
        )

        context = browser.new_context(
            user_agent=user_agent,
            viewport={"width": 1280, "height": 844},
            permissions=["geolocation"],
            geolocation={"latitude": 37.7749, "longitude": -122.4194},
            locale="en-US",
            accept_downloads=True,
            bypass_csp=True,
            java_script_enabled=True
        )
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

        def random_headers(route):
            headers = {
                'User-Agent': user_agent,
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.google.com/',
                'Content-Type': 'application/json',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            route.continue_(headers=headers)

        context.route("**/*", random_headers)

        print("Driver created successfully")
        page = context.new_page()

        return browser, context, page

    except Exception as e:
        print(f"Error in create_driver: {e}")
        return None, None, None
