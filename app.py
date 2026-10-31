import os
import subprocess
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "message": "SimVascular Cloud Run Web Interface is successfully running!",
        "note": "You can use this API endpoint to trigger SimVascular scripts."
    })

# 示例：通过 Web 请求在云端调用 SimVascular 命令或 Python 脚本
@app.route('/run-simulation', methods=['POST'])
def run_simulation():
    # 这里可以在后台调用 SimVascular 工具命令
    return jsonify({"message": "Simulation request received."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
