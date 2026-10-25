# Bookworm 部署指南

## 服务器信息

- **主机名**: book
- **IP**: 124.220.45.149
- **用户**: ubuntu
- **部署路径**: ~/workspace/bookshelf

## 同步脚本

使用 `sync_to_server.sh` 同步后端代码到服务器：

```bash
cd /Users/marvin/workspace/life_project/bookworm
./sync_to_server.sh
```

脚本会自动：
1. 检查 SSH 连接
2. 同步 `src/`、`config/`、`requirements.txt`、`main.py` 等文件
3. 排除 `__pycache__`、`venv/`、`data/uploads/` 等临时文件

## 部署步骤

### 1. 同步代码
```bash
./sync_to_server.sh
```

### 2. SSH 到服务器
```bash
ssh book
cd ~/workspace/bookshelf
```

### 3. 安装依赖
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 配置环境变量
```bash
# 编辑 .env 文件
nano .env

# 主要配置项：
# - MIMO_API_KEY: MiMo API 密钥
# - MIMO_API_BASE: API 地址
# - NEO4J_URI: Neo4j 数据库地址（如需使用）
```

### 5. 启动服务

#### 方式一：直接运行
```bash
python main.py
```

#### 方式二：使用 Docker
```bash
docker-compose up -d
```

#### 方式三：使用 Makefile
```bash
make run
```

### 6. 验证服务
```bash
# 检查服务是否启动
curl http://localhost:8000/health

# 或者
curl http://124.220.45.149:8000/health
```

## 安全配置

### 限流配置
已实现 API 限流，配置在 `src/bookworm/api/rate_limit.py`：
- 普通 API：100 次/10 秒
- 识别/添加书籍 API：10 次/60 秒

### 书籍数量限制
每个用户最多 60 本书，配置在 `src/bookworm/bookshelf/service.py`。

## 防火墙配置

如需外部访问，确保服务器防火墙开放 8000 端口：

```bash
# Ubuntu/Debian
sudo ufw allow 8000/tcp

# 或使用 iptables
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
```

## Nginx 反向代理（可选）

如果需要使用域名或 HTTPS，可以配置 Nginx 反向代理：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件
    location /data {
        alias /home/ubuntu/workspace/bookshelf/data;
    }
}
```

## 日志查看

```bash
# 查看应用日志
tail -f ~/workspace/bookshelf/logs/app.log

# 查看 Docker 日志
docker-compose logs -f
```

## 故障排除

### 1. 端口被占用
```bash
# 查找占用 8000 端口的进程
lsof -i :8000

# 杀掉进程
kill -9 <PID>
```

### 2. 数据库错误
```bash
# 检查数据库文件
ls -la ~/workspace/bookshelf/data/bookshelf.db

# 如需重建数据库
rm ~/workspace/bookshelf/data/bookshelf.db
python main.py  # 会自动创建新数据库
```

### 3. 依赖安装失败
```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 快速部署命令

```bash
# 一键部署（同步 + 重启服务）
ssh book "cd ~/workspace/bookshelf && pkill -f 'python main.py' || true && source venv/bin/activate && nohup python main.py > logs/app.log 2>&1 &"
```
