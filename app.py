import os
import time
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

# 可视化 Web 控制台界面
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SimVascular 云端控制台</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
        .hero { background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%); color: white; padding: 40px 0; margin-bottom: 30px; border-radius: 0 0 16px 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .card { border-radius: 12px; border: none; box-shadow: 0 2px 8px rgba(0,0,0,0.06); transition: transform 0.2s; }
        .card:hover { transform: translateY(-2px); }
        .terminal { background: #1e1e1e; color: #4af626; font-family: monospace; padding: 15px; border-radius: 8px; min-height: 180px; max-height: 260px; overflow-y: auto; font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="hero">
        <div class="container text-center">
            <h1 class="display-6 fw-bold">🫀 SimVascular Cloud Console</h1>
            <p class="lead mb-0">基于 Google Cloud Run 的云端计算与模拟服务控制台</p>
            <span class="badge bg-success mt-2">服务运行正常 (Online)</span>
        </div>
    </div>

    <div class="container">
        <div class="row g-4">
            <!-- 模块 1：模拟求解器触发 -->
            <div class="col-md-6">
                <div class="card p-4 h-100">
                    <h5 class="fw-bold mb-3">⚡ 快速执行血管计算任务</h5>
                    <p class="text-muted">触发云端 Python/求解器后台脚本，测试模拟流程。</p>
                    <div class="mb-3">
                        <label class="form-label text-secondary small">选择分析模式：</label>
                        <select id="modeSelect" class="form-select">
                            <option value="0d_solver">0D 血管网络模拟 (svZeroDSolver)</option>
                            <option value="1d_solver">1D 脉管动力学计算 (svOneDSolver)</option>
                            <option value="mesh_check">网格与模型几何检查 (Geometry Verification)</option>
                        </select>
                    </div>
                    <button class="btn btn-primary w-100 py-2 fw-semibold" onclick="runSimulation()">
                        🚀 启动云端模拟计算
                    </button>
                </div>
            </div>

            <!-- 模块 2：服务环境与规格 -->
            <div class="col-md-6">
                <div class="card p-4 h-100">
                    <h5 class="fw-bold mb-3">📊 云端实例状态</h5>
                    <ul class="list-group list-group-flush">
                        <li class="list-group-item d-flex justify-content-between align-items-center px-0">
                            运行平台
                            <span class="badge bg-primary rounded-pill">Google Cloud Run (Serverless)</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center px-0">
                            部署区域
                            <span class="text-secondary">europe-west1 (比利时)</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center px-0">
                            容器监听端口
                            <span class="text-secondary">8080</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center px-0">
                            自动部署链路 (CI/CD)
                            <span class="badge bg-info text-dark rounded-pill">GitHub -> Cloud Build</span>
                        </li>
                    </ul>
                </div>
            </div>

            <!-- 模块 3：实时日志终端 -->
            <div class="col-12">
                <div class="card p-4">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h5 class="fw-bold mb-0">💻 实时运行日志 (Console Output)</h5>
                        <button class="btn btn-sm btn-outline-secondary" onclick="clearLogs()">清空日志</button>
                    </div>
                    <div id="terminal" class="terminal">
                        [系统就绪] SimVascular 云端控制台已加载完毕，等待任务触发...<br>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function log(msg) {
            const term = document.getElementById('terminal');
            const now = new Date().toLocaleTimeString();
            term.innerHTML += `[${now}] ${msg}<br>`;
            term.scrollTop = term.scrollHeight;
        }

        function clearLogs() {
            document.getElementById('terminal').innerHTML = '[已重置] 等待任务触发...<br>';
        }

        async function runSimulation() {
            const mode = document.getElementById('modeSelect').value;
            log(`正在向云端提交任务: ${mode}...`);
            
            try {
                const response = await fetch('/api/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mode: mode })
                });
                const data = await response.json();
                log(`<span style="color: #64b5f6;">云端返回:</span> ${data.message}`);
                log(`<span style="color: #81c784;">执行状态:</span> ${data.status} (耗时: ${data.duration})`);
            } catch (err) {
                log(`<span style="color: #e57373;">请求失败:</span> ${err.message}`);
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    # 渲染可视化控制台网页
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/run', methods=['POST'])
def run_task():
    data = request.get_json() or {}
    mode = data.get('mode', 'default')
    
    # 模拟云端处理耗时与响应
    time.sleep(0.5)
    
    return jsonify({
        "status": "success",
        "mode": mode,
        "duration": "0.52s",
        "message": f"任务 [{mode}] 已在 Cloud Run 容器实例中成功调度运行！"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
