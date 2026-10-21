import logging
import time
import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("TempMailClient")

class TempMailClient:
    
    def __init__(self):
        self.base_url = "https://tempmails.uk/"
        self.session = requests.Session()
        self.csrf_token = None
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        })

    def initialize_session(self) -> bool:
        try:
            logger.info("Initializing session and connecting to %s...", self.base_url)
            response = self.session.get(self.base_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            meta_tag = soup.find('meta', attrs={'name': 'csrf-token'})

            if not meta_tag or not meta_tag.get('content'):
                logger.error("Failed to locate CSRF token meta tag on the page.")
                return False

            self.csrf_token = meta_tag['content']
            logger.info("Successfully acquired CSRF token: %s...", self.csrf_token[:10])
            return True

        except requests.exceptions.RequestException as e:
            logger.error("Network error during session initialization: %s", e)
            return False

    def get_messages(self, captcha_response: str = "") -> dict:
        if not self.csrf_token:
            logger.warning("CSRF token missing. Attempting to initialize session first...")
            if not self.initialize_session():
                return {}

        endpoint = f"{self.base_url}get_messages"
        
        headers = {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': self.csrf_token,
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': self.base_url
        }

        payload = {
            "_token": self.csrf_token,
            "captcha": captcha_response
        }

        try:
            logger.info("Polling inbox for messages...")
            response = self.session.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            if data.get("status"):
                mailbox = data.get("mailbox")
                messages = data.get("messages", [])
                logger.info("Active Mailbox: %s | Messages Found: %d", mailbox, len(messages))
                return data
            else:
                logger.warning("Server responded with a negative status.")
                return data

        except requests.exceptions.HTTPError as e:
            logger.error("HTTP error occurred while fetching messages: %s", e)
            if e.response is not None:
                logger.error("Response body: %s", e.response.text)
        except requests.exceptions.RequestException as e:
            logger.error("Connection error occurred: %s", e)
        except ValueError:
            logger.error("Failed to parse response JSON from server.")
            
        return {}


if __name__ == "__main__":
    logger.info("Starting TempMail automation runner...")
    
    client = TempMailClient()
    inbox_data = client.get_messages()

    if not inbox_data or not inbox_data.get("status"):
        logger.error("Failed to generate a temporary email address.")
        exit(1)

    email_address = inbox_data.get("mailbox")

    print(f"Your Temporary Email Address: {email_address}")
    print("Waiting for incoming messages... (Press Ctrl+C to exit)\n")

    try:
        while True:
            time.sleep(5)
            logger.info("Checking inbox for new messages...")
            
            inbox_data = client.get_messages()
            messages = inbox_data.get("messages", [])

            if messages:
                print(f"Success! Found {len(messages)} message(s) in inbox:")
                
                for i, msg in enumerate(messages, 1):
                    print(f"\n--- Message [{i}] ---")
                    print(f"From    : {msg.get('from')} <{msg.get('from_email')}>")
                    print(f"Subject : {msg.get('subject')}")
                    print(f"Date    : {msg.get('receivedAt')}")
                    print(f"Seen    : {msg.get('is_seen')}")
                    print(f"\nContent:\n{msg.get('content')}")
                
                print("\n" + "=" * 60)
                break
            else:
                logger.info("Inbox is still empty. Checking again in 5 seconds...")

    except KeyboardInterrupt:
        logger.info("Stopped by user.")
