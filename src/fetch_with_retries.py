import requests
import time
import random
from datetime import datetime, timedelta
from requests.exceptions import ConnectionError, Timeout, RequestException, HTTPError
from logs import logger
from config import USER_AGENTS

# Dictionary to track banned User-Agents and the time they were banned
BANNED_USER_AGENTS = {}

# User-Agent Ban duration (e.g., 5 minutes)
BAN_DURATION = timedelta(minutes=5)

# List of possible User-Agent headers
USER_AGENTS = USER_AGENTS

def fetch_with_retries(url, headers=None, max_retries=3, backoff_factor=5, timeout=10):
    """
    Fetch a URL with retries.

    Parameters:
    - url: URL to fetch
    - max_retries: Maximum number of retries
    - backoff_factor: Seconds to wait between retries (exponential backoff)
    - timeout: Timeout for each request
    
    Returns:
    - Response content
    """
    
    previous_user_agent = None  # Track the previous User-Agent to avoid repetition
    
    for attempt in range(max_retries):
        try:
            # If no headers are provided, use an empty dict
            if headers is None:
                headers = {}
              
            # Select a random User-Agent that is not banned or previously used
            available_agents = [agent for agent in USER_AGENTS if agent != previous_user_agent and not is_banned(agent)]
            if not available_agents:
                logger.error("All User-Agents have been banned. Cannot proceed.")
                return None
            
            user_agent = random.choice(available_agents)
            headers["User-Agent"] = user_agent
            
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status() # Raise error for HTTP failures
            
            # Update the previous User-Agent for the next attempt
            previous_user_agent = user_agent
            
            logger.info(f"Successfully fetched {url}")
            print(f"Successfully fetched {url}")
            return response.text # Return response content
          
        except Timeout:
            logger.warning(f"Timeout on attempt {attempt + 1}. Retrying in {backoff_factor * (attempt + 1)} sec...")
        except HTTPError as e:
            if response.status_code == 503:
                logger.warning(f"503 Service Unavailable on attempt {attempt + 1}. Retrying in {backoff_factor * (attempt + 1)} sec...")
                # Mark this User-Agent as banned temporarily
                ban_user_agent(user_agent)
            else:
                logger.error(f"HTTP error {e.response.status_code}. Not retrying.")
                break  # Exit on other HTTP errors
        except (ConnectionError, RequestException) as e:
            logger.warning(f"Request failed: {e}. Retrying in {backoff_factor * (attempt + 1)} sec...")
        
        time.sleep(backoff_factor * (attempt + 1))  # Exponential backoff
    
    logger.error(f"Failed to fetch URL: {url}. Max retries exceeded.")
    return None

def is_banned(user_agent):
    """Check if the User-Agent is banned or can be retried."""
    if user_agent in BANNED_USER_AGENTS:
        ban_time = BANNED_USER_AGENTS[user_agent]
        if datetime.now() - ban_time >= BAN_DURATION:
            # If enough time has passed, remove from banned list and allow retry
            logger.info(f"User-Agent {user_agent} can be retried after ban duration.")
            del BANNED_USER_AGENTS[user_agent]
            return False
        else:
            logger.warning(f"User-Agent {user_agent} is still banned. Try later.")
            return True
    return False

def ban_user_agent(user_agent):
    """Ban a User-Agent temporarily and record the ban time."""
    logger.warning(f"Banning User-Agent {user_agent} due to 503 error.")
    BANNED_USER_AGENTS[user_agent] = datetime.now()