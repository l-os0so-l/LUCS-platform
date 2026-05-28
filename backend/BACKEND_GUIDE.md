# RSOD Web Platform — 后端架构文档

> 本文档面向需要理解、维护或扩展后端功能的开发者。涵盖架构设计、数据库模型、核心模块实现及 API 概览。

---

## 一、项目概述

LUCS Platform（RSOD Web Platform）后端是一个基于 **FastAPI** 构建的异步 Web 服务，为前端提供：

- 遥感影像的语义分割推理（DeepLabV3+ / ResNet50）
- 用户认证与权限管理（JWT + SQLite）
- 检测历史记录的持久化存储
- AI 问答对话（Kimi / Moonshot API）
- 静态文件托管（上传图片、分割结果图）

---

## 二、技术栈

| 层级 | 技术/库 | 版本/说明 |
|------|---------|-----------|
| Web 框架 | FastAPI | 异步 ASGI，自动生成 OpenAPI 文档 |
| ASGI 服务器 | Uvicorn | 运行 FastAPI 应用 |
| ORM | SQLAlchemy 2.x | SQLite 数据库，声明式模型 |
| 密码哈希 | passlib (pbkdf2_sha256) | 安全存储用户密码 |
| JWT | PyJWT | 用户认证 Token 生成与验证 |
| 深度学习 | PyTorch + smp | segmentation-models-pytorch 语义分割 |
| 图像处理 | Pillow (PIL) | 图片读取、保存、resize |
| 日志 | 自定义彩色日志 | 支持 request-id 链路追踪 |
| AI 对话 | OpenAI SDK | 兼容 Moonshot (Kimi) API |

---

## 三、目录结构

```
backend/
├── main.py                     # 应用入口：FastAPI 实例、路由注册、生命周期事件
├── app/
│   ├── config.py               # 配置管理：环境变量 + .env 文件
│   ├── database.py             # 数据库连接：SQLAlchemy engine + Session + Base
│   ├── api/                    # API 路由层（按模块拆分）
│   │   ├── auth.py             # 注册 / 登录 / 获取当前用户
│   │   ├── detection.py        # 单图检测 / 批量检测 / 视频帧检测 / 历史记录 CRUD
│   │   ├── users.py            # 用户资料 / 个人统计
│   │   └── qa.py               # AI 问答（对接 Kimi API）
│   ├── core/                   # 核心基础设施
│   │   ├── paths.py            # 路径管理：项目根目录自动探测 + 环境变量覆盖
│   │   ├── logging_utils.py    # 日志配置 + RequestLoggingMiddleware
│   │   └── validation.py       # 数据集校验工具（独立模块）
│   ├── models/                 # 数据模型
│   │   ├── database.py         # SQLAlchemy ORM 模型（User、DetectionRecord）
│   │   └── schemas.py          # Pydantic 数据校验模型（请求/响应 DTO）
│   ├── services/               # 业务逻辑层
│   │   ├── detection_service.py # 语义分割推理服务（模型加载、预测、可视化）
│   │   └── history_service.py  # 历史记录 JSON 文件存储（兼容旧版）
│   └── utils/                  # 工具函数
│       ├── security.py         # JWT + 密码哈希 + 当前用户依赖
│       └── file_utils.py       # 文件上传保存 + URL 生成
├── static/                     # 静态文件目录（挂载到 /static）
│   ├── uploads/                # 用户上传的原图
│   └── results/                # 分割结果图 + 叠加图
├── models/                     # 深度学习模型权重
│   └── land_seg_best.pth       # DeepLabV3+ ResNet50 训练权重
└── data/                       # 数据持久化
    ├── rsod_platform.db        # SQLite 数据库文件
    └── detection_history.json  # 历史记录 JSON 备份（兼容旧版）
```

---

## 四、核心架构

### 4.1 分层设计

后端采用经典的三层架构：

```
┌─────────────────────────────────────────────┐
│  API 路由层 (app/api/*.py)                   │
│  - 参数校验、认证依赖、HTTP 状态码           │
│  - 调用 Service 层，组装 Response            │
├─────────────────────────────────────────────┤
│  业务逻辑层 (app/services/*.py)              │
│  - 检测推理、历史记录管理                    │
│  - 与模型、文件系统、外部 API 交互           │
├─────────────────────────────────────────────┤
│  数据访问层 (app/models/*.py + database.py)  │
│  - ORM 模型定义、数据库会话管理              │
│  - Pydantic Schema 数据校验                  │
└─────────────────────────────────────────────┘
```

