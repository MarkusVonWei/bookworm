.PHONY: help install run test lint format clean docker-up docker-down frontend-install frontend-dev frontend-build

help:
	@echo "可用命令:"
	@echo "  install         - 安装后端依赖"
	@echo "  run             - 启动后端服务"
	@echo "  test            - 运行测试"
	@echo "  lint            - 代码检查"
	@echo "  format          - 代码格式化"
	@echo "  clean           - 清理临时文件"
	@echo "  docker-up       - 启动Docker服务"
	@echo "  docker-down     - 停止Docker服务"
	@echo "  frontend-install - 安装前端依赖"
	@echo "  frontend-dev    - 启动前端开发服务器"
	@echo "  frontend-build  - 构建前端生产版本"

install:
	python3 -m venv venv
	source venv/bin/activate && pip install -r requirements.txt

run:
	source venv/bin/activate && python main.py

test:
	source venv/bin/activate && python tests/test_basic.py

lint:
	source venv/bin/activate && mypy src/

format:
	source venv/bin/activate && black src/ && isort src/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .mypy_cache .pytest_cache

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build