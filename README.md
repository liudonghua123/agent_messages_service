# Agent Messages Service

一个用于保存和管理agent聊天会话记录的完整应用，提供MCP服务和Web界面。

## 功能特性

### MCP服务 (/mcp)
- `add_chats()` - 批量添加聊天记录
- `search_chats()` - 根据条件搜索聊天记录
- `get_chat_stats()` - 获取聊天统计信息

### RESTful API
- `GET /status` - 获取应用状态信息
- `GET /chats` - 简单查询聊天记录
- `POST /chats/search` - 复杂条件搜索
- `POST /chats` - 创建聊天记录
- `DELETE /chats` - 删除聊天记录（单个或批量）

### Web前端
- Vue3 + Ant Design Vue
- 分页显示聊天记录
- 搜索和过滤功能
- 详情查看
- 批量删除功能

## 项目结构

```
agent_messages_service/
├── backend/
│   ├── main.py          # FastAPI主应用
│   ├── database.py      # 数据库配置和模型
│   ├── models.py        # Pydantic模型
│   ├── mcp_server.py    # MCP服务器
│   └── static/          # 前端构建文件（部署后）
├── frontend/
│   ├── src/
│   │   ├── App.vue      # 主组件
│   │   ├── main.js      # 入口文件
│   │   └── api/
│   │       └── index.js # API接口
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
├── .env                 # 环境配置
├── requirements.txt     # Python依赖
├── create_table.sql     # 数据库表结构
└── README.md
```

## 安装和运行

### 1. 安装后端依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

编辑 `.env` 文件，配置数据库和服务器设置：

```env
# Database Configuration
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///./chats.db

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 4. 开发模式运行

后端：
```bash
cd backend
python main.py
```

前端（另开终端）：
```bash
cd frontend
npm run dev
```

### 5. 生产部署

构建前端并部署：
```bash
cd frontend
npm run deploy
```

然后运行后端：
```bash
cd backend
python main.py
```

访问 http://localhost:8000 查看应用。

## 数据库表结构

```sql
CREATE TABLE chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    datetime DATETIME NOT NULL,
    user VARCHAR(255) NOT NULL,
    fullfill BOOLEAN NOT NULL DEFAULT FALSE,
    process_time INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## MCP工具使用示例

### 添加聊天记录
```python
add_chats([
    {
        "session": "session_001",
        "question": "什么是人工智能？",
        "answer": "人工智能是计算机科学的一个分支...",
        "datetime": "2024-01-01T10:00:00",
        "user": "user1",
        "fullfill": True,
        "process_time": 1500
    }
])
```

### 搜索聊天记录
```python
search_chats({
    "user": "user1",
    "fullfill": True,
    "datetime_from": "2024-01-01T00:00:00"
})
```

## API使用示例

### 复杂查询
```bash
curl -X POST "http://localhost:8000/chats/search" \
  -H "Content-Type: application/json" \
  -d '{
    "conditions": [
      {
        "field": "datetime",
        "operator": "between",
        "value": "2024-01-01T00:00:00",
        "value2": "2024-12-31T23:59:59"
      },
      {
        "field": "user",
        "operator": "eq",
        "value": "user1"
      }
    ],
    "page": 1,
    "page_size": 20
  }'
```

### 批量删除
```bash
curl -X DELETE "http://localhost:8000/chats?ids=1,2,3"
```

## 支持的查询操作符

- `eq` - 等于
- `ne` - 不等于
- `gt` - 大于
- `ge` - 大于等于
- `lt` - 小于
- `le` - 小于等于
- `like` - 模糊匹配
- `between` - 范围查询

## 技术栈

- **后端**: FastAPI + FastMCP + SQLAlchemy
- **前端**: Vue3 + Vite + Ant Design Vue
- **数据库**: SQLite (开发) / MySQL (生产)
- **部署**: 前后端分离，静态文件服务