# 1. 基础镜像
FROM python:3.11-slim

# 2. 设置工作目录
WORKDIR /app

# 3. 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# 4. 依赖安装
# 假设 backend 目录下有 requirements.txt 文件
# 如果使用 Poetry, 请相应修改以下命令
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 代码复制
# 将 backend 目录下的所有代码复制到容器的 /app 目录
# 由于 build context 是 ./backend, COPY . . 会复制 backend 目录的内容
COPY . .

# 6. 暴露端口
EXPOSE 8000

# 7. 默认启动命令
# 假设 FastAPI 应用实例在 app/main.py 中的 app 对象
# 如果您的应用入口点不同, 请相应修改
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]