import os
import shutil
import requests
from bs4 import BeautifulSoup
import csv
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from fake_useragent import UserAgent
from colorama import Fore, Style, init
import state_manager
from backend.utils import load_proxies, is_valid_amazon_link, move_and_rename_files

init(autoreset=True)

MAX_RETRIES = 5
OLD_SKUS_DIR = "src/oldskus"
SRC_DIR = "src"

def search_walmart_by_sku(sku, proxies, user_agent):
    retries = 0
    max_retries = 5
    while retries < max_retries:
        if not state_manager.is_running:
            return "Process Stopped"
        proxy = random.choice(proxies)
        headers = {
            "User-Agent": user_agent.random,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        search_url = f"https://www.walmart.com/search/?query={sku}"
        try:
            response = requests.get(search_url, headers=headers, proxies=proxy, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                product_link = soup.select_one('a[class*="product-title-link"]')
                if product_link:
                    product_url = "https://www.walmart.com" + product_link['href']
                    product_title = product_link.get_text(strip=True)
                    print(f"[SUCCESS] Walmart Product found: {product_title} for SKU: {sku}")
                    return product_url
            retries += 1
        except requests.exceptions.RequestException:
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
    return results

def search_amazon_by_sku(sku, proxies, user_agent):
    retries = 0
    while retries < MAX_RETRIES:
        if not state_manager.is_running:
            return "Process Stopped"
        proxy = random.choice(proxies)
        headers = {
            "User-Agent": user_agent.random,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        search_url = f"https://www.amazon.com/s?k={sku}"
        try:
            response = requests.get(search_url, headers=headers, proxies=proxy, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                product_link = soup.select_one('a.a-link-normal.a-text-normal, a.a-link-normal.s-no-outline')
                if product_link and is_valid_amazon_link("https://www.amazon.com" + product_link['href']):
                    return "https://www.amazon.com" + product_link['href']
            retries += 1
        except requests.exceptions.RequestException:
            retries += 1
    return "Not Found"

def search_skus_concurrently(skus, proxies_file, max_workers=10):
    proxies = load_proxies(proxies_file)
    user_agent = UserAgent()
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_sku = {executor.submit(search_amazon_by_sku, sku, proxies, user_agent): sku for sku in skus}
        for future in as_completed(future_to_sku):
            sku = future_to_sku[future]
            if not state_manager.is_running:
                break
            try:
                amazon_link = future.result()
                results.append({'SKU': sku, 'Amazon Link': amazon_link})
                if "Not Found" not in amazon_link:
                    print(f"[SUCCESS] Product found for SKU: {sku}")
                else:
                    print(f"[ERROR] Product not found for SKU: {sku}")
            except Exception as e:
                results.append({'SKU': sku, 'Amazon Link': f"Error: {e}"})
                print(f"[ERROR] Failed search for SKU: {sku} - Error: {e}")
    return results

def search_skus_from_list(skus, proxies_file):
    results = search_skus_concurrently(skus, proxies_file)
    if state_manager.is_running:
        with open('amazon_links_from_skus.csv', mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['SKU', 'Amazon Link'])
            writer.writeheader()
            writer.writerows(results)
        print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} Search complete. Results saved to amazon_links_from_skus.csv")
        move_and_rename_files(OLD_SKUS_DIR)

def search_skus_from_file(file_path, proxies_file):
    with open(file_path, 'r') as file:
        skus = [line.strip() for line in file.readlines()]
    results = search_skus_concurrently(skus, proxies_file)
    if state_manager.is_running:
        with open('amazon_links_from_skus.csv', mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['SKU', 'Amazon Link'])
            writer.writeheader()
            writer.writerows(results)
        print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} Search complete. Results saved to amazon_links_from_skus.csv")
        move_and_rename_files(OLD_SKUS_DIR)

def get_search_results():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    oldskus_dir = os.path.join(base_dir, "oldskus")
    try:
        latest_file = max(
            [f for f in os.listdir(oldskus_dir) if f.startswith("amazon_links_from_skus")],
            key=lambda f: os.path.getmtime(os.path.join(oldskus_dir, f))
        )
        latest_file_path = os.path.join(oldskus_dir, latest_file)
        
        results = []
        with open(latest_file_path, mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                results.append({
                    'SKU': row.get('SKU', '').strip(),
                    'Amazon Link': row.get('Amazon Link', '').strip()
                })
        return results

    except (ValueError, FileNotFoundError):
        print("Error: No amazon_links_from_skus file found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []