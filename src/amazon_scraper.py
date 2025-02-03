from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, unquote, urlparse, parse_qs
import pandas as pd
import time
from datetime import datetime
from typing import List, Optional, Union, Dict, Set
from config import CUSTOM_HEADERS, PRICE_DROP_THRESHOLD, LOG_FILE_PATH, CHECK_FREQUENCY, PRICE_DROP_MODE 
from .notification import display_notification
from .fetch_with_retries import fetch_with_retries
from logs import logging

PRICE_DROP_THRESHOLD = float(PRICE_DROP_THRESHOLD)

def extract_asin(url):
    """Extract ASIN from Amazon URLs (direct or tracked)."""
    # Decode URL-encoded characters
    decoded_url = unquote(url)
    
    # Case 1: ASIN in the URL path (e.g., /dp/B0XXXXXX)
    asin_pattern = r"/dp/([A-Z0-9]{10})|/gp/product/([A-Z0-9]{10})"
    match = re.search(asin_pattern, decoded_url)
    if match:
        asin = (match.group(1) or match.group(2)).upper()
        return asin
    
    # Case 2: ASIN in query parameters (e.g., pd_rd_i=B0XXXXXX)
    parsed_url = urlparse(decoded_url)
    query_params = parse_qs(parsed_url.query)
    
    # Check common ASIN-carrying parameters
    asin_params = ["pd_rd_i", "asin", "product_id"]
    for param in asin_params:
        if param in query_params:
            asin_candidate = query_params[param][0]
            if len(asin_candidate) == 10 and asin_candidate.isalnum():
                return asin_candidate.upper()  # ASINs are uppercase
    
    return None

def load_previous_price(asin=None):
    """Load the previous price data from the log file."""
    try:
        df = pd.read_csv(LOG_FILE_PATH)
        # Ensure timestamp is in datetime format
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        # Sort by timestamp (most recent first)
        df_sorted = df.sort_values(by='timestamp', ascending=False)
        # Drop duplicates based on the URL, keeping the most recent entry
        df_final = df_sorted.drop_duplicates(subset='asin', keep='first')
        # Set the 'url' column as the index
        df_final.set_index('asin', inplace=True)
        
        # If a specific URL is provided, return its data
        if asin is not None:
            # Check if the URL exists in the index
            if asin in df_final.index:
                return df_final.loc[asin, 'price']  # Returns a DataFrame with the URL's data
            else:
                return None
          
        return df_final
    except FileNotFoundError:
        return None

