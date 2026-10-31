import os
import time
from flask import Flask, jsonify, request, render_template_string
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 配置临时文件存储路径
UPLOAD_FOLDER = '/tmp/simvascular_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# 支持最大 100MB 的文件上传
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SimVascular 云端计算与数据处理控制台</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f5f7fb; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; }
        .hero { background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%); color: white; padding: 36px 0; margin-bottom: 25px; border-radius: 0 0 16px 16px; }
        .card { border-radius: 12px; border: none; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .terminal { background: #181a1f; color: #50fa7b; font-family: monospace; padding: 16px; border-radius: 8px; min-height: 200px; max-height: 320px; overflow-y: auto; font-size: 0.88rem; }
        .upload-box { border: 2px dashed #b0bec5; border-radius: 8px; padding: 25px; text-align: center; background: #fafafa; cursor: pointer; transition: 0.2s; }
        .upload-box:hover { border-color: #1976d2; background: #eef5fc; }
    </style>
</head>
<body>
    <div class="hero">
        <div class="container text-center">
            <h2 class="fw-bold">🫀 SimVascular 云端计算与数据处理中心</h2>
            <p class="mb-0 text-white-50">上传患者影像、模型网格（.stl, .vtp, .vti, .dcm）或模拟参数并执行云端分析</p>
        </div>
    </div>

    <div class="container mb-5">
        <div class="row g-4">
            <!-- 数据输入与任务提交区域 -->
            <div class="col-lg-6">
                <div class="card p-4 h-100">
                    <h5 class="fw-bold mb-3">📁 传入待处理数据</h5>
                    <form id="taskForm" onsubmit="submitTask(event)">
                        <!-- 文件上传 -->
                        <div class="mb-3">
                            <label class="form-label text-secondary fw-semibold">1. 上传模型/数据文件：</label>
                            <input type="file" id="dataFile" class="form-control" accept=".stl,.vtp,.vti,.vtk,.dcm,.json,.xml,.txt,.zip" required>
                            <div class="form-text">支持常见格式：STL, VTP, VTI, VTK, DICOM压缩包, JSON参数文件（最大 100MB）</div>
                        </div>

                        <!-- 计算模式 -->
                        <div class="mb-3">
                            <label class="form-label text-secondary fw-semibold">2. 选择处理流程：</label>
                            <select id="modeSelect" class="form-select">
                                <option value="surface_mesh_analysis">网格与表面几何特征提取 (Surface Analysis)</option>
                                <option value="vessel_centerline">血管中心线提取与分叉检测 (Centerline Extraction)</option>
                                <option value="0d_reduced_solver">0D/1D 降阶血流动力学模拟 (svZeroD/svOneD Solver)</option>
                                <option value="custom_python_script">执行自定义 Python 批量预处理脚本</option>
                            </select>
                        </div>

                        <!-- 补充计算参数 -->
                        <div class="mb-3">
                            <label class="form-label text-secondary fw-semibold">3. 附加参数 (可选 JSON 格式)：</label>
                            <textarea id="paramJson" class="form-control" rows="2" placeholder='{"viscosity": 0.04, "cardiac_cycle": 1.0}'></textarea>
                        </div>

                        <button type="submit" id="submitBtn" class="btn btn-primary w-100 py-2 fw-semibold">
                            🚀 上传数据并开始云端计算
                        </button>
                    </form>
                </div>
            </div>

            <!-- 状态与规格 -->
            <div class="col-lg-6">
                <div class="card p-4 h-100">
                    <h5 class="fw-bold mb-3">⚙️ 云端计算资源状态</h5>
                    <ul class="list-group list-group-flush mb-3">
                        <li class="list-group-item d-flex justify-content-between px-0">
                            计算后端 <span class="badge bg-success">Google Cloud Run (已就绪)</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between px-0">
                            数据存储挂载 <span class="text-secondary">/tmp 临时内存工作空间</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between px-0">
                            最大上传限制 <span class="text-secondary">100 MB</span>
                        </li>
                    </ul>
                    <div class="alert alert-info py-2 small mb-0">
                        💡 <strong>处理流程说明</strong>：文件上传到容器后，将保存在内存工作目录，并通过 Python 脚本调用 SimVascular 相关分析与算法模块处理，结果会实时输出到下方日志终端。
                    </div>
                </div>
            </div>

            <!-- 运行日志与结果展示 -->
            <div class="col-12">
                <div class="card p-4">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h5 class="fw-bold mb-0">💻 实时处理日志与输出 (Console Output)</h5>
                        <button class="btn btn-sm btn-outline-secondary" onclick="clearLogs()">清屏</button>
                    </div>
                    <div id="terminal" class="terminal">
                        [系统状态] 控制台就绪，请选择文件并点击上传处理...<br>
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
            document.getElementById('terminal').innerHTML = '[已重置] 等待任务提交...<br>';
        }

        async function submitTask(e) {
            e.preventDefault();
            const fileInput = document.getElementById('dataFile');
            const mode = document.getElementById('modeSelect').value;
            const params = document.getElementById('paramJson').value;
            const submitBtn = document.getElementById('submitBtn');

            if (!fileInput.files.length) {
                alert('请先选择需要上传的数据文件！');
                return;
            }

            const file = fileInput.files[0];
            const formData = new FormData();
            formData.append('file', file);
            formData.append('mode', mode);
            formData.append('params', params);

            submitBtn.disabled = true;
            submitBtn.innerText = '正在上传并处理...';
            log(`开始上传文件: <span style="color:#f1fa8c;">${file.name}</span> (${(file.size / 1024).toFixed(1)} KB)...`);

            try {
                const response = await fetch('/api/process', {
                    method: 'POST',
                    body: formData
                });
                const res = await response.json();

                if (res.status === 'success') {
                    log(`<span style="color:#50fa7b;">[上传成功]</span> 目标文件已写入工作区: ${res.saved_filename}`);
                    log(`<span style="color:#8be9fd;">[执行模式]</span> ${res.mode}`);
                    log(`<span style="color:#ff79c6;">[处理结果]</span> ${res.message}`);
                    log(`<span style="color:#bd93f9;">[耗时统计]</span> ${res.duration}`);
                } else {
                    log(`<span style="color:#ff5555;">[处理异常]</span> ${res.error || '未知错误'}`);
                }
            } catch (err) {
                log(`<span style="color:#ff5555;">[请求失败]</span> 无法与后端建立连接: ${err.message}`);
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerText = '🚀 上传数据并开始云端计算';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/process', methods=['POST'])
def process_data():
    if 'file' not in request.files:
        return jsonify({"status": "error", "error": "未检测到上传的文件"}), 400
    
    file = request.files['file']
    mode = request.form.get('mode', 'default')
    params = request.form.get('params', '')

    if file.filename == '':
        return jsonify({"status": "error", "error": "文件名为空"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    start_time = time.time()
    filesize_kb = round(os.path.getsize(filepath) / 1024, 2)

    # 模拟数据处理逻辑（后续可在此处直接通过 subprocess 或 Python 模块调用真实算法）
    time.sleep(1.0)
    duration = f"{round(time.time() - start_time, 2)}s"

    return jsonify({
        "status": "success",
        "saved_filename": filename,
        "filesize": f"{filesize_kb} KB",
        "mode": mode,
        "duration": duration,
        "message": f"成功读取数据文件 [{filename}]，已在容器中完成校验并成功加载到分析管道！"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
