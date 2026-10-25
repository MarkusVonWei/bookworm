# 同步和部署说明

## 服务器信息

| 项目 | 值 |
|------|-----|
| 主机名 | book |
| IP | 124.xxx.xxx.xxx |
| 用户 | ubuntu |
| 部署路径 | ~/workspace/bookshelf |
| SSH 配置 | `~/.ssh/config` 中的 `Host <server>` |

## 同步脚本

### 使用方法
```bash
cd /Users/marvin/workspace/life_project/bookworm
./sync_to_server.sh
```

### 同步内容
- `src/` - 后端源代码
- `config/` - 配置文件
- `requirements.txt` - Python 依赖
- `main.py` - 入口文件
- `Dockerfile` - Docker 配置
- `docker-compose.yml` - Docker Compose 配置
- `.env` - 环境变量
- `Makefile` - 构建脚本

### 排除内容
- `__pycache__/` - Python 缓存
- `venv/` - 虚拟环境
- `data/uploads/` - 上传文件
- `logs/` - 日志文件
- `.git/` - Git 仓库

## 远程服务器操作

### 1. SSH 连接
```bash
ssh <server>
```

### 2. 进入项目目录
```bash
cd ~/workspace/bookshelf
```

### 3. 安装依赖
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. 启动服务
```bash
# 直接运行
python main.py

# 或使用 Docker
docker-compose up -d

# 或使用 Makefile
make run
```

### 5. 验证服务
```bash
curl http://localhost:8000/health
```

## 安全功能

### 1. API 限流
- 普通 API: 100 次/10 秒
- 识别/添加 API: 10 次/60 秒
- 配置文件: `src/bookworm/api/rate_limit.py`

### 2. 书籍数量限制
- 每个用户最多 60 本书
- 配置文件: `src/bookworm/bookshelf/service.py`

## 文件同步状态

最新同步时间: $(date '+%Y-%m-%d %H:%M:%S')

已同步的文件:
- src/bookworm/bookshelf/service.py (8833 bytes)
- src/bookworm/bookshelf/api.py (15179 bytes)
- src/bookworm/api/rate_limit.py (3683 bytes)
- src/bookworm/api/app.py (2019 bytes)
- config/settings.py (2035 bytes)
- 其他文件...

## 常用命令

```bash
# 同步代码
./sync_to_server.sh

# SSH 到服务器
ssh <server>

# 查看服务状态
ssh <server> "curl -s http://localhost:8000/health"

# 重启服务
ssh <server> "cd ~/workspace/bookshelf && pkill -f 'python main.py'; nohup python main.py > logs/app.log 2>&1 &"

# 查看日志
ssh <server> "tail -f ~/workspace/bookshelf/logs/app.log"
```
