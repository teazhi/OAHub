import json
import os
from playwright.sync_api import Playwright, sync_playwright
from playwright_stealth import stealth_sync
import random
import time
from fake_useragent import UserAgent

def random_delay(min_time=0.5, max_time=1.5):
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

def create_driver(playwright):
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

    def get_mobile_user_agent():
        return "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"
        # mobile_user_agents = [
        #     "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",  # iPhone 12 Pro
        #     "Mozilla/5.0 (Linux; Android 11; SM-G980F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",  # Samsung Galaxy S20
        #     "Mozilla/5.0 (Linux; Android 11; Pixel 5 Build/RP1A.200720.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",  # Google Pixel 5
        # ]
        # user_agent = random.choice(mobile_user_agents)
        # print(f"Using User-Agent: {user_agent}")
        
        # return user_agent

    user_agent = get_mobile_user_agent()

    # Launch the browser with global proxy settings
    browser = playwright.chromium.launch(
        headless=True,  # Set to True if you want headless browsing
        proxy=proxy
    )

    # Create a new context with user agent and other settings
    context = browser.new_context(
        user_agent=user_agent,
        viewport={"width": 390, "height": 844},  # iPhone 12 Pro resolution
        is_mobile=True,  # Enable mobile emulation
        device_scale_factor=3,  # Retina display scale factor
        has_touch=True,  # Enable touch events
        permissions=["geolocation"],
        geolocation={"latitude": 37.7749, "longitude": -122.4194},  # Example: San Francisco
        locale="en-US",
        accept_downloads=True,
        bypass_csp=True,
        java_script_enabled=True  # Keep JavaScript enabled
    )

    # stealth_sync(context)

    # Stealth mode: remove WebDriver and other detection features
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
        window.chrome = { runtime: {} };  // Fake Chrome object
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
            'DNT': '1',  # Do Not Track
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        route.continue_(headers=headers)

    # Apply random headers to each request
    context.route("**/*", random_headers)

    # Create a new page
    page = context.new_page()

    return browser, context, page