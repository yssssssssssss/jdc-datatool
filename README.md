# JDC数据分析工具

一个基于Flask后端和Streamlit前端的智能数据分析工具，集成了大模型AI能力，提供数据处理、可视化和智能洞察功能。

## 🚀 功能特性

### 📊 数据处理
- 支持CSV、Excel等多种数据格式
- 数据清洗和预处理
- 缺失值处理和异常值检测
- 特征工程和数据转换

### 📈 数据可视化
- 多种图表类型（直方图、散点图、折线图、柱状图等）
- 交互式图表支持
- 自定义样式和主题
- 高质量图表导出

### 🤖 AI智能分析
- 集成OpenAI GPT模型
- 智能数据洞察和建议
- 自动化分析报告生成
- 图表解释和业务含义提取

### 📄 报告生成
- 自动生成HTML分析报告
- 数据质量评估报告
- 可视化图表集成
- 多格式导出支持

## 🏗️ 项目结构

```
jdc-datatool/
├── backend/                 # Flask 后端应用
│   ├── app.py              # 后端应用入口
│   ├── data_processor.py   # 数据处理、清洗、特征工程
│   ├── llm_analyzer.py     # 大模型交互逻辑
│   ├── visualization.py    # 可视化生成逻辑
│   ├── report_generator.py # 报告生成逻辑
│   └── uploads/            # 上传文件存储目录
├── frontend/               # Streamlit 前端应用
│   ├── app.py              # 前端应用入口
│   ├── requirements.txt    # 前端所需的Python库
│   └── assets/             # 静态资源
│       └── logo.svg        # 应用Logo
├── shared/                 # 共享配置和工具
│   └── config.py           # 共享配置，如API密钥等
├── requirements.txt        # 后端所需的Python库
└── README.md              # 项目说明
```

## 🛠️ 安装和部署

### 环境要求
- Python 3.8+
- pip 包管理器
- 可选：Redis（用于缓存）
- 可选：PostgreSQL（用于数据存储）

### 快速开始

1. **克隆项目**
```bash
git clone <repository-url>
cd jdc-datatool
```

2. **创建虚拟环境**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **安装依赖**
```bash
# 安装后端依赖
pip install -r requirements.txt

# 安装前端依赖
pip install -r frontend/requirements.txt
```

4. **配置环境变量**
```bash
# 复制环境变量模板
cp .env.template .env

# 编辑.env文件，配置必要的API密钥
# 特别是OPENAI_API_KEY
```

5. **启动后端服务**
```bash
cd backend
python app.py
```

6. **启动前端应用**
```bash
# 新开终端窗口
cd frontend
streamlit run app.py
```

7. **访问应用**
- 前端界面：http://localhost:7001
- 后端API：http://localhost:7701

## 🔧 配置说明

### 环境变量配置

在项目根目录创建`.env`文件，配置以下变量：

```env
# OpenAI API配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo

# 应用配置
DEBUG=False
SECRET_KEY=your_secret_key

# 文件上传配置
MAX_FILE_SIZE=200
UPLOAD_FOLDER=uploads

# 数据库配置（可选）
DB_HOST=localhost
DB_PORT=5432
DB_NAME=jdc_datatool
DB_USER=postgres
DB_PASSWORD=your_password
```

### 配置文件

详细配置选项请参考 `shared/config.py` 文件。

## 📖 使用指南

### 1. 数据上传
- 支持CSV、Excel格式文件
- 最大文件大小：200MB
- 自动检测数据类型和编码

### 2. 数据预览
- 查看数据基本信息
- 数据类型分析
- 缺失值统计
- 基础统计摘要

### 3. 数据分析
- 描述性统计分析
- 相关性分析
- 缺失值分析
- 异常值检测

### 4. 可视化生成
- 选择合适的图表类型
- 自定义图表参数
- 交互式图表支持
- 高质量图表导出

### 5. AI洞察
- 智能数据分析建议
- 图表解释和业务含义
- 数据质量评估
- 处理建议生成

### 6. 报告生成
- 自动生成分析报告
- HTML格式输出
- 包含图表和洞察
- 支持自定义模板

## 🔌 API接口

### 后端API端点

- `GET /` - 健康检查
- `POST /api/upload` - 文件上传
- `POST /api/analyze` - 数据分析
- `POST /api/visualize` - 生成可视化
- `POST /api/report` - 生成报告
- `POST /api/ai-insights` - AI洞察分析

详细API文档请参考后端代码注释。

## 🧪 测试

```bash
# 运行测试
pytest tests/

# 运行测试并生成覆盖率报告
pytest --cov=backend tests/
```

## 📦 部署

### Docker部署

```bash
# 构建镜像
docker build -t jdc-datatool .

# 运行容器
docker run -p 5000:5000 -p 8501:8501 jdc-datatool
```

### 生产环境部署

1. 使用Gunicorn运行Flask应用
2. 使用Nginx作为反向代理
3. 配置SSL证书
4. 设置环境变量和日志

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📝 开发规范

- 使用Black进行代码格式化
- 使用flake8进行代码检查
- 编写单元测试
- 更新文档

## 🐛 问题反馈

如果您遇到任何问题或有改进建议，请：

1. 查看现有的Issues
2. 创建新的Issue并详细描述问题
3. 提供复现步骤和环境信息

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Flask](https://flask.palletsprojects.com/) - Web框架
- [Streamlit](https://streamlit.io/) - 前端框架
- [OpenAI](https://openai.com/) - AI能力支持
- [Plotly](https://plotly.com/) - 可视化库
- [Pandas](https://pandas.pydata.org/) - 数据处理库

## 📞 联系方式

- 项目维护者：[您的姓名]
- 邮箱：[您的邮箱]
- 项目主页：[项目链接]

---

**JDC数据分析工具** - 让数据分析更智能、更高效！