# 书虫LLM Agent

基于《如何阅读一本书》方法论的LLM Agent，能够深度阅读书籍并构建知识图谱，回答用户问题。

## 功能特性

- **书籍解析**：支持PDF、TXT、EPUB、Markdown等格式
- **知识提取**：自动提取核心概念、观点和论证结构
- **知识图谱**：构建概念间关系网络
- **智能问答**：基于书籍内容回答用户问题
- **Web界面**：基于Vue 3的现代化用户界面

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制环境变量示例文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要的API密钥：

```env
OPENAI_API_KEY=your_openai_api_key_here
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password_here
```

### 3. 启动服务

```bash
# 启动后端服务
python main.py
```

后端服务将在 `http://localhost:8000` 启动。

```bash
# 启动前端开发服务器
cd frontend
npm install
npm run dev
```

前端服务将在 `http://localhost:3000` 启动。

## API接口

### 上传书籍

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@your_book.pdf"
```

### 提问问题

```bash
curl -X POST "http://localhost:8000/question" \
  -H "Content-Type: application/json" \
  -d '{"question": "这本书的主要观点是什么？"}'
```

### 获取概念列表

```bash
curl "http://localhost:8000/concepts"
```

### 搜索概念

```bash
curl "http://localhost:8000/search?keyword=人工智能"
```

### 获取概念关系图

```bash
curl "http://localhost:8000/graph/人工智能?depth=2"
```

## 项目结构

```
bookworm/
├── src/
│   └── bookworm/
│       ├── parsers/          # 书籍解析器
│       ├── extractors/       # 知识提取器
│       ├── graph/            # 知识图谱
│       ├── rag/              # 检索增强生成
│       ├── api/              # Web API
│       └── utils/            # 工具函数
├── tests/                    # 测试文件
├── config/                   # 配置文件
├── data/                     # 数据目录
├── docs/                     # 文档
├── main.py                   # 主程序入口
└── requirements.txt          # 依赖列表
```

## 核心组件

### 书籍解析器

- `PDFParser`：PDF文件解析
- `TXTParser`：TXT文件解析
- `EPUBParser`：EPUB文件解析
- `MarkdownParser`：Markdown文件解析

### 知识提取器

- `ConceptExtractor`：核心概念提取
- `ArgumentExtractor`：核心观点提取
- `RelationExtractor`：关系提取

### 知识图谱

- `Neo4jClient`：Neo4j数据库客户端
- `GraphBuilder`：知识图谱构建器

### 检索增强生成

- `ChromaClient`：向量数据库客户端
- `RAGEngine`：RAG引擎

## 开发指南

### 运行测试

```bash
python tests/test_basic.py
```

### 代码格式化

```bash
black src/
isort src/
```

### 类型检查

```bash
mypy src/
```

## 依赖说明

- **LlamaIndex**：LLM应用框架
- **Neo4j**：图数据库
- **ChromaDB**：向量数据库
- **FastAPI**：Web框架
- **PyPDF2**：PDF解析
- **ebooklib**：EPUB解析

## 许可证

MIT License