import os
import shutil
import requests
from bs4 import BeautifulSoup
import csv
import time
import random
from fake_useragent import UserAgent
from colorama import Fore, Style, init

import sys
print(sys.executable)

init(autoreset=True)

MAX_RETRIES = 5
OLD_SKUS_DIR = "src/oldskus"
SRC_DIR = "src"

def load_proxies(file_path):
    proxies = []
    with open(file_path, 'r') as f:
        for line in f:
            proxy_parts = line.strip().split(':')
            if len(proxy_parts) == 4:
                ip, port, username, password = proxy_parts
                proxy = {
                    'http': f'http://{username}:{password}@{ip}:{port}',
                    'https': f'https://{username}:{password}@{ip}:{port}'
                }
                proxies.append(proxy)
            elif len(proxy_parts) == 2:
                ip, port = proxy_parts
                proxy = {
                    'http': f'http://{ip}:{port}',
                    'https': f'https://{ip}:{port}'
                }
                proxies.append(proxy)
    return proxies

def is_valid_amazon_link(link):
    if not link.startswith("https://www.amazon.com/"):
        return False
    if "aax-us-iad" in link or "sspa/click" in link:
        return False
    return True

def search_amazon_by_sku(sku, proxies, user_agent):
    retries = 0

    while retries < MAX_RETRIES:
        proxy = random.choice(proxies)
        # print(f"Proxy: {proxy}\nUser Agent: {user_agent}")

        headers = {
            "User-Agent": user_agent,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }

        search_url = f"https://www.amazon.com/s?k={sku}"

        try:
            response = requests.get(search_url, headers=headers, proxies=proxy, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                product_link = soup.find('a', {'class': 'a-link-normal s-no-outline'})
                if product_link:
                    link = "https://www.amazon.com" + product_link['href']
                    if is_valid_amazon_link(link):
                        print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} Product found!")
                        return link
                    else:
                        print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} Irrelevant link found.")
                        return "Bad Link"
                else:
                    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} No product found.")
                    return "Not Found"
            elif response.status_code == 503:
                retries += 1
                print(f"{Fore.RED}[503]{Style.RESET_ALL} Retrying with a different proxy ({retries}/{MAX_RETRIES})...")
                time.sleep(5 * retries)
            else:
                print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Failed to retrieve search results for SKU {sku}, Status Code: {response.status_code}")
                return f"Status Code: {response.status_code}"

        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Request failed for SKU {sku} using proxy {proxy['http']}: {e}")
            return "Request Failed"
    
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Max retries reached.")
    return "Max Retries"

def get_next_file_number(directory, base_filename, extension):
    i = 1
    while True:
        new_filename = f"{base_filename} {i}{extension}"
        if not os.path.exists(os.path.join(directory, new_filename)):
            return i
        i += 1

def move_and_rename_files():
    if not os.path.exists(OLD_SKUS_DIR):
        os.makedirs(OLD_SKUS_DIR)

    next_number = get_next_file_number(OLD_SKUS_DIR, "amazon_links_from_skus", ".csv")

    new_csv_name = f"amazon_links_from_skus {next_number}.csv"
    shutil.move("amazon_links_from_skus.csv", os.path.join(OLD_SKUS_DIR, new_csv_name))

    print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} Files have been renamed and moved to {OLD_SKUS_DIR}.")

def search_skus_from_file(file_path, proxies_file):
    proxies = load_proxies(proxies_file)
    
    user_agent = UserAgent().random

    with open(file_path, 'r') as file:
        skus = [line.strip() for line in file.readlines()]

    print(f"Running finder for all {len(skus)} SKU's...")

    results = []
    for sku in skus:
        print(f"{Fore.MAGENTA}{'─'*40}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} Searching for SKU: {sku}")
        
        amazon_link = search_amazon_by_sku(sku, proxies, user_agent)
        results.append({'SKU': sku, 'Amazon Link': amazon_link})

        delay = random.uniform(1, 5)
        print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} Sleeping for {delay:.2f} seconds...")
        time.sleep(delay)

    print(f"{Fore.MAGENTA}{'─'*40}{Style.RESET_ALL}")

    with open('amazon_links_from_skus.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['SKU', 'Amazon Link'])
        writer.writeheader()
        writer.writerows(results)

    print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} Search complete. Results saved to amazon_links_from_skus.csv")

    move_and_rename_files()