### 4.2 请求生命周期

```
Client Request
    ↓
CORS Middleware
    ↓
RequestLoggingMiddleware (生成 x-request-id，记录耗时)
    ↓
FastAPI 依赖注入
    ├── get_db()          → SQLAlchemy Session
    ├── get_current_user() → JWT 解码 → 查询 User 表
    ↓
API Router Handler
    ↓
Service Layer
    ↓
Database / Model / External API
    ↓
Pydantic Response Model
    ↓
JSON Response
```

---

## 五、数据库设计

### 5.1 连接配置 (`app/database.py`)

```python
# SQLite 单文件数据库，适合中小规模部署
DATABASE_URL = "sqlite:///<project>/backend/data/rsod_platform.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # 允许多线程访问
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

- **启动时自动建表**：`main.py` 中 `@app.on_event("startup")` 调用 `Base.metadata.create_all(bind=engine)`
- **会话管理**：通过 `get_db()` 依赖注入，确保请求结束后会话正确关闭

### 5.2 ORM 模型 (`app/models/database.py`)

#### User 表

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | String(36), PK | UUID，默认自动生成 |
| `username` | String(50), Unique | 登录用户名 |
| `email` | String(100), Unique | 邮箱 |
| `password_hash` | String(255) | pbkdf2_sha256 哈希值 |
| `nickname` | String(50) | 昵称 |
| `role` | String(20) | `user` / `admin` |
| `avatar_url` | String(500) | 头像 URL |
| `location` | String(100) | 所在地 |
| `is_active` | Boolean | 账号是否启用 |
| `created_at` | DateTime | 注册时间 |
| `updated_at` | DateTime | 最后更新时间 |

**关系**：`User.detection_records` ↔ `DetectionRecord.user` (一对多，级联删除)

#### DetectionRecord 表

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | String(36), PK | 检测记录 UUID |
| `user_id` | String(36), FK → users.id | 关联用户（可为 NULL） |
| `filename` | String(255) | 原始上传文件名 |
| `model_name` | String(50) | 使用的模型版本 |
| `type` | String(20) | `single` / `batch` / `video` |
| `image_url` | String(500) | 原图访问 URL |
| `result_image_url` | String(500) | 伪彩色分割图 URL |
| `overlay_image_url` | String(500) | 叠加图 URL |
| `class_stats` | JSON | 7 类像素统计列表 |
| `total_pixels` | Integer | 总像素数 |
| `inference_time` | Float | 推理耗时（秒） |
| `created_at` | DateTime | 检测时间 |

### 5.3 双存储策略

检测记录同时保存到 **SQLite 数据库**（主存储）和 **JSON 文件**（`data/detection_history.json`，兼容旧版）：

- 新记录优先查数据库，数据库没有时回退到 JSON
- JSON 文件作为迁移过渡期备份，后续可逐步淘汰

---

## 六、主要功能模块

### 6.1 语义分割推理 (`app/services/detection_service.py`)

#### 模型信息

- **架构**：DeepLabV3+ + ResNet50（`segmentation_models_pytorch`）
- **输入**：任意尺寸 RGB 图片，预处理为 32 的倍数
- **输出**：`argmax` 后的类别索引 mask（H, W），值域 0-6
- **类别映射**（已人工校准）：

| 索引 | 中文名 | 英文名 | 显示颜色 |
|------|--------|--------|----------|
| 0 | 背景 | background | 黑色 `#000000` |
| 1 | 荒地 | barren | 棕色 `#8B4513` |
| 2 | 建筑 | building | 红色 `#FF0000` |
| 3 | 道路 | road | 黄色 `#FFFF00` |
| 4 | 水域 | water | 蓝色 `#0000FF` |
| 5 | 耕地 | agriculture | 绿色 `#00FF00` |
| 6 | 森林 | forest | 深绿 `#008000` |

#### 推理流程

