import os
import requests
from bs4 import BeautifulSoup
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from fake_useragent import UserAgent
from colorama import Fore, Style, init

import state_manager
from backend.utils import load_proxies, is_valid_amazon_link, move_and_rename_files, get_proxy_and_headers

init(autoreset=True)

MAX_RETRIES = 5
OLD_SKUS_DIR = "src/oldskus"

def concurrent_sku_search(skus, proxies_file, search_function, link_key, max_workers=5):
    proxies = load_proxies(proxies_file)
    user_agent = UserAgent()
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_sku = {executor.submit(search_function, sku, proxies, user_agent): sku for sku in skus}

        for future in as_completed(future_to_sku):
            sku = future_to_sku[future]
            if not state_manager.is_running:
                break
            try:
                link = future.result()
                results.append({'SKU': sku, link_key: link})
                print(f"[{'SUCCESS' if 'Not Found' not in link else 'ERROR'}] Product {'found' if 'Not Found' not in link else 'not found'} for SKU: {sku}")
            except Exception as e:
                results.append({'SKU': sku, link_key: f"Error: {e}"})
                print(f"[ERROR] Failed search for SKU {sku} - Error: {e}")

    if state_manager.is_running:
        save_search_results(results, filename_base='search_results')
    state_manager.is_running = False
    return results

def search_walmart_by_sku(sku, proxies, user_agent):
    retries = 0
    timeout = 5
    page = 1

    while retries < MAX_RETRIES:
        if not state_manager.is_running:
            return "Process Stopped"

        proxy, headers = get_proxy_and_headers(proxies, user_agent)
        search_url = f"https://www.walmart.com/search/?query={sku}&page={page}"

        try:
            response = requests.get(search_url, headers=headers, proxies=proxy, timeout=timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                product_links = soup.select(
                    'a[class*="product-title-link"], '
                    'a[class*="search-result-product-title"], '
                    'a[data-automation-id*="product-title"], '
                    'a[href*="ip/"]'
                )
                for link in product_links:
                    product_url = "https://www.walmart.com" + link['href']
                    if sku in product_url or sku in soup.get_text():
                        # print(f"[SUCCESS] Walmart Product found for SKU: {sku}")
                        return product_url
                if soup.select_one('button[data-automation-id="pagination-next"]'):
                    page += 1
                else:
                    return "Not Found"
            else:
                retries += 1
        except requests.RequestException as e:
            print(f"[ERROR] {e}")
            retries += 1
    return "Not Found"

def search_skus_on_walmart(skus, proxies_file):
    proxies = load_proxies(proxies_file)
    user_agent = UserAgent()
    results = []

    for sku in skus:
        if not state_manager.is_running:
            break
        walmart_link = search_walmart_by_sku(sku, proxies, user_agent)
        results.append({'SKU': sku, 'Walmart Link': walmart_link})
        print(f"[INFO] Search result for SKU {sku}: {walmart_link}")

    if state_manager.is_running:
        save_search_results(results, filename_base='search_results')
    state_manager.is_running = False
    print("[INFO] Walmart search completed.")

def search_amazon_by_sku(sku, proxies, user_agent):
    retries = 0

    while retries < MAX_RETRIES:
        if not state_manager.is_running:
            return "Process Stopped"

        proxy, headers = get_proxy_and_headers(proxies, user_agent)
        search_url = f"https://www.amazon.com/s?k={sku}"

        try:
            response = requests.get(search_url, headers=headers, proxies=proxy, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                product_link = soup.select_one('a.a-link-normal.a-text-normal, a.a-link-normal.s-no-outline')
                if product_link and is_valid_amazon_link("https://www.amazon.com" + product_link['href']):
                    return "https://www.amazon.com" + product_link['href']
            else:
                retries += 1
        except requests.RequestException as e:
            print(f"[ERROR] {e}")
            retries += 1
    return "Not Found"

def walmart_search_concurrently(skus, proxies_file, max_workers=5):
    return concurrent_sku_search(skus, proxies_file, search_walmart_by_sku, link_key='Walmart Link', max_workers=max_workers)

def amazon_search_concurrently(skus, proxies_file, max_workers=5):
    return concurrent_sku_search(skus, proxies_file, search_amazon_by_sku, link_key='Amazon Link', max_workers=max_workers)

def save_search_results(results, filename_base='search_results'):
    search_type = "Amazon" if "Amazon Link" in results[0] else "Walmart"
    filename = f'{filename_base}_{search_type.lower()}.csv'

    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['SKU', f'{search_type} Link'])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} Results saved to {filename}")
    move_and_rename_files(OLD_SKUS_DIR, filename)

def search_skus_on_amazon(skus=None, file_path=None, proxies_file="proxies.txt"):
    if skus is None and file_path is not None:
        with open(file_path, 'r') as file:
            skus = [line.strip() for line in file.readlines()]

    if skus is None:
        print("[ERROR] No SKUs provided for Amazon search.")
        return

    results = concurrent_sku_search(skus, proxies_file, search_amazon_by_sku, link_key='Amazon Link', max_workers=10)
    if state_manager.is_running:
        save_search_results(results, filename_base='search_results')
    print("[INFO] Amazon search completed.")

def get_search_results():
    try:
        files = [f for f in os.listdir(OLD_SKUS_DIR) if f.startswith("search_results")]
        if not files:
            print("Error: No search results file found.")
            return []

        latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(OLD_SKUS_DIR, f)))
        latest_file_path = os.path.join(OLD_SKUS_DIR, latest_file)

        with open(latest_file_path, mode='r', newline='', encoding='utf-8') as file:
            return [row for row in csv.DictReader(file)]

    except (ValueError, FileNotFoundError):
        print("Error: No search results file found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []