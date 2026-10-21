# TempMail Emails

A lightweight, Python client that interfaces with tempmails.uk to programmatically generate temporary email addresses, fetch messages, and poll inboxes in real time.

Built with `requests` and `BeautifulSoup`, this script handles automated session generation, CSRF token extraction, custom headers, and continuous inbox monitoring.

---

## Features

- **Automated CSRF Extraction:** Scrapes the target web page on startup to extract and store the required Laravel CSRF token for secure requests.
- **Dynamic Session Management:** Maintains cookies and headers using `requests.Session()` across initialization and polling cycles.
- **Continuous Inbox Polling:** Automatically queries the inbox at regular intervals (every 5 seconds by default) and displays newly received messages in the terminal.
- **Detailed Message Parsing:** Extracts and prints the sender address, subject line, timestamp, read status, and full message content.
- **Structured Logging:** Clean, time-stamped console output using Python's built-in `logging` module for easy debugging and tracking.

---

## Prerequisites

Make sure you have Python 3.8+ installed along with the required third-party libraries:

```bash
pip install requests beautifulsoup4