```
PIL Image (原图)
    ↓ _preprocess_image
Resize → 短边对齐 512，保持长宽比，32 倍数
    ↓
归一化 (ImageNet: mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
    ↓
Tensor (1, 3, H, W) → GPU/CPU
    ↓ model.forward
Logits (1, 7, H, W)
    ↓ argmax
Pred Mask (H, W)
    ↓ NEAREST resize
原图尺寸 Mask
    ↓ _save_visualizations
伪彩色图 (PALETTE[mask]) + 叠加图 (原图 60% + 彩色 40%)
```

#### 线程安全

模型加载为**单例**（`DetectionService`），推理时通过 `threading.Lock()` 加锁：

```python
with self._lock:
    mask = _predict(self.model, pil_img)
```

> PyTorch 模型非线程安全，并发请求必须串行化。

#### 实时视频帧检测

- 不保存到数据库/文件系统
- 直接返回 base64 编码的图片 + 像素统计
- 用于前端视频实时播放时的逐帧分类

---

### 6.2 用户认证 (`app/utils/security.py` + `app/api/auth.py`)

#### 密码哈希

```python
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
```

- 使用 `pbkdf2_sha256`（避免 bcrypt 缺少 C 后端的问题）
- `hash_password()` / `verify_password()`

#### JWT 流程

```
注册 / 登录
    ↓
验证用户名密码
    ↓
create_access_token({"sub": user.id})
    ↓
返回 {token, user_info}
    ↓
前端存储 token 到 localStorage
    ↓
后续请求 Header: Authorization: Bearer <token>
    ↓
get_current_user() 解码 JWT → 查询 User 表
```

- Token 有效期：**7 天**
- 算法：**HS256**
- 认证方式：**HTTP Bearer Token**

#### 两种用户依赖

| 依赖函数 | 未登录时的行为 | 使用场景 |
|----------|---------------|----------|
| `get_current_user` | 返回 `None` | 检测接口（允许匿名，但记录 `user_id=None`） |
| `get_current_user_required` | 抛 401 | 历史记录、用户资料、个人统计 |

---

### 6.3 历史记录管理 (`app/api/detection.py` + `app/services/history_service.py`)

#### 权限隔离

所有历史记录接口严格按 `user_id` 过滤：

```python
query = db.query(DetectionRecord).filter(DetectionRecord.user_id == current_user.id)
```

- 用户 A 只能查看/删除自己的记录
- 早期 `user_id=None` 的记录对所有登录用户隐藏

#### 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/detection/single` | 单图分类 |
| POST | `/api/detection/video-frame` | 视频实时帧分类 |
| GET | `/api/detection/history` | 分页查询历史（支持搜索、模型过滤） |
| GET | `/api/detection/history/{id}` | 单条详情 |
| DELETE | `/api/detection/history/{id}` | 删除记录 |
| GET | `/api/detection/targets/list` | 获取 7 类土地类型定义 |

---

### 6.4 AI 问答 (`app/api/qa.py`)

- 对接 **Kimi (Moonshot) K2.6** 模型
- 使用 OpenAI 兼容 SDK：`base_url = "https://api.moonshot.cn/v1"`
- API Key 从 `.env` 文件读取（`MOONSHOT_API_KEY`）
- **单轮对话**：不维护会话历史，每次独立请求
- **系统提示词**包含真实的模型指标（mIoU ~65-70%，各类别 Val IoU），禁止 AI 编造能力

---

## 七、配置管理

### 7.1 配置来源 (`app/config.py`)

优先级从高到低：

1. **环境变量**（如 `RSOD_DATA_DIR`）
2. **`.env` 文件**（`backend/.env`，键值对格式）
3. **代码默认值**

```bash
# backend/.env 示例
MOONSHOT_API_KEY=sk-xxxxxxxxxxxxxxxx
```

### 7.2 路径管理 (`app/core/paths.py`)

**核心设计**：运行时自动探测项目根目录（通过 `.rsod_platform` 标记文件），无需硬编码绝对路径。