def write_csv(data):
  try:
    df_new = pd.DataFrame(data)
    df_new['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Set 'asin' as the index for new data
    df_new.set_index('asin', inplace=True)

    # Load existing data if file exists
    try:
        df_existing = pd.read_csv(LOG_FILE_PATH, index_col='asin')
        df = pd.concat([df_existing, df_new], axis=0, ignore_index=False)  # Append new data
    except FileNotFoundError:
        df = df_new  # If no file, create new one
    except Exception as e:
        logging.error(f"Error reading {LOG_FILE_PATH}: {e}")
        return

    # Save updated data
    df.to_csv(LOG_FILE_PATH)
    logging.info("CSV file updated successfully.")
  except Exception as e:
    logging.error(f"Error writing to CSV: {e}")

def get_product_info(url: str) -> Dict:
  """Extract product information from an Amazon product page."""
  response = fetch_with_retries(url, headers=CUSTOM_HEADERS)
  if response is None:
        logging.error(f'Error in getting webpage: {url}')
        return None

  soup = BeautifulSoup(response, 'lxml')

  title_element = soup.select_one('#productTitle')
  title = title_element.text.strip() if title_element else None

  price_element = soup.select_one('span.a-offscreen')
  price = None
  if price_element:
      try:
          price = float(price_element.text.strip().replace('$', '').replace(',', ''))
      except ValueError:
          logging.error(f"Error parsing price for {title}")
          return None

  rating_element = soup.select_one('#acrPopover')
  rating_text = rating_element.attrs.get('title') if rating_element else None
  rating = rating_text.replace('out of 5 stars', '') if rating_text else None

  image_element = soup.select_one('#landingImage')
  image = image_element.attrs.get('src') if image_element else None
  
  asin = extract_asin(url)
  
  # Error handling for display_notification
  if title is None or price is None or asin is None:
    logging.error(f'Error in getting product title: {url}')
    return None

  # Todo: check previous price and send notification if the price drops
  # Load previous product data
  previous_price = load_previous_price(asin)
  if previous_price is not None:
    if PRICE_DROP_MODE == 'value':
        if price <= previous_price - PRICE_DROP_THRESHOLD:
            logging.info("Price dropped by value threshold!")
            display_notification(title, previous_price, price, asin, url)
    elif PRICE_DROP_MODE == 'percentage':
        if price <= previous_price * (1 - PRICE_DROP_THRESHOLD / 100):
            logging.info("Price dropped by percentage threshold!")
            display_notification(title, previous_price, price, asin, url)
  
  return {
      'title': title,
      'price': price,
      'rating': rating,
      'image': image,
      'url': url,
      'asin': asin,
  }

def parse_listing(listing_url: str, max_pages: int, current_page: int = 1, visited_urls: Optional[Set[str]] = None, visited_listing_urls: Optional[Set[str]] = None) -> None:
  """
  Parse an Amazon listing page to extract product URLs.

  Parameters:
  - listing_url (str): The URL of the Amazon search results or listing page to parse.
  - max_pages (int): The maximum number of pages to scrape. Scraping stops once this number is reached.
  - current_page (int, optional): The current page number in the search results, defaults to 1.
  - visited_urls (Optional[Set[str]], optional): A set of URLs that have already been scraped, used to avoid revisiting the same product pages. Defaults to None.
  - visited_listing_urls (Optional[Set[str]], optional): A set of listing URLs that have been visited to avoid re-processing them. Defaults to None.

  Returns:
  - None: This function does not return any value. It collects product information and writes it to a CSV file.
  """
  if visited_urls is None:
      visited_urls = set()
  if visited_listing_urls is None:
      visited_listing_urls = set()
      
  if current_page > max_pages or listing_url in visited_listing_urls:
    logging.info("searching ended because of max pages or visited urls")
    return []
  
  visited_listing_urls.add(listing_url)
  
  # Fetch page content
  response = fetch_with_retries(listing_url, headers = CUSTOM_HEADERS)
  if response is None:
    logging.error(f'Error in getting webpage: {listing_url}')
    return []
  
  # Parse product links
  soup_search = BeautifulSoup(response, 'lxml')
  link_elements = soup_search.select('[data-cy="title-recipe"] > a.a-link-normal')
  page_data = []
  
  # Process product pages
  for link in link_elements:
        full_url = urljoin(listing_url, link.attrs.get('href'))
        if full_url not in visited_urls:
            visited_urls.add(full_url)
            logging.info(f'Scraping product from {full_url[:100]}', flush=True)
            
            # Get product info and store in memory temporarily
            product_info = get_product_info(full_url)
            if product_info:
                page_data.append(product_info)
            
            # Add a delay to prevent Amazon blocking
            time.sleep(CHECK_FREQUENCY)
  
  # write data to csv
  write_csv(page_data)
                
  next_page_el = soup_search.select_one('a.s-pagination-next:not(.s-pagination-disabled)')
  if next_page_el:
      next_page_url = next_page_el.attrs.get('href')
      next_page_url = urljoin(listing_url, next_page_url)
      if next_page_url != listing_url:
          logging.info(f'Scraping next page: {next_page_url}')
          parse_listing(
              next_page_url,
              max_pages,
              current_page + 1,
              visited_urls,
              visited_listing_urls
          )


class Amazon:

  @staticmethod
  def search(query:  Union[str, List[str]], max_pages: int = 50) -> None:
    data = []
  
    for item in query:
      parse_listing(f'https://www.amazon.com/s?k={item}', max_pages = max_pages)
  
    return data
  
  @staticmethod
  def get_product(urls: Union[str, List[str]]) -> Dict:
    data = []
  
    for item in urls:
      data.append(get_product_info(item))
    
    # write data to csv
    write_csv(data)
    