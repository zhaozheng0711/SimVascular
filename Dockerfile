# 使用支持 Python 或所需环境的基础镜像
FROM python:3.10-slim

# 安装 SimVascular 依赖或相关运行环境
WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt || true

# 假设您的应用入口是一个 Web 服务（例如 Flask / FastAPI），监听 8080 端口
ENV PORT=8080
EXPOSE 8080

CMD ["python", "app.py"]
