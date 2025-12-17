# 文化传播应用

一个基于Flask开发的文化传播应用，支持局域网访问。

## 快速开始

### 环境要求

- Python 3.8+
- pip

### 安装依赖

```bash
# 创建虚拟环境（可选）
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 启动应用

应用提供了两种启动方式，推荐使用**生产级服务器（Waitress）**以获得更好的局域网访问支持。

#### 方式1：生产级服务器（推荐）

```bash
python start_server.py
```

- 优点：稳定性高，适合局域网访问，支持多线程
- 启动后访问地址：
  - 本地访问：http://127.0.0.1:8000
  - 局域网访问：启动后在终端中查看

#### 方式2：开发级服务器

```bash
python run.py
```

- 优点：支持热重载，适合开发调试
- 缺点：稳定性较差，并发性能有限
- 启动后访问地址：
  - 本地访问：http://127.0.0.1:8000
  - 局域网访问：http://服务器IP:8000（替换为实际服务器IP）

## 局域网访问说明

### 确保在同一局域网

- 服务器IP：启动后在终端中查看
- 客户端IP应与服务器IP在同一网段内

### 客户端访问步骤

1. 确保客户端设备与服务器在同一局域网
2. 在浏览器中输入：http://服务器IP:8000（替换为启动后显示的实际IP）
3. 如遇到访问问题，参考下方的故障排除指南

## 故障排除

### 1. 服务器无法启动

- 检查端口是否被占用：
  ```bash
  netstat -ano | findstr :8000
  ```
- 如端口被占用，可修改`start_server.py`或`run.py`中的端口号

### 2. 客户端无法访问

- 检查网络连接：
  ```bash
  ping 服务器IP
  ```
- 检查防火墙设置，确保端口8000允许访问
- 尝试关闭客户端防火墙进行测试
- 清除浏览器缓存或使用无痕模式

### 3. 访问速度慢

- 确保客户端与服务器在同一局域网
- 检查服务器终端显示的实际IP地址是否正确
- 避免在网络拥堵时段访问
- 检查客户端设备性能

## 项目结构

```
文化传播/
├── app/             # 应用核心代码
│   ├── home/        # 首页模块
│   ├── culture/     # 文化模块
│   ├── vr/          # VR体验模块
│   ├── community/   # 互动社区模块
│   ├── dashboard/   # 后台管理模块
│   ├── user/        # 用户管理模块
│   └── ai/          # AI引擎模块
├── migrations/      # 数据库迁移文件
├── static/          # 静态资源
├── templates/       # 模板文件
├── config.py        # 配置文件
├── run.py           # 开发服务器启动脚本
├── start_server.py  # 生产服务器启动脚本
└── requirements.txt # 依赖文件
```

## 技术栈

- **后端框架**：Flask 3.0.3
- **数据库**：SQLAlchemy + SQLite
- **ORM**：Flask-SQLAlchemy
- **迁移工具**：Flask-Migrate
- **生产服务器**：Waitress
- **跨域支持**：Flask-CORS

## 注意事项

1. 本应用使用的是SQLite数据库，适合开发和小型部署
2. 如需要在生产环境使用，建议切换到PostgreSQL或MySQL
3. 定期备份`app/data-dev.sqlite`数据库文件
4. 请勿将敏感信息硬编码到代码中，使用环境变量或配置文件

## 部署说明

### 在Render平台部署

#### 准备工作

1. 确保项目已添加`.gitignore`文件
2. 确保已创建`Procfile`文件
3. 确保`requirements.txt`包含所有必要依赖，包括`gunicorn`
4. 确保`run.py`能正确处理环境变量

#### 部署步骤

1. **创建GitHub仓库**
   - 将项目推送到GitHub仓库
   - 确保`.gitignore`文件已排除不必要的文件

2. **注册Render账号**
   - 访问[Render官网](https://render.com/)并注册账号

3. **创建Web服务**
   - 点击"New" -> "Web Service"
   - 选择"Build and deploy from a Git repository"
   - 连接GitHub账号并选择项目仓库
   - 配置部署设置：
     - **Name**: 输入服务名称
     - **Runtime**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: 自动填充为`gunicorn run:app`（来自Procfile）
     - **Region**: 选择合适的区域

4. **配置环境变量**
   - 在"Environment Variables"部分添加：
     - `FLASK_CONFIG`: `production`
     - `SECRET_KEY`: 随机生成的密钥
     - `COZE_API_KEY`: 你的扣子API密钥（可选）
     - `COZE_APP_ID`: 你的扣子应用ID（可选）

5. **配置数据库**
   - 在Render上创建PostgreSQL数据库
   - 复制数据库连接URL
   - 在环境变量中添加：
     - `DATABASE_URL`: 从Render复制的PostgreSQL连接URL

6. **部署应用**
   - 点击"Create Web Service"
   - 等待部署完成
   - 访问提供的URL查看应用

7. **执行数据库迁移**
   - 在Render控制台中，进入"Shell"
   - 运行以下命令：
     ```bash
     flask db upgrade
     ```

#### 部署后管理

- **访问应用**: 通过Render提供的URL访问
- **查看日志**: 在Render控制台的"Logs"标签查看应用日志
- **更新应用**: 推送代码到GitHub仓库，Render会自动重新部署
- **数据库管理**: 在Render控制台的"PostgreSQL"服务中管理数据库

## 开发说明

### 添加新功能

1. 在`app/`目录下创建新的模块文件夹
2. 创建蓝图和路由
3. 在`app/__init__.py`中注册蓝图
4. 运行开发服务器进行测试

### 数据库迁移

```bash
# 创建迁移文件
flask db migrate -m "迁移描述"

# 执行迁移
flask db upgrade
```

## 联系方式

如有问题，请联系开发者。
