import logging
import os

log_directory = 'logs'

# Configure the logger
logging.basicConfig(
  filename=os.path.join(log_directory, 'app.log'),  # Log file name
  filemode='a',        # Append mode
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
  level=logging.DEBUG  # Log level
)

# Create a logger object
logger = logging.getLogger('AmazonScraperLogger')

# Example usage
if __name__ == "__main__":
  logger.info('Logger is configured and ready to use.')