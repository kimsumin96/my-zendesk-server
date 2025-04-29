from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


@app.route('/run-script', methods=['POST'])
def run_script():
    try:
        # 실제로 실행할 Python 스크립트 경로
        result = subprocess.run(['python', 'C:/Users/user/sumin_s/sum/sum_s/sum2/main.py'], capture_output=True, text=True)
        
        # 스크립트 실행 결과를 반환
        return jsonify({
            'status': 'success',
            'output': result.stdout,
            'error': result.stderr
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)

    