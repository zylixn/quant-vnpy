# quant-vnpy

A Flask API service for quantitative trading, built on top of vnpy.

## 项目简介

quant-vnpy 是一个基于 vnpy 开发的量化交易系统，提供完整的股票交易工作流程，包括数据获取、策略执行、风险评估、回测和交易模拟等功能。系统采用模块化设计，通过任务管理机制实现各组件的协同工作。

## 功能特性

### 核心功能
- **数据获取**：支持从本地文件、API 和数据库获取股票数据
- **策略执行**：内置多种交易策略，包括牛市策略、熊市策略等
- **风险评估**：提供多种风险指标计算，如最大回撤、夏普比率、索提诺比率等
- **回测系统**：基于 vnpy 的回测引擎，支持多种回测参数配置
- **交易模拟**：提供模拟交易功能，支持订单管理和成交记录
- **任务管理**：统一的任务管理框架，支持异步任务执行和状态监控

### API 接口
- RESTful API 设计，支持所有核心功能的远程调用
- 完整的任务管理接口，支持任务的创建、启动、停止和状态查询
- 标准化的响应格式，便于前端集成

### 技术特点
- 模块化设计，各组件松耦合
- 多线程异步执行，提高系统性能
- 完善的错误处理和日志记录
- 支持扩展自定义策略和数据源

## 系统架构

```
quant-vnpy/
├── app/             # Flask 应用
│   ├── api/         # API 路由
│   └── config.py    # 配置文件
├── cmd/             # 命令行工具
│   └── main.py      # 应用入口
├── internal/        # 内部模块
│   ├── backtest/    # 回测模块
│   ├── fetcher/     # 数据获取模块
│   ├── risk/        # 风险评估模块
│   ├── strategies/  # 策略模块
│   ├── trading/     # 交易模块
│   └── task/        # 任务管理模块
├── pyproject.toml   # 项目依赖
└── start.bat        # 启动脚本
```

### 模块说明

| 模块 | 主要职责 | 文件位置 |
|------|---------|----------|
| 数据获取 | 获取和处理股票数据 | internal/fetcher/ |
| 策略 | 实现交易策略 | internal/strategies/ |
| 风险评估 | 计算风险指标 | internal/risk/ |
| 交易 | 模拟交易执行 | internal/trading/ |
| 回测 | 策略回测 | internal/backtest/ |
| 任务管理 | 管理任务生命周期 | internal/task/ |

## 安装说明

### 前置依赖
- Python 3.10+
- vnpy 4.3.0+
- Flask 2.0.0+

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd quant-vnpy
   ```

2. **安装依赖**
   ```bash
   # 使用 pip
   pip install -r requirements.txt
   
   # 或使用 poetry
   poetry install
   ```

3. **配置 vnpy**
   - 参考 vnpy 官方文档配置数据源和交易接口

## 使用指南

### 启动服务

```bash
# 使用启动脚本
./start.bat

# 或直接运行
python cmd/main.py
```

服务默认运行在 `http://0.0.0.0:5000`。

### 核心 API 接口

#### 任务管理
- `POST /api/tasks/create` - 创建任务
- `GET /api/tasks/list` - 列出任务
- `GET /api/tasks/get/{task_id}` - 获取任务详情
- `POST /api/tasks/start/{task_id}` - 启动任务
- `POST /api/tasks/stop/{task_id}` - 停止任务
- `DELETE /api/tasks/delete/{task_id}` - 删除任务
- `GET /api/tasks/status/{task_id}` - 获取任务状态
- `POST /api/tasks/create_and_start` - 创建并启动任务

#### 数据获取
- `GET /api/fetcher/stock` - 获取股票数据
- `GET /api/fetcher/stock_list` - 获取股票列表
- `GET /api/fetcher/stock_info` - 获取股票信息

#### 风险评估
- `GET /api/risk/assessment` - 获取风险评估
- `GET /api/risk/report` - 获取风险报告

#### 交易
- `POST /api/trading/buy` - 买入
- `POST /api/trading/sell` - 卖出
- `GET /api/trading/account` - 获取账户信息
- `GET /api/trading/positions` - 获取持仓信息

### 示例：执行完整工作流

```bash
curl -X POST http://localhost:5000/api/tasks/create_and_start \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "full_workflow",
    "params": {
      "symbol": "600000",
      "start": "2025-02-11T00:00:00",
      "end": "2026-02-11T00:00:00",
      "interval": "1d",
      "strategy_name": "bull",
      "initial_balance": 100000.0
    }
  }'
```

## 项目结构

