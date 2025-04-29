# ticket_count.py
from datetime import datetime, timedelta
from collections import defaultdict
import pytz, os, json, gspread, requests
from oauth2client.service_account import ServiceAccountCredentials
from config import ZENDESK_DOMAIN, GOOGLE_SHEET_KEY

def process_all_agents(target_date_kst):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds/google_creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(GOOGLE_SHEET_KEY).worksheet("4/29")

    base_dir = os.path.dirname(__file__)
    tag_map_path = os.path.join(base_dir, "tag_map.json")
    with open(tag_map_path, "r", encoding="utf-8") as f:
        tag_map = json.load(f)

    start_utc = target_date_kst.astimezone(pytz.utc)
    end_utc = (target_date_kst + timedelta(days=1)).astimezone(pytz.utc)
    start_str = start_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_str = end_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    agents = [
        {
            "name": "김수민",
            "email": "sumin.kim@wemadeplay.com",
            "token": "ARJOvGXJ9JnY4AZoWdTbQJglKcGDokdMDJurBTpv"
        },
        {
            "name": "황철호",
            "email": "cheolho.hwang@wemadeplay.com",
            "token": "7NS7GJ3fwRLxIMFd6SfE2edx1JWlhQj7wkbuEh3m"
        }
    ]

    for agent in agents:
        process_agent(agent["name"], agent["email"], agent["token"], tag_map, sheet, target_date_kst, start_str, end_str)

def process_agent(agent_name, agent_email, agent_token, tag_map, sheet, target_date_kst, start_str, end_str):
    ...