import schedule
import time
from src import Amazon
from config import CHECK_FREQUENCY, AMAZON_QUERY_PARAMS, AMAZON_PRODUCT_URLS

queries = AMAZON_QUERY_PARAMS

product_urls = AMAZON_PRODUCT_URLS

def scrap_amazon():
  Amazon.search(queries, max_pages=2) # max pages can be increased if needed. two pages are for testing purposes

def scrap_amazon_product():
  Amazon.get_product(product_urls)

def schedule_tasks():
  # Scrap Amazon specific product every {CHECK_FREQUENCY} seconds
  schedule.every(CHECK_FREQUENCY).seconds.do(scrap_amazon_product)
  
  # Scrap Amazon every day with the search queries
  schedule.every().day.do(scrap_amazon)
  
  # Additional scheduled tasks can be added here if needed
  

def main():
  schedule_tasks()
  while True:
    schedule.run_pending()
    time.sleep(1)

if __name__ == "__main__":
  main()
