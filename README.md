# 竞品监测平台

天气类App竞品监测 + ToB行业情报监测平台

## 项目简介

实时追踪天气类App竞品动态和ToB行业（地铁、航空、能源）气象情报，自动生成周报。

### 主要功能

- 🌤️ **天气App竞品监测**：10个竞品的版本更新、公司动态、市场数据追踪
- 🏢 **ToB行业监测**：地铁、航空、能源三大行业的气象相关情报
- 📊 **数据可视化**：Dashboard展示、趋势分析图表
- 📝 **自动周报**：每周五自动生成Markdown格式周报
- ⏰ **定时任务**：每天自动采集数据，每周自动备份

## 技术栈

- **后端**：Python 3.9+ / Flask / SQLAlchemy
- **前端**：Bootstrap 5 / Chart.js / Axios
- **数据库**：SQLite
- **调度**：APScheduler
- **数据采集**：Claude API (WebSearch)

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/你的用户名/competitor-monitor-platform.git
cd competitor-monitor-platform
```

### 2. 安装依赖

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 初始化数据库

```bash
python init_db.py
```

### 4. 配置环境变量（可选）

```bash
# 配置Claude API Key以启用自动数据采集
export ANTHROPIC_API_KEY="your-api-key-here"
```

### 5. 启动服务

```bash
# 方式1：使用启动脚本
./start.sh

# 方式2：直接运行
python app.py
```

### 6. 访问平台

打开浏览器访问：http://localhost:5001

## 功能说明

### 天气App竞品监测

监测以下10个竞品：
- The Weather Channel
- AccuWeather
- Windy.com
- Weather & Radar
- Clime
- Weathernews
- WeatherLive
- 天气通
- 彩云天气
- 墨迹天气

### ToB行业监测

#### 🚇 地铁行业
- 监测内容：地铁与气象结合需求、防汛防灾、智能调度
- 竞品：华风气象、华云气象

#### ✈️ 航空行业
- 监测内容：航班延误预警、航路气象服务
- 竞品：WNI（日本气象新闻公司）

#### ⚡ 能源行业
- 监测内容：风电光伏功率预测、双细则政策
- 竞品：国能日新、东润环能、金风科技、远景能源

## 定时任务

- **每天凌晨2点**：自动采集所有竞品和行业数据
- **每周五下午5点**：自动生成周报
- **每周日凌晨3点**：自动备份数据库

## 目录结构

```
竞品监测平台/
├── app.py                  # Flask主应用
├── config.py               # 配置文件
├── scheduler.py            # 定时任务调度
├── init_db.py             # 数据库初始化
├── requirements.txt        # Python依赖
├── models/                 # 数据模型
├── collectors/            # 数据采集器
├── services/              # 业务服务
├── templates/             # HTML模板
├── static/                # 静态资源
├── data/                  # 数据目录
│   ├── competitors.db     # SQLite数据库
│   └── reports/           # 生成的报告
└── logs/                  # 日志文件
```

## 配置说明

### 修改端口

编辑 `config.py`：

```python
PORT = 5001  # 改为你需要的端口
```

### 配置竞品列表

编辑 `config.py` 中的 `COMPETITORS` 列表

### 配置行业监测

编辑 `config.py` 中的 `TOB_INDUSTRIES` 字典

## API文档

### 获取Dashboard数据
```
GET /api/dashboard/summary
```

### 获取最新动态
```
GET /api/activities/recent?days=7&limit=20
```

### 获取竞品列表
```
GET /api/competitors
```

### 获取行业情报
```
GET /api/industry/{industry_key}/news
```

### 手动触发采集
```
POST /api/collection/trigger
POST /api/industry/collect
```

### 生成周报
```
POST /api/reports/generate
```

## 数据采集

### 自动采集（需要API Key）

使用Claude API进行自动数据采集：

1. 获取API Key：https://console.anthropic.com/
2. 配置环境变量：`export ANTHROPIC_API_KEY="sk-ant-..."`
3. 重启服务

### 手动录入

在"设置"页面可以手动录入市场数据

## 生成示例数据

```bash
python generate_sample_data.py
```

## 常见问题

### Q: 端口5000被占用怎么办？
A: macOS的AirPlay占用了5000端口，已默认使用5001端口

### Q: 如何停止服务？
A: `pkill -f app.py`

### Q: 如何查看日志？
A: `tail -f logs/app.log`

### Q: IP地址变化了怎么办？
A: 使用 `http://localhost:5001` 访问，不受IP变化影响

## 注意事项

- 首次运行需要执行 `init_db.py` 初始化数据库
- Claude API按使用量计费，每天约0.5-1美元
- 数据库文件在 `data/competitors.db`
- 周报保存在 `/Users/xiaoxiao.liu/竞品监测周报/`

## 后续计划

- [ ] AI智能分析和洞察生成
- [ ] 邮件/钉钉通知功能
- [ ] 更多行业接入
- [ ] 数据导出（Excel/PDF）
- [ ] 移动端适配

## 许可证

MIT License

## 作者

墨迹天气团队

---

© 2026 行业/竞品监测平台
