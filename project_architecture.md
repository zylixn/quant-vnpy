# Quant-VNPY 项目架构脑图

```
Quant-VNPY
├── 应用层 (app/)
│   ├── Flask应用
│   │   ├── 应用初始化 (__init__.py)
│   │   ├── 应用入口 (__main__.py)
│   │   └── 配置管理
│   ├── API模块
│   │   ├── 健康检查 (health.py)
│   │   └── Swagger文档
│   └── 配置文件
│       ├── 基础配置 (config.py)
│       ├── 开发配置 (config_dev.py)
│       ├── 生产配置 (config_prod.py)
│       ├── 测试配置 (config_test.py)
│       └── 配置管理器 (config_manager.py)
├── 核心模块 (internal/)
│   ├── 回测模块 (backtest/)
│   │   ├── 回测引擎 (backtest_engine.py)
│   │   ├── 回测分析器 (backtest_analyzer.py)
│   │   ├── 数据加载器 (data_loader.py)
│   │   ├── 回测策略
│   │   └── API接口
│   ├── 数据模块 (data/)
│   │   └── 股息调整 (dividend_adjustment.py)
│   ├── 数据获取模块 (fetcher/)
│   │   ├── 股票数据获取器 (stock_fetcher.py)
│   │   ├── 数据处理器 (data_processor.py)
│   │   ├── 数据源 (data_sources.py)
│   │   └── API接口
│   ├── 风险评估模块 (risk/)
│   │   ├── 风险评估器 (risk_assessor.py)
│   │   ├── 股票风险管理器 (stock_risk_manager.py)
│   │   ├── VNPY集成 (vnpy_integration.py)
│   │   └── API接口
│   ├── 策略模块 (strategies/)
│   │   ├── 股票策略 (stock_strategies.py)
│   │   ├── 牛市趋势策略 (bull_trend_strategy.py)
│   │   ├── LSTM策略 (lstm_strategy.py)
│   │   ├── 均值回归策略 (mean_reversion_strategy.py)
│   │   └── 海龟交易策略 (turtle_trading_strategy.py)
│   ├── 任务管理模块 (task/)
│   │   ├── 任务管理器 (task_manager.py)
│   │   ├── 任务类型 (tasks.py)
│   │   ├── 股票分析任务
│   │   └── API接口
│   └── 交易模块 (trading/)
│       ├── 账户管理器 (account_manager.py)
│       ├── 成本计算器 (cost_calculator.py)
│       ├── 交易时间 (trading_time.py)
│       ├── 交易模拟器
│       │   ├── 基础模拟器 (simulator.py)
│       │   ├── 策略适配器 (strategy_adapter.py)
│       │   └── VNPY模拟器 (vnpy_simulator.py)
│       └── API接口
├── 命令行工具 (cmd/)
│   └── 主命令行工具 (main.py)
└── 测试模块 (tests/)
    └── 股票交易测试 (test_stock_trading.py)
```

## 模块说明

### 应用层 (app/)
- **Flask应用**：提供Web API接口，集成Swagger文档
- **API模块**：定义API资源，包含健康检查端点
- **配置文件**：管理应用配置，支持不同环境的配置

### 核心模块 (internal/)
- **回测模块**：提供回测功能，支持多种回测策略
- **数据模块**：处理数据相关操作，如股息调整
- **数据获取模块**：获取股票数据，支持多种数据源
- **风险评估模块**：评估交易风险，提供风险指标
- **策略模块**：实现多种交易策略，如牛市趋势、LSTM、均值回归等
- **任务管理模块**：管理和执行任务，如股票分析任务
- **交易模块**：提供交易功能，包含交易模拟器和账户管理

### 命令行工具 (cmd/)
- 提供命令行界面，方便用户执行操作

### 测试模块 (tests/)
- 提供测试用例，确保代码质量

## 技术栈

- **Python**：主要开发语言
- **Flask**：Web框架，提供API接口
- **Flask-RESTX**：RESTful API扩展，支持Swagger文档
- **VNPY**：量化交易库，提供交易和回测功能
- **Pytest**：测试框架

## 主要功能

1. **股票数据获取**：从多种数据源获取股票数据
2. **股票分析**：分析股票数据，评估股票价值
3. **交易策略**：实现多种交易策略，如牛市趋势、LSTM等
4. **回测**：对交易策略进行回测，评估策略性能
5. **风险评估**：评估交易风险，提供风险指标
6. **交易模拟**：模拟交易过程，测试交易策略
7. **任务管理**：管理和执行任务，如股票分析任务
8. **API接口**：提供RESTful API接口，支持Swagger文档