```python
from app.core.paths import paths

paths.root      # → <project>/rsod-web-platform/
paths.backend   # → <project>/rsod-web-platform/backend/
paths.static    # → <project>/rsod-web-platform/backend/static/
paths.uploads   # → <project>/rsod-web-platform/backend/static/uploads/
paths.results   # → <project>/rsod-web-platform/backend/static/results/
paths.models    # → <project>/rsod-web-platform/backend/models/
```

**环境变量覆盖**：

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `RSOD_ROOT` | 自动探测 | 项目根目录 |
| `RSOD_DATA_DIR` | `backend/data/` | 数据库/日志目录 |
| `RSOD_MODEL_DIR` | `backend/models/` | 模型权重目录 |
| `RSOD_STATIC_DIR` | `backend/static/` | 静态文件根目录 |
| `RSOD_UPLOAD_DIR` | `static/uploads/` | 上传图片目录 |
| `RSOD_RESULT_DIR` | `static/results/` | 结果图片目录 |

---

## 八、文件存储

### 8.1 上传文件处理 (`app/utils/file_utils.py`)

```python
async def save_upload_file(file: UploadFile) -> str:
    timestamp = int(time.time())
    pure_name = Path(file.filename).name  # 丢弃路径，仅保留文件名
    filename = f"{timestamp}_{pure_name}"
    # 保存到 static/uploads/
```

- 添加时间戳前缀避免文件名冲突
- **重要**：`webkitdirectory` 上传时文件名可能包含子目录路径（如 `small/image.png`），后端使用 `Path(file.filename).name` 提取纯文件名

### 8.2 URL 生成

```python
def get_file_url(filename: str, dir_path: str) -> str:
    # 基于 static 目录计算相对路径
    # 返回: /static/uploads/xxx.png 或 /static/results/xxx_mask.png
```

前端拼接完整 URL：`http://localhost:8000/static/uploads/xxx.png`

---

## 九、日志系统

### 9.1 配置 (`app/core/logging_utils.py`)

- 支持 **文本格式** 和 **JSON 格式**
- 支持文件轮转 + 控制台彩色输出
- 自动注入 `x-request-id` 请求头，实现链路追踪

### 9.2 RequestLoggingMiddleware

自动记录每条请求的：

- 请求方法、路径、客户端 IP
- 处理耗时（毫秒）
- 响应状态码
- 唯一 request-id

跳过路径：`/health`、`/api/test/connect`、`/`

---

## 十、部署运行

### 10.1 开发环境启动

```bash
cd backend
# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

访问：
- API 文档：`http://localhost:8000/docs`
- 健康检查：`http://localhost:8000/health`

### 10.2 前端代理配置

Vite 开发服务器配置代理（`vite.config.js`）：

```javascript
server: {
  proxy: {
    '/api': 'http://localhost:8000',
    '/static': 'http://localhost:8000',
  }
}
```

### 10.3 生产环境注意事项

1. **更换 JWT SECRET_KEY**：`app/utils/security.py` 中硬编码的密钥必须替换为强随机字符串
2. **关闭 DEBUG 模式**：`app/config.py` 中 `DEBUG = False`
3. **数据库迁移**：目前使用 `create_all()` 自动建表，生产环境建议使用 Alembic 管理迁移
4. **模型文件**：确保 `backend/models/land_seg_best.pth` 存在
5. **CORS**：限制 `CORS_ORIGINS` 为实际前端域名

---

## 十一、常见问题

### Q: 模型加载失败（`FileNotFoundError: land_seg_best.pth`）？

A: 将训练好的模型权重放入 `backend/models/land_seg_best.pth`，或修改 `.env` 中的 `SEGMENTATION_MODEL_PATH`。

### Q: 数据库表结构变更后如何同步？

A: 目前采用 `Base.metadata.create_all()` 自动建表。如需删除重建，直接删除 `backend/data/rsod_platform.db`，重启服务即可。

### Q: 如何添加新的 API 路由？

A: 在 `app/api/` 下新建模块，创建 `APIRouter`，然后在 `main.py` 中 `app.include_router(..., prefix="/api")`。

### Q: numpy 2.x 兼容性错误？

A: `detection_service.py` 头部已包含 numpy 2.x 兼容性补丁，将 `numpy._core` 映射到 `numpy.core`，使旧版 torch 保存的权重能正常加载。

---

*文档版本：v1.0 | 最后更新：2026-05-28*
