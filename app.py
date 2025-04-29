import subprocess
import os
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/run-script", methods=["POST"])
def run_script():
    try:
        # 현재 파일(app.py) 기준으로 main.py 경로를 지정
        script_path = os.path.join(os.path.dirname(__file__), "main.py")
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True,
            check=True
        )
        return jsonify({
            "message": "Script executed successfully.",
            "stdout": result.stdout
        })
    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": "Script execution failed",
            "stderr": e.stderr
        }), 500
    
print("✅ main.py가 Render 서버에서 실행되었습니다!")