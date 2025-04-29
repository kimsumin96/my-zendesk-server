import os
import json
import requests
import gspread
from datetime import datetime, timedelta
from collections import defaultdict
from oauth2client.service_account import ServiceAccountCredentials
import pytz
from config import ZENDESK_DOMAIN, GOOGLE_SHEET_KEY

def process_agent(agent_name, agent_email, agent_token, sheet, tag_map, target_date_kst):
    kst = pytz.timezone('Asia/Seoul')
    start_utc = target_date_kst.astimezone(pytz.utc)
    end_utc = (target_date_kst + timedelta(days=1)).astimezone(pytz.utc)
    start_str = start_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_str = end_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    query = (
        f'type:ticket status:solved assignee:"{agent_email}" '
        f'updated>={start_str} updated<{end_str}'
    )
    url = f"https://{ZENDESK_DOMAIN}/api/v2/search.json?query={query}"
    response = requests.get(url, auth=(f"{agent_email}/token", agent_token))
    tickets = response.json().get("results", [])

    print(f"\n✅ {agent_name} - 해결 티켓 수: {len(tickets)}")

    user_url = f"https://{ZENDESK_DOMAIN}/api/v2/users/me.json"
    user_resp = requests.get(user_url, auth=(f"{agent_email}/token", agent_token))
    my_user_id = user_resp.json()["user"]["id"]

    game_counts = defaultdict(int)

    for ticket in tickets:
        ticket_id = ticket["id"]
        ticket_tags = ticket.get("tags", [])
        ticket_games = [tag_map[tag] for tag in ticket_tags if tag in tag_map]

        if not ticket_games:
            print(f"⚠️ Unknown tags in ticket {ticket_id}: {ticket_tags}")
            continue

        game_name = ticket_games[0]

        comments_url = f"https://{ZENDESK_DOMAIN}/api/v2/tickets/{ticket_id}/comments.json"
        comments_resp = requests.get(comments_url, auth=(f"{agent_email}/token", agent_token))
        comments = comments_resp.json().get("comments", [])

        count_for_this_ticket = 1
        public_replies_today = 0
        for comment in comments:
            author_id = comment["author_id"]
            created_at = datetime.strptime(comment["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc).astimezone(kst)
            if author_id == my_user_id and comment.get("public", False):
                if created_at.date() == target_date_kst.date():
                    public_replies_today += 1

        if public_replies_today > 1:
            count_for_this_ticket += (public_replies_today - 1)

        game_counts[game_name] += count_for_this_ticket

    name_col_index = 3
    name_col = sheet.col_values(name_col_index)
    try:
        row_index = next(i + 1 for i, v in enumerate(name_col) if v.strip() == agent_name)
    except StopIteration:
        raise Exception(f"시트에 '{agent_name}' 이름이 없습니다.")

    base_col = 5
    game_order = ['애니팡1', '사천성', '애니팡2', '아쿠아', '상하이', '고포류', '애니팡3', '터치', '위베베', '팝타운', '애니팡4', '매치라이크', '머지', '광고']
    values = [[game_counts.get(game, 0)] for game in game_order]
    cell_range = sheet.range(row_index, base_col, row_index, base_col + len(game_order) - 1)

    for cell, value in zip(cell_range, [v[0] for v in values]):
        cell.value = value

    sheet.update_cells(cell_range)
    print(f"✅ {agent_name} - 시트 배치 업데이트 완료")

def run_all():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds/google_creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(GOOGLE_SHEET_KEY).worksheet("4/29")

    base_dir = os.path.dirname(__file__)
    tag_map_path = os.path.join(base_dir, "tag_map.json")
    with open(tag_map_path, "r", encoding="utf-8") as f:
        tag_map = json.load(f)

    kst = pytz.timezone('Asia/Seoul')
    target_date_kst = datetime(2025, 4, 29, tzinfo=kst)

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
        process_agent(agent["name"], agent["email"], agent["token"], sheet, tag_map, target_date_kst)