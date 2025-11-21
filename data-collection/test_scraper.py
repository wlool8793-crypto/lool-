"""Test script to debug scraper"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

base_url = "https://indiankanoon.org"
search_params = "doctypes:supremecourt fromdate:1-1-2023 todate:31-12-2023"
search_url = f"{base_url}/search/?formInput={quote(search_params)}&pagenum=0"

print(f"URL: {search_url}")

response = requests.get(search_url)
soup = BeautifulSoup(response.content, 'html.parser')

# Try finding results
results = soup.find_all('div', class_='result')
print(f"\nFound {len(results)} results with class_='result'")

if results:
    for i, result in enumerate(results[:3]):
        print(f"\n--- Result {i+1} ---")

        # Find title link
        title_tag = result.find('a', class_='result_title')
        if title_tag:
            print(f"Title (with class): {title_tag.get_text(strip=True)}")
            print(f"URL (with class): {title_tag.get('href', 'N/A')}")

        # Try without class
        title_div = result.find('div', class_='result_title')
        if title_div:
            link = title_div.find('a')
            if link:
                print(f"Title (div method): {link.get_text(strip=True)}")
                print(f"URL (div method): {link.get('href', 'N/A')}")
