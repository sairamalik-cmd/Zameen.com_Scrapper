"""
Zameen.com Web Scraper
Collects property listings from Islamabad, Pakistan
Author: ML Project - House Price Prediction
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
import os
from datetime import datetime

# ─── Configuration ────────────────────────────────────────────────────────────
BASE_URL = "https://www.zameen.com"
ISLAMABAD_URL = "https://www.zameen.com/homes/islamabad-2-1.html"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.zameen.com/",
}

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "../data/zameen_islamabad_raw.csv")


# ─── Helper Functions ─────────────────────────────────────────────────────────

def get_page(url, retries=3):
    """Fetch a URL with retry logic and polite delay."""
    for attempt in range(retries):
        try:
            time.sleep(random.uniform(2, 5))   # polite delay
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                return BeautifulSoup(resp.text, "html.parser")
            print(f"  [!] Status {resp.status_code} for {url}")
        except Exception as e:
            print(f"  [!] Attempt {attempt+1} failed: {e}")
    return None


def parse_price(text):
    """Normalise price strings to PKR (integer)."""
    if not text:
        return None
    text = text.replace(",", "").strip().upper()
    multipliers = {"CRORE": 1e7, "LAKH": 1e5, "ARAB": 1e9}
    for word, mult in multipliers.items():
        if word in text:
            num = re.findall(r"[\d.]+", text)
            return int(float(num[0]) * mult) if num else None
    nums = re.findall(r"[\d.]+", text)
    return int(float(nums[0])) if nums else None


def parse_area(text):
    """Convert area to square feet."""
    if not text:
        return None
    text = text.strip().upper()
    conversions = {"MARLA": 272.25, "KANAL": 4356, "SQ. FT.": 1, "SQ FT": 1}
    for unit, factor in conversions.items():
        if unit in text:
            nums = re.findall(r"[\d.]+", text)
            return round(float(nums[0]) * factor, 2) if nums else None
    nums = re.findall(r"[\d.]+", text)
    return float(nums[0]) if nums else None


def get_listing_urls(page_soup):
    """Extract individual listing URLs from a search page."""
    links = []
    # Filter to only include actual listing URLs from Zameen.com
    for a in page_soup.select("a[href*='/Property/']"):
        href = a.get("href", "")
        # Avoid social media share links that contain the property URL as a parameter
        if "facebook.com" in href or "twitter.com" in href or "google.com" in href or "pinterest.com" in href:
            continue
            
        full = href if href.startswith("http") else BASE_URL + href
        if full not in links and "zameen.com/Property/" in full:
            links.append(full)
    return links


def scrape_listing(url):
    """Scrape a single property listing page."""
    soup = get_page(url)
    if not soup:
        return None

    record = {"url": url, "city": "Islamabad"}

    # Price
    price_tag = soup.select_one("[class*='price']") or soup.select_one("[data-cy='listing-price']")
    record["price"] = parse_price(price_tag.get_text(strip=True)) if price_tag else None

    # Title / property type
    title_tag = soup.select_one("h1")
    title_text = title_tag.get_text(strip=True) if title_tag else ""
    record["title"] = title_text
    for ptype in ["House", "Apartment", "Plot", "Upper Portion", "Lower Portion", "Room", "Farm House"]:
        if ptype.lower() in title_text.lower():
            record["property_type"] = ptype
            break
    else:
        record["property_type"] = "House"

    # Location
    loc_tag = soup.select_one("[class*='location']") or soup.select_one("[data-cy='listing-location']")
    record["location"] = loc_tag.get_text(strip=True).split(",")[0] if loc_tag else None

    # Features (area, beds, baths)
    area_tag = soup.select_one("[class*='area']") or soup.find(string=re.compile(r'Marla|Kanal|sq\. ft', re.I))
    record["area_sqft"] = parse_area(area_tag.get_text(strip=True) if hasattr(area_tag, 'get_text') else str(area_tag))

    beds_tag = soup.find(string=re.compile(r'\d+\s+Bed', re.I))
    record["bedrooms"] = int(re.findall(r'\d+', str(beds_tag))[0]) if beds_tag else None

    baths_tag = soup.find(string=re.compile(r'\d+\s+Bath', re.I))
    record["bathrooms"] = int(re.findall(r'\d+', str(baths_tag))[0]) if baths_tag else None

    # Additional features from spec table
    spec_map = {}
    for row in soup.select("tr, [class*='feature'], [class*='amenity']"):
        text = row.get_text(separator="|").lower()
        for feat in ["parking", "servant quarter", "store room", "kitchen", "drawing room", "built in year"]:
            if feat in text:
                val = re.findall(r'\d+', text)
                spec_map[feat] = val[0] if val else "Yes"

    record["parking_spaces"]     = spec_map.get("parking", None)
    record["servant_quarters"]   = 1 if "servant quarter" in spec_map else 0
    record["store_rooms"]        = spec_map.get("store room", 0)
    record["kitchens"]           = spec_map.get("kitchen", 1)
    record["drawing_rooms"]      = spec_map.get("drawing room", 0)
    record["built_in_year"]      = spec_map.get("built in year", None)

    return record


def get_next_page_url(soup, current_page):
    """Return the URL for the next results page."""
    next_link = soup.select_one(f"a[href*='-{current_page + 1}.html']")
    if next_link:
        href = next_link.get("href", "")
        return href if href.startswith("http") else BASE_URL + href
    # Construct URL pattern
    new_url = re.sub(r'-(\d+)\.html', f'-{current_page + 1}.html', ISLAMABAD_URL)
    return new_url


# ─── Main Scraping Loop ───────────────────────────────────────────────────────

def run_scraper(max_pages=20, max_listings=400):
    """
    Main scraper entry point.
    Iterates through search result pages and scrapes individual listings.
    """
    all_records = []
    current_url = ISLAMABAD_URL
    page_num = 1

    print(f"[+] Starting Zameen.com scraper — target: {max_listings} listings")
    print(f"[+] City: Islamabad")
    print("-" * 60)

    while page_num <= max_pages and len(all_records) < max_listings:
        print(f"\n[→] Scraping results page {page_num}: {current_url}")
        page_soup = get_page(current_url)

        if not page_soup:
            print(f"[!] Could not load page {page_num}. Stopping.")
            break

        listing_urls = get_listing_urls(page_soup)
        print(f"    Found {len(listing_urls)} listings on this page")

        for i, listing_url in enumerate(listing_urls):
            if len(all_records) >= max_listings:
                break
            print(f"    [{len(all_records)+1}/{max_listings}] Scraping: {listing_url[:80]}...")
            record = scrape_listing(listing_url)
            if record and record.get("price"):
                all_records.append(record)
                print(f"           Price: PKR {record['price']:,}  |  Area: {record.get('area_sqft')} sqft  |  Beds: {record.get('bedrooms')}")

        # Navigate to next page
        current_url = get_next_page_url(page_soup, page_num)
        page_num += 1

    # Save results
    df = pd.DataFrame(all_records)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\n[✓] Scraping complete. {len(df)} listings saved to: {OUTPUT_PATH}")
    return df


if __name__ == "__main__":
    df = run_scraper(max_pages=20, max_listings=400)
    print(df.head())
    print(f"\nDataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
