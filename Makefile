# 变量定义
PYTHON = ./venv/bin/python3
UVICORN = ./venv/bin/uvicorn
FRONTEND_DIR = ./frontend
BACKEND_HOST = 0.0.0.0
BACKEND_PORT = 8000
FRONTEND_PORT = 5174

.PHONY: all help install backend frontend stop clean status run-main

# 默认显示帮助
help:
	@echo "SmartBite 管理命令:"
	@echo "  make install    - 安装后端和前端依赖"
	@echo "  make start      - 启动后端和客户 API (并行)"
	@echo "  make run-main   - 启动主服务 (端口 8000, 含 UI + API)"
	@echo "  make backend    - 启动 FastAPI 后端"
	@echo "  make frontend   - 启动 Vite 前端开发服务器"
	@echo "  make stop       - 停止所有服务"
	@echo "  make status     - 查看服务运行状态"
	@echo "  make clean      - 清理 Python 缓存"

# 安装依赖
install:
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt
	cd $(FRONTEND_DIR) && npm install

# 构建前端 UI
build-ui:
	@echo "构建前端..."
	cd $(FRONTEND_DIR) && npm run build
	@echo "前端构建完成，输出到 frontend/dist/"

# 启动 Customer 后端 (端口 8001)
backend-customer:
	@echo "正在启动 Customer 后端服务 (端口 8001)..."
	$(UVICORN) app.run_customer:app_customer --host $(BACKEND_HOST) --port 8001 --reload

# 启动主服务 (端口 8000) - 先构建 UI
run-main: build-ui
	@echo "正在启动主服务 (端口 8000, UI + API)..."
	$(UVICORN) app.run_staff:app_staff --host $(BACKEND_HOST) --port 8000 --reload

# 启动前端 (增加 --host 以支持 AWS 访问)
frontend:
	@echo "正在启动前端服务..."
	cd $(FRONTEND_DIR) && npm run dev -- --host 0.0.0.0 --port $(FRONTEND_PORT)

# 并行启动 (使用 -j2 参数)
start:
	@make -j2 run-main backend-customer

# 向后兼容的 backend 命令 (默认启动主服务)
backend: run-main

# 停止服务 (使用你之前掌握的 pkill 灭火法)
stop:
	@echo "正在停止 Uvicorn 和 Node 进程..."
	-pkill -u coder uvicorn
	-pkill -u coder node
	@echo "服务已停止。"

# 查看状态
status:
	@echo "--- 后端状态 ---"
	-lsof -i :$(BACKEND_PORT)
	@echo "--- 前端状态 ---"
	-lsof -i :$(FRONTEND_PORT)

# 清理
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache
