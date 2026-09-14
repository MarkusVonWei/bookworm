# AGENTS.md - 书虫LLM Agent 项目指南

## 项目概述

书虫LLM Agent是一个基于《如何阅读一本书》方法论的智能阅读助手，能够深度阅读书籍并构建知识图谱，回答用户问题。

## 核心功能

1. **书籍解析**：支持PDF、TXT、EPUB、Markdown等格式
2. **知识提取**：自动提取核心概念、观点和论证结构
3. **知识图谱**：构建概念间关系网络（Neo4j）
4. **智能问答**：结合向量检索和图谱查询（RAG）

## 技术栈

### 后端
- **LLM框架**：LlamaIndex
- **图数据库**：Neo4j
- **向量数据库**：ChromaDB
- **Web框架**：FastAPI
- **文档处理**：PyPDF2、ebooklib

### 前端
- **框架**：Vue 3
- **构建工具**：Vite
- **UI组件库**：Element Plus
- **HTTP客户端**：Axios
- **路由**：Vue Router

## 项目结构

```
bookworm/
├── src/bookworm/
│   ├── parsers/          # 书籍解析器
│   ├── extractors/       # 知识提取器
│   ├── graph/            # 知识图谱
│   ├── rag/              # 检索增强生成
│   └── api/              # Web API
├── frontend/             # 前端项目
│   ├── src/
│   │   ├── views/        # 页面组件
│   │   ├── api/          # API服务
│   │   └── router/       # 路由配置
│   ├── package.json      # 前端依赖
│   └── vite.config.js    # Vite配置
├── config/               # 配置文件
├── tests/                # 测试
├── examples/             # 示例
├── data/                 # 数据目录
├── logs/                 # 日志
├── main.py               # 主程序
├── requirements.txt      # 依赖
├── Dockerfile            # Docker配置
└── docker-compose.yml    # 多容器部署
```

## 常用命令

### 开发环境

```bash
# 安装依赖
make install
# 或
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# 启动服务
make run
# 或
python main.py

# 运行测试
make test
# 或
python tests/test_basic.py

# 代码检查
make lint

# 代码格式化
make format
```

### 前端开发

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

### Docker部署

```bash
# 启动服务
make docker-up
# 或
docker-compose up -d

# 停止服务
make docker-down
# 或
docker-compose down
```

## 环境配置

1. 复制环境变量示例：
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，配置：
   - `OPENAI_API_KEY`：OpenAI API密钥
   - `NEO4J_URI`：Neo4j数据库地址
   - `NEO4J_PASSWORD`：Neo4j密码

## API接口

### 主要端点

- `POST /upload`：上传并解析书籍
- `POST /question`：提问问题
- `GET /concepts`：获取所有概念
- `GET /concepts/{name}`：获取特定概念
- `GET /search?keyword=xxx`：搜索概念
- `GET /graph/{name}`：获取概念关系图
- `GET /health`：健康检查

### 使用示例

```bash
# 上传书籍
curl -X POST "http://localhost:8000/upload" -F "file=@book.pdf"

# 提问
curl -X POST "http://localhost:8000/question" \
  -H "Content-Type: application/json" \
  -d '{"question": "这本书的主要观点是什么？"}'
```

## 开发指南

### 添加新的解析器

1. 在 `src/bookworm/parsers/` 创建新解析器类
2. 继承 `BookParser` 基类
3. 实现 `parse()`、`get_metadata()`、`get_chapters()`、`get_full_text()` 方法
4. 在 `factory.py` 中注册新解析器

### 添加新的提取器

1. 在 `src/bookworm/extractors/` 创建新提取器类
2. 定义数据结构（dataclass）
3. 实现提取逻辑，使用LLM进行分析
4. 在 `__init__.py` 中导出

### 修改知识图谱

1. 节点类型定义在 `src/bookworm/graph/neo4j_client.py`
2. 关系类型定义在 `src/bookworm/extractors/relation_extractor.py`
3. 图构建逻辑在 `src/bookworm/graph/graph_builder.py`

## 测试

### 运行测试

```bash
# 运行基础测试
python tests/test_basic.py

# 运行示例
python examples/basic_usage.py
```

### 编写测试

1. 在 `tests/` 目录创建测试文件
2. 使用 `pytest` 框架
3. 测试数据放在 `data/books/` 目录

## 部署

### 本地部署

1. 安装依赖：`make install`
2. 配置环境变量：编辑 `.env`
3. 启动服务：`make run`
4. 访问：`http://localhost:8000`

### Docker部署

1. 配置环境变量
2. 启动服务：`make docker-up`
3. 访问：`http://localhost:8000`

## 故障排除

### 常见问题

1. **Neo4j连接失败**：检查Neo4j服务是否启动，配置是否正确
2. **OpenAI API错误**：检查API密钥是否有效
3. **依赖安装失败**：确保Python版本 >= 3.10

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# 查看Docker日志
docker-compose logs -f bookworm
```

## 核心经验教训

### 1. 日志配置必须先行

**问题**：项目初期没有配置日志，导致问题无法排查。

**解决方案**：
- 在项目启动阶段就配置好日志系统
- 使用 `config/logging.py` 统一管理日志配置
- 关键操作必须添加日志记录

```python
import logging
logger = logging.getLogger("bookworm")
logger.info("操作信息")
logger.error("错误信息", exc_info=True)
```

### 2. Neo4j认证方式

**问题**：Neo4j密码为空时，使用 `(username, password)` 元组认证会报错 `Unsupported authentication token`。

**解决方案**：
- 密码为空时不传入auth参数
- 在 `neo4j_client.py` 中判断密码是否为空

```python
if not self.password:
    self._driver = GraphDatabase.driver(self.uri)
else:
    self._driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
```

### 3. LlamaIndex OpenAI参数名

**问题**：LlamaIndex的OpenAI类使用 `api_base` 而不是 `base_url`。

**解决方案**：
- 查看类的签名确认参数名：`inspect.signature(OpenAI.__init__)`
- 使用正确的参数名 `api_base`

```python
from llama_index.llms.openai import OpenAI

llm = OpenAI(
    model="gpt-4",
    api_key="your_key",
    api_base="https://your-api-base/v1"  # 注意是 api_base 不是 base_url
)
```

### 4. OpenAI API可替换配置

**问题**：默认OpenAI API在国内访问困难。

**解决方案**：
- 在 `config/settings.py` 中添加 `OPENAI_BASE_URL` 配置
- 默认值设置为可访问的代理地址
- 所有使用OpenAI的地方都引用这个配置

```python
# config/settings.py
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://token-plan-cn.xiaomimimo.com/v1")
```

### 5. 文件上传超时处理

**问题**：上传书籍后，LLM处理需要很长时间，导致请求超时。

**解决方案**：
- 前端设置合理的超时时间
- 考虑异步处理模式
- 添加进度提示

## 贡献指南

1. Fork项目
2. 创建功能分支：`git checkout -b feature/xxx`
3. 提交更改：`git commit -m 'Add feature xxx'`
4. 推送分支：`git push origin feature/xxx`
5. 创建Pull Request

## 相关文档

- [设计文档](DESIGN.md)：详细架构设计
- [待办清单](TODO.md)：实现进度
- [README](README.md)：项目介绍

## 联系方式

- 项目地址：[GitHub仓库地址]
- 问题反馈：[Issues页面]