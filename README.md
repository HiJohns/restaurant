# 订餐软件 (Restaurant Ordering System)

Hello 大家好啊！这是新的代码

## 项目简介

全栈订餐系统，包含前端 React + Vite 界面和后端 FastAPI 服务。

## 快速开始

### 前置要求
- Node.js 16+
- Python 3.8+
- npm 或 yarn

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd restaurant
```

2. **启动所有服务**
```bash
make start
```

这个命令会自动：
- 启动 Customer 后端 API (端口 8001) - 客户菜单和下单
- 启动 Staff 后端 API (端口 8000) - 员工管理和分析
- 启动前端开发服务器 (端口 5174)

或者分别启动：
```bash
make backend-customer  # 客户后端 (8001)
make backend-staff     # 员工后端 (8000)
make frontend          # 前端 (5174)
```

3. **访问应用**
- 本地访问: http://localhost:5174
- 后端 API: http://localhost:8000

4. **停止服务**
```bash
./stop_all.sh
# 或按 Ctrl+C
```

## 生产环境部署

### 环境变量配置

**开发环境** (`frontend/.env.development`):
```
VITE_API_BASE=http://localhost:8000
```

**生产环境** (`frontend/.env.production`):
```
VITE_API_BASE=http://opencode.linxdeep.com:8000
```

### 使用 Nginx 反向代理（推荐）

1. **安装 Nginx**
```bash
sudo apt update
sudo apt install nginx
```

2. **配置 Nginx**

创建配置文件 `/etc/nginx/sites-available/opencode.linxdeep.com`:

```nginx
server {
    listen 80;
    server_name opencode.linxdeep.com;

    # 前端静态资源
    location / {
        proxy_pass http://localhost:5174;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # API 反向代理
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. **启用配置**
```bash
sudo ln -s /etc/nginx/sites-available/opencode.linxdeep.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

4. **配置说明**
- 前端通过 `http://opencode.linxdeep.com` 访问
- API 通过 `http://opencode.linxdeep.com/api/` 访问
- 浏览器地址栏不暴露端口

### 不使用反向代理（直接端口访问）

如果直接使用端口访问，需确保：
- 后端端口 8000 在 AWS 安全组中开放
- 前端 API 调用使用完整域名

前端配置：
```javascript
// frontend/src/config.js
export const API_BASE = 'http://opencode.linxdeep.com:8000';
```

## 项目结构

```
restaurant/
├── app/                    # FastAPI 后端
│   └── main.py            # 主应用文件
├── data/                   # 数据库文件
│   └── smartbite.db       # SQLite 数据库
├── frontend/               # React 前端
│   ├── src/
│   │   ├── App.jsx        # 主组件
│   │   ├── Menu.jsx       # 菜单组件
│   │   └── config.js      # API 配置
│   └── .env.*             # 环境变量
├── scripts/                # 脚本文件
├── run_all.sh             # 一键启动脚本
├── stop_all.sh            # 一键停止脚本
├── requirements.txt       # Python 依赖
└── README.md             # 本文档
```

## API 端点

### Customer Service (端口 8001)
- **GET** `/dishes` - 获取菜品列表
- **POST** `/order` - 创建订单

### Staff Service (端口 8000)
- **GET** `/orders/pending` - 获取待处理订单
- **PATCH** `/order/{id}/status` - 更新订单状态
- **GET** `/analytics/revenue` - 获取收入分析
- **POST** `/dishes` - 创建菜品 (管理员)
- **DELETE** `/dishes/{id}` - 删除菜品 (管理员)

## 技术栈

- **前端**: React 18, Vite, JavaScript
- **后端**: FastAPI, Python 3.8+
- **数据库**: SQLite
- **服务器**: Uvicorn

## 贡献指南

1. 创建功能分支: `git checkout -b feature-name`
2. 提交更改: `git commit -m 'feat: description'`
3. 推送到分支: `git push origin feature-name`
4. 创建 Pull Request

## 许可证

MIT License
