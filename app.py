from flask import Flask, request, jsonify
from ticket_count import process_all_agents
from datetime import datetime
import pytz

app = Flask(__name__)

@app.route("/update", methods=["POST"])
def update_ticket_counts():
    kst = pytz.timezone('Asia/Seoul')
    today_kst = datetime.now(kst).replace(hour=0, minute=0, second=0, microsecond=0)
    try:
        process_all_agents(today_kst)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)