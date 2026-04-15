# 🍽️ Food Calories Calculator — 食物热量计算器

一个通过拍摄食物照片智能识别食物并估算热量的 Web 应用。

## ✨ 功能特性

- **单张照片识别**：上传食物照片，自动识别食物种类并估算热量
- **饭前饭后对比**：通过对比饭前和饭后照片，精确计算实际食用量和摄入热量
- **双模型支持**：
  - **OpenRouter 多模态模型**：使用 Qwen2.5-VL 等云端视觉语言模型（推荐）
  - **本地自训练模型**：支持 Python (PyTorch) 或 .NET ML 训练的模型
- **响应式设计**：支持桌面和移动端浏览器

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────┐
│                   Frontend                       │
│     HTML + CSS + JavaScript (原生, 无框架)        │
│  · 照片拍摄/上传  · 模型选择  · 结果展示           │
└───────────────────┬─────────────────────────────┘
                    │ REST API
┌───────────────────┴─────────────────────────────┐
│                Backend (FastAPI)                  │
│  /api/food/recognize  — 单张照片识别              │
│  /api/food/compare    — 饭前饭后对比              │
│  /api/health          — 健康检查                  │
├─────────────────────────────────────────────────┤
│              Model Services                      │
│  ┌──────────────┐    ┌──────────────────┐        │
│  │ OpenRouter   │    │  Local Model     │        │
│  │ (Qwen2.5-VL │    │  (PyTorch /      │        │
│  │  via API)   │    │   ML.NET)        │        │
│  └──────────────┘    └──────────────────┘        │
└─────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 前提条件

- Python 3.10+
- pip

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 OpenRouter API Key
# 如果只使用本地模型，可以留空 API Key
```

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `OPENROUTER_API_KEY` | OpenRouter API 密钥 | (空) |
| `OPENROUTER_MODEL` | 使用的多模态模型 | `qwen/qwen2.5-vl-72b-instruct` |
| `DEFAULT_MODEL` | 默认识别模型 | `openrouter` |

### 3. 启动服务

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

然后访问 http://localhost:8000 即可使用。

### 4. 运行测试

```bash
cd backend
pytest tests/ -v
```

## 📁 项目结构

```
FoodCaloriesCalculator0/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 应用入口
│   │   ├── config.py            # 配置管理
│   │   ├── models.py            # 数据模型
│   │   ├── routers/
│   │   │   └── food.py          # 食物识别 API 路由
│   │   └── services/
│   │       ├── openrouter.py    # OpenRouter API 集成
│   │       └── local_model.py   # 本地模型集成（含演示模式）
│   ├── tests/
│   │   └── test_api.py          # API 测试
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html               # 前端页面
│   ├── style.css                # 样式
│   └── app.js                   # 前端逻辑
├── docs/
│   └── model_training.md        # 自训练模型指南
└── README.md
```

## 🔌 API 接口

### `POST /api/food/recognize` — 单张照片识别

| 参数 | 类型 | 说明 |
|------|------|------|
| `image` | File | 食物照片 |
| `model` | string | `"openrouter"` 或 `"local"` |

### `POST /api/food/compare` — 饭前饭后对比

| 参数 | 类型 | 说明 |
|------|------|------|
| `before_image` | File | 饭前照片 |
| `after_image` | File | 饭后照片 |
| `model` | string | `"openrouter"` 或 `"local"` |

### `GET /api/health` — 健康检查

返回服务状态。

## 🤖 模型说明

### OpenRouter 多模态模型（推荐）

通过 [OpenRouter](https://openrouter.ai/) 调用 Qwen2.5-VL 等视觉语言模型：
- 无需本地训练，开箱即用
- 识别精度高，支持多种食物
- 需要 API Key（在 OpenRouter 注册获取）

### 自训练模型

支持使用 PyTorch 或 .NET ML (ML.NET) 训练自己的食物识别模型。详细说明请参考 [模型训练指南](docs/model_training.md)，包括：
- 数据集获取（Food-101、UECFOOD-256、Nutrition5k 等）
- 模型训练（基于 ResNet 迁移学习）
- 模型集成（替换 `local_model.py` 中的 demo 实现）

## 📜 License

MIT