```
quant-vnpy/
├── app/                     # Flask 应用
│   ├── api/                 # API 路由
│   │   ├── resources/       # 资源文件
│   │   └── __init__.py      # API 初始化
│   ├── __init__.py          # 应用初始化
│   └── config.py            # 配置文件
├── cmd/                     # 命令行工具
│   └── main.py              # 应用入口
├── internal/                # 内部模块
│   ├── backtest/            # 回测模块
│   │   ├── api/             # 回测 API
│   │   ├── backtest_engine.py # 回测引擎
│   │   └── strategies.py    # 回测策略
│   ├── fetcher/             # 数据获取模块
│   │   ├── api/             # 数据获取 API
│   │   ├── data_processor.py # 数据处理
│   │   └── stock_fetcher.py # 股票数据获取
│   ├── risk/                # 风险评估模块
│   │   ├── api/             # 风险评估 API
│   │   └── risk_assessor.py # 风险评估器
│   ├── strategies/          # 策略模块
│   │   ├── bull_trend_strategy.py # 牛市策略
│   │   └── bear_strategy.py # 熊市策略
│   ├── trading/             # 交易模块
│   │   ├── api/             # 交易 API
│   │   └── simulator/       # 交易模拟器
│   └── task/                # 任务管理模块
│       ├── api/             # 任务管理 API
│       ├── task_manager.py  # 任务管理器
│       └── tasks.py         # 任务类型定义
├── pyproject.toml           # 项目依赖
├── README.md                # 项目文档
└── start.bat                # 启动脚本
```

## 快速开始

### 1. 数据获取

```python
from internal.fetcher.stock_fetcher import StockFetcher
from datetime import datetime

# 创建数据获取器
fetcher = StockFetcher()

# 获取股票数据
bars = fetcher.get_stock_data(
    symbol="600000",
    start=datetime(2025, 1, 1),
    end=datetime(2025, 12, 31),
    interval="1d"
)
```

### 2. 策略执行

```python
from internal.strategies.bull_trend_strategy import BullStrategy

# 使用牛市策略
strategy = BullStrategy(cta_engine=None, strategy_name="bull", vt_symbol="600000.SSE", setting={})
```

### 3. 回测

```python
from internal.backtest.backtest_engine import BacktestEngine
from datetime import datetime

# 创建回测引擎
engine = BacktestEngine()

# 设置回测参数
engine.set_parameters(
    vt_symbol="600000.SSE",
    interval="1d",
    start=datetime(2025, 1, 1),
    end=datetime(2025, 12, 31),
    capital=1000000
)

# 添加策略
from internal.strategies.bull_trend_strategy import BullStrategy
engine.add_strategy(BullStrategy, {})

# 运行回测
results = engine.run_backtesting()
statistics = engine.calculate_statistics()
```

### 4. 任务管理

```python
from internal.task.task_manager import TaskManager
from internal.task.tasks import FullWorkflowTask
from datetime import datetime, timedelta

# 创建任务管理器
task_manager = TaskManager()

# 创建完整工作流任务
workflow_params = {
    "symbol": "600000",
    "start": datetime.now() - timedelta(days=365),
    "end": datetime.now(),
    "interval": "1d",
    "strategy_name": "bull",
    "initial_balance": 100000.0
}
workflow_task = FullWorkflowTask(workflow_params)

# 启动任务
task_id = task_manager.create_and_start_task(workflow_task)
print(f"任务 ID: {task_id}")

# 获取任务状态
status = task_manager.get_task_status(task_id)
print(f"任务状态: {status}")
```

## 自定义策略

要添加自定义策略，只需在 `internal/strategies/` 目录下创建新的策略文件，并继承 `CtaTemplate` 类：

```python
from vnpy.app.cta_strategy import CtaTemplate

class MyStrategy(CtaTemplate):
    """自定义策略"""
    author = "Your Name"

    # 策略参数
    param1 = 10
    param2 = 20

    parameters = ["param1", "param2"]
    variables = []

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

    def on_bar(self, bar):
        """收到新 K 线时回调"""
        # 策略逻辑
        pass
```

## 配置说明

### 数据源配置

在使用 API 数据源时，需要配置相应的 API 密钥。具体配置方法请参考各数据源的官方文档。

### 风险参数配置

在 `internal/risk/risk_assessor.py` 中，可以调整风险评估的参数：

```python
# 风险管理参数
risk_limits = {
    'max_position_size': 0.3,  # 最大持仓比例
    'max_drawdown': 0.2,       # 最大回撤限制
    'max_leverage': 3.0,        # 最大杠杆
    'single_trade_risk': 0.02   # 单笔交易风险
}
```

## 故障排除

### 常见问题

1. **模块导入错误**
   - 确保已安装所有依赖包
   - 确保 Python 版本 >= 3.10

2. **数据源连接失败**
   - 检查网络连接
   - 检查 API 密钥配置
   - 检查数据源服务状态

3. **回测结果异常**
   - 检查数据质量
   - 检查策略参数配置
   - 检查回测参数设置

### 日志查看

系统运行日志可在控制台查看，详细的错误信息会输出到标准错误流。

## 贡献指南

欢迎各位开发者贡献代码和提出建议！

### 贡献流程
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

### 代码规范
- 遵循 PEP 8 代码风格
- 提供清晰的文档和注释
- 编写单元测试

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 联系方式

- 项目地址：[https://github.com/yourusername/quant-vnpy](https://github.com/yourusername/quant-vnpy)
- 问题反馈：[https://github.com/yourusername/quant-vnpy/issues](https://github.com/yourusername/quant-vnpy/issues)

---

**注意**：本项目仅用于学习和研究目的，不构成任何投资建议。实际交易中请谨慎使用，并遵循相关法律法规。