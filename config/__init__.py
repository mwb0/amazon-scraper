# config.py

# Price check frequency (Set this value in hours to check the price)
CHECK_FREQUENCY = 5  # Check the price every 5 seconds for testing


# Price drop threshold (Set this value for the price drop trigger in dollars or percentage)
PRICE_DROP_THRESHOLD = 0 

PRICE_DROP_MODE = 'percentage'  # Set this value to 'percentage' or 'value' to trigger notifications based on percentage or value

# Log file path (This file will store all the price checks and notifications)
LOG_FILE_PATH = '.\data\price_log.csv'  # Default file path for logging, you can change it if desired

# User Agent to simulate a browser request (Usually fine as is, can be modified if needed)
CUSTOM_HEADERS = {
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.google.com/',
    # Add more headers here if needed
}

# user-agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/50.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/17.17134",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    # Add more user agents here if needed
]

# Query parameters for Amazon search (You can modify these parameters if needed)
AMAZON_QUERY_PARAMS = [
  "Kindle Fire"
]

# Product urls for Amazon search (You can modify these parameters if needed)
AMAZON_PRODUCT_URLS = [
  "https://www.amazon.com/Amazon_Fire_HD_10/dp/B0BHZT5S12?dib=eyJ2IjoiMSJ9.ot9Y0p2Weu9jijdSogBTGiJ-Nc3dLKWsmAVXxUUioNvPpH4S8lqfFYhd23Yy7-H1H16ezwEwdrC7sH2OFKAVSd5tLGhmqS7f1l8U1-XPPGeZ5oaD6aZaw1JFcLcac3GBE0KxPLXHcHI0T4GZrAhHYL8ngoI8C90Y0nAI4HobJg3rQ1GwGxQncpqPCy6CPtZsECc4Kyn_ldyMMAC7-Nd-bRJS85mOSWllG84raV1CIQLV8IiTaylEsEgvtXd85PSdHSPCLuOPE1OMb8W7LgY7ut0l9a83p9xJe0HsiA7nJhNUv6Rrds-HPhYLZU4j5BgetOsFdFMgWo7nGpoV5q5fMCViDngBCADjKEg4nvQIjno.xgJvHiRPQbP2cZ1-nH61qvGJVxNhWrXbFZ2PwrjZmPM&dib_tag=se&keywords=Kindle%2BFire&qid=1738356545&s=electronics&sr=1-4"
]