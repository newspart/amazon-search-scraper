from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import sys
import argparse
import json
import re
import csv
import os
from urllib.parse import quote


class CustomUCWebDriver(uc.Chrome):
    def post(self, url, data, headers):
        headers_js = json.dumps(headers)  # Convert headers to JSON string for safe injection
        data_js = json.dumps(data)  # Convert data to JSON string for safe injection
        script = f"""
            return fetch("{url}", {{
                method: "POST",
                headers: {headers_js},
                body: JSON.stringify({data_js})
            }})
            .then(response => response.text())
            .catch(error => 'Error: ' + error.message);
        """
        return self.execute_script(script)


def get_csrf_token(driver):
    try:
        print("Waiting for data-toaster-csrftoken element...")
        toaster_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-toaster-csrftoken]"))
        )
        csrf_token = toaster_element.get_attribute("data-toaster-csrftoken")
        if csrf_token:
            print(f"Found data-toaster-csrftoken: {csrf_token}")
            return csrf_token
        else:
            print("data-toaster-csrftoken attribute is empty.")
        return None
    except Exception as e:
        print(f"Error retrieving CSRF token: {e}")
        return None


def set_amazon_country(driver, country_code):
    try:
        csrf_token = get_csrf_token(driver)
        payload = {
            "locationType": "COUNTRY",
            "district": country_code,
            "countryCode": country_code,
            "deviceType": "web",
            "storeContext": "generic",
            "pageType": "Search",
            "actionSource": "glow"
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": driver.execute_script("return navigator.userAgent")
        }
        if csrf_token:
            headers["anti-csrftoken-a2z"] = csrf_token
        post_url = f"https://www.amazon.com/portal-migration/hz/glow/address-change?actionSource=glow"
        response_data = driver.post(post_url, payload, headers)
        print(f"Sent POST request to set country to {country_code}")
        print(f"POST response: {response_data}")
        time.sleep(1)
    except Exception as e:
        print(f"Failed to set country via POST request: {e}")


def scrape_amazon(search_url, country_code, output_file=None):
    driver = None
    items = []  # Store items for output
    print(f"Search URL: {search_url}")

    try:
        print("Setting up stealth Chrome driver...")
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        try:
            driver = CustomUCWebDriver(options=chrome_options)
            print("Driver initialized successfully.")
        except Exception as e:
            print(f"Failed to initialize driver: {e}")
            print("Check if Chrome/Chromium is installed (`sudo apt install chromium-browser`) and up to date.")
            return

        # Set the country via POST request
        print(f"Setting country to {country_code}...")
        driver.get(search_url)  # Load search link to get CSRF token and set country
        set_amazon_country(driver, country_code)
        driver.get(search_url)

        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-component-type='s-search-result']"))
            )
            print("Page loaded successfully.")
        except Exception as e:
            print(f"Cant detect search-result: {e}")
            return

        print("Scraping goods: names and prices...")
        time.sleep(5)
        try:
            list_items = driver.find_elements(By.CSS_SELECTOR, "[role='listitem']")
        except Exception as e:
            print(f"Error finding list items: {e}")
            print("Amazon might’ve changed their HTML. Check the page structure.")
            return

        if not list_items:
            print("No list items found with role='listitem'. Check the page structure.")
            return

        print("\nGoods Names and Prices:")
        for i, item in enumerate(list_items):
            try:
                name_element = item.find_element(By.CLASS_NAME, "a-size-medium.a-spacing-none.a-color-base.a-text-normal")
                name = name_element.text.strip()
            except Exception:
                continue
            try:
                price_container = item.find_element(By.CLASS_NAME, "a-price")
                price = price_container.text.partition('\n')[0]
            except Exception:
                continue

            # Store the item
            items.append({"name": name, "price": price})
            print(f"{name}: {price}")

        # Write to output file if specified
        if output_file:
            try:
                if output_file.endswith('.csv'):
                    with open(output_file, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=["name", "price"])
                        writer.writeheader()
                        writer.writerows(items)
                    print(f"Results saved to {output_file}")
                elif output_file.endswith('.txt'):
                    with open(output_file, 'w', encoding='utf-8') as f:
                        for item in items:
                            f.write(f"{item['name']}: {item['price']}\n")
                    print(f"Results saved to {output_file}")
                else:
                    print("Unsupported file extension. Use .csv or .txt")
            except Exception as e:
                print(f"Failed to write to output file: {e}")

    except Exception as e:
        print(f"Script went to hell: {e}")
    finally:
        if driver:
            driver.quit()
            print("Driver cleaned up.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Amazon search results with custom country code.")
    parser.add_argument("country_code", help="Country code for Amazon region (e.g., ID for Indonesia, FR for France)")
    parser.add_argument("--search-url", help="Amazon search URL (e.g., https://www.amazon.com/s?k=rtx+5070)")
    parser.add_argument("--search-text", help="Search text to query Amazon (e.g., 'rtx 5070')")
    parser.add_argument("-o", "--output", help="Output file for results (e.g., output.csv or output.txt)")
    args = parser.parse_args()

    # Determine search URL
    if args.search_url and args.search_text:
        print("Both --search-url and --search-text provided. Using --search-url.")
        search_url = args.search_url
    elif args.search_text:
        search_text = quote(args.search_text.replace(' ', '+'))
        search_url = f"https://www.amazon.com/s?k={search_text}"
    elif args.search_url:
        search_url = args.search_url
    else:
        print("Error: Either --search-url or --search-text must be provided.")
        sys.exit(1)

    scrape_amazon(search_url, args.country_code, args.output)