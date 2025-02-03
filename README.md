# Amazon Kindle Fire Price Drop Notifier

This project monitors the price of the Kindle Fire on Amazon and sends an automated notification when the price drops by a specified threshold.

## How the Application Works

Here's the workflow:

### 1. Periodic Price Checks
The script runs at configurable intervals (default: every 6 hours) using a scheduler. Each cycle:

- Fetches product pages using HTTP requests with custom headers to mimic browser behavior
- Parses HTML content with BeautifulSoup to extract pricing data
- Handles Amazon's anti-scraping measures through request retries and user-agent rotation

### 2. Price Comparison
- Compares current price with historical data stored in ```price_log.csv```
- Triggers notifications if price drop exceeds the configured threshold

### 3. Notification
- Desktop alerts via Tkinter

### 4. Data Management
Maintains two types of records:
- Persistent CSV logs in ```data/price_log.csv```
- Runtime operation logs in ```logs/app.log```


## Prerequisites
- **Python 3.9 or later**
- **Miniconda (Optional, recommended for environment management)**
- **Google Chrome** (For Selenium-based scraping, if needed)

## Installation & Setup

### 1. Clone the Repository
```sh
 git clone https://github.com/mwb0/amazon-scraper.git
 cd amazon-scraper
```

### 2. Set Up a Virtual Environment
Using Miniconda:
```sh
 conda create --name amazon-scraper python=3.9
 conda activate amazon-scraper
```
Using venv:
```sh
 python -m venv venv
 source venv/bin/activate  # On macOS/Linux
 venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies
```sh
 pip install -r requirements.txt
```

### 4. Configure `config.py`
Edit the `config.py` file and set up:
- `AMAZON_PRODUCT_URLS`: The Amazon product page URLs.
- `AMAZON_QUERY_PARAMS`: The Queries for fetching on Amazon.com.
- `CUSTOM_HEADERS`: The custom header for fetching data.
- `LOG_FILE_PATH`: The path of the CSV file.
- `USER_AGENT`: Your browser's user-agent string.
- `PRICE_DROP_MODE`: 'percentage' or 'value'.
- `PRICE_DROP_THRESHOLD`: Set the price drop limit. It's `0` now for testing.
- `CHECK_FREQUENCY`: Frequency of price checks (in seconds).

### 5. Run the Script
```sh
 # Regular execution
 python main.py
```

## Challenges & Solutions

### Anti-Scraping Measures
Challenge: Blocked requests due to missing headers or bot detection
Solution:
 - Rotating user agents from common browsers
 - Implemented request headers mimicking browser behavior
 - Added delay CHECK_FREQUENCY seconds between requests
 - Added exponential backoff when 503 error occurred (5 seconds, 10 secs, 15 secs, ... by default)

## Additional Features
### 1. Multi-Product Support
 - Monitor multiple products according to a query list per day (you can change the period)
 - Monitor multiple Kindle models simultaneously through URL list configuration
### 2. Intelligent Retry Mechanism
 - 3 automatic retries for failed requests
 - Exponential backoff between attempts
### 3. Historical Price Tracking
CSV logging with pandas for easy data analysis
### 4. Cross-Platform Desktop Alerts
Tkinter-based notifications that work on Windows, macOS, and Linux

## File Structure
```
amazon-scraper/
│-- config/                    # Configuration settings
│   ├── __init__.py            # Stores user-defined settings
│-- logs/                      # Stores log files
|-- |── __init__.py            # Basic config for logging package
│   ├── app.log                # Log file for monitoring script activity
│-- data/                      # Stores scraped data
│   ├── price_log.csv          # CSV file logging price history
│-- src/                       # Source code directory
|-- |── __init__.py            # Imports scrapers
│   ├── amazon_scraper.py      # Main web scraping logic
│   ├── fetch_with_retries.py  # Handles retry mechanism for requests
│   ├── notification.py        # Manages notifications
│-- main.py                    # Entry point to run the script
│-- requirements.txt           # Required dependencies
│-- README.md                  # Project documentation
│-- .gitignore                 # Git ignore file to exclude unnecessary files
│-- venv/                      # Virtual environment (if used)
```

## Dependencies
These are installed via `requirements.txt`:
- `beautifulsoup4` (For web scraping)
- `requests` (For making HTTP requests)
- `pandas` (For data handling)
- `tkinter` (For notifications)
- `logging` (For logging events)