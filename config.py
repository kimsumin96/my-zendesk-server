from dotenv import load_dotenv
import os

load_dotenv()

ZENDESK_EMAIL = os.getenv("ZENDESK_EMAIL")
ZENDESK_TOKEN = os.getenv("ZENDESK_TOKEN")
ZENDESK_DOMAIN = os.getenv("ZENDESK_DOMAIN")
GOOGLE_SHEET_KEY = os.getenv("GOOGLE_SHEET_KEY")

