# 股票交易功能使用说明

## 1. 功能概述

本项目实现了完整的股票交易功能，包括：

- **分红除权处理**：支持股票分红、送股、配股等事件的处理，实现前复权和后复权计算
- **交易成本计算**：精确计算股票交易的佣金、印花税、过户费等各项成本
- **资金账户管理**：管理股票持仓、资金变动、资产组合分析
- **交易时间管理**：处理A股、港股、美股交易时间，节假日和停牌股票
- **风险控制**：个股风险、行业风险、市场风险、流动性风险和合规风险控制
- **股票特有策略**：价值投资、成长投资、技术分析、动量、均值回归、波段交易等策略

## 2. 模块说明

### 2.1 分红除权处理模块
**文件**：`internal/data/dividend_adjustment.py`

**功能**：
- `DividendEvent`：分红事件类，处理分红、送股、配股等事件
- `DividendAdjuster`：分红除权调整器，实现前复权和后复权计算
- `StockDataProcessor`：股票数据处理器，处理和转换股票数据

**使用示例**：
```python
from internal.data.dividend_adjustment import DividendAdjuster

adjuster = DividendAdjuster()
adjusted_bars = adjuster.adjust_prices(bars, "forward", "600519")
```

### 2.2 交易成本计算模块
**文件**：`internal/trading/cost_calculator.py`

**功能**：
- `StockTradingCostCalculator`：股票交易成本计算器，计算佣金、印花税、过户费等各项成本

**使用示例**：
```python
from internal.trading.cost_calculator import StockTradingCostCalculator
from vnpy.trader.constant import Direction, Offset, Exchange

calculator = StockTradingCostCalculator()
cost = calculator.calculate_cost(
    price=10.0,
    volume=1000,
    direction=Direction.LONG,
    offset=Offset.OPEN,
    exchange=Exchange.SSE
)
```

### 2.3 资金账户管理模块
**文件**：`internal/trading/account_manager.py`

**功能**：
- `StockPosition`：股票持仓类，管理单个股票的持仓信息
- `StockAccount`：股票账户类，管理资金和持仓
- `PortfolioManager`：资产组合管理器，管理多个账户

**使用示例**：
```python
from internal.trading.account_manager import StockAccount
from vnpy.trader.object import TradeData

account = StockAccount("test_account", 1000000.0)
trade = TradeData(...)
account.update_trade(trade)
```

### 2.4 交易时间管理模块
**文件**：`internal/trading/trading_time.py`

**功能**：
- `TradingTimeConfig`：交易时间配置，定义各市场交易时间
- `HolidayManager`：节假日管理器，处理节假日和补班日
- `TradingTimeManager`：交易时间管理器，判断是否为交易时间
- `MarketCalendar`：市场日历，提供交易日和节假日信息

**使用示例**：
```python
from internal.trading.trading_time import TradingTimeManager
from datetime import datetime

manager = TradingTimeManager()
is_trading = manager.is_trading_time(datetime.now())
```

### 2.5 风险控制模块
**文件**：`internal/risk/stock_risk_manager.py`

**功能**：
- `StockRiskConfig`：股票风险控制配置
- `StockRiskManager`：股票风险管理器，检查订单风险和计算组合风险

**使用示例**：
```python
from internal.risk.stock_risk_manager import StockRiskManager
from vnpy.trader.object import OrderData

manager = StockRiskManager()
risk_check = manager.check_order_risk("default", order)
```

### 2.6 股票特有策略模块
**文件**：`internal/strategies/stock_strategies.py`

**功能**：
- `ValueInvestingStrategy`：价值投资策略
- `GrowthInvestingStrategy`：成长投资策略
- `TechnicalAnalysisStrategy`：技术分析策略
- `MomentumStrategy`：动量策略
- `MeanReversionStrategy`：均值回归策略
- `SwingTradingStrategy`：波段交易策略
- `StockStrategyFactory`：策略工厂，创建和管理策略

**使用示例**：
```python
from internal.strategies.stock_strategies import StockStrategyFactory

strategy = StockStrategyFactory.create_strategy("value_investing", cta_engine, vt_symbol, setting)
```

## 3. 配置说明

### 3.1 配置文件
**文件**：`app/config.py`

**股票交易相关配置**：

- **分红除权配置**：
  - `DIVIDEND_ADJUSTMENT_ENABLED`：是否启用分红除权处理
  - `DIVIDEND_DATA_PATH`：分红数据存储路径
  - `DIVIDEND_UPDATE_INTERVAL`：分红数据更新间隔

- **交易成本配置**：
  - `TRADING_COST_CONFIG`：交易成本配置，包括佣金、印花税、过户费等

- **券商配置**：
  - `BROKER_NAME`：券商名称
  - `BROKER_CONFIG`：券商配置，包括用户ID、密码等

- **股票账户配置**：
  - `ACCOUNT_CONFIG`：账户配置，包括初始资金、最大持仓比例等

- **交易时间配置**：
  - `TRADING_TIME_CONFIG`：交易时间配置，包括市场类型、节假日文件等

- **停牌股票配置**：
  - `SUSPENDED_STOCKS_FILE`：停牌股票文件路径
  - `SUSPENDED_STOCKS_UPDATE_INTERVAL`：停牌股票更新间隔

### 3.2 环境变量

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `DATA_SOURCE` | 数据源 | tushare |
| `DATA_TOKEN` | 数据源token | "" |
| `DATA_CACHE_DIR` | 数据缓存目录 | data/cache |
| `DATA_DOWNLOAD_DIR` | 数据下载目录 | data/download |

## 4. 使用方法

### 4.1 安装依赖

```bash
# 使用 poetry 安装依赖
poetry install

# 或使用 pip 安装依赖
pip install -r requirements.txt
```

### 4.2 运行测试

```bash
# 运行股票交易功能测试
python -m pytest tests/test_stock_trading.py -v
```

### 4.3 运行策略

```bash
# 启动交易引擎
python cmd/main.py

# 或使用 Makefile
make run
```

### 4.4 编译可执行文件

```bash
# 使用 pyinstaller 编译可执行文件
make pyinstaller
```

## 5. 策略使用

### 5.1 价值投资策略

**核心指标**：
- 市盈率（PE）：< 15
- 市净率（PB）：< 1.5
- 净资产收益率（ROE）：> 10%
- 市值：> 100亿
- 现金分红率：> 3%

**配置示例**：
```python
setting = {
    "pe_threshold": 15.0,
    "pb_threshold": 1.5,
    "roe_threshold": 0.1,
    "market_cap_min": 10000000000,
    "cash_dividend_ratio": 0.03,
    "holding_period": 30
}
```

### 5.2 成长投资策略

**核心指标**：
- 营收增长率：> 20%
- 净利润增长率：> 25%
- 每股收益增长率：> 20%
- 销售额增长率：> 15%
- 利润率：> 15%

**配置示例**：
```python
setting = {
    "revenue_growth_threshold": 0.2,
    "earnings_growth_threshold": 0.25,
    "eps_growth_threshold": 0.2,
    "sales_growth_threshold": 0.15,
    "profit_margin_threshold": 0.15
}
```

### 5.3 技术分析策略

**核心指标**：
- 均线多头排列
- MACD金叉
- KDJ金叉
- RSI正常区间
- 布林带中轨上方

**配置示例**：
```python
setting = {
    "ma_fast": 10,
    "ma_medium": 20,
    "ma_slow": 60,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    "kdj_period": 9,
    "kdj_slow": 3,
    "rsi_period": 14,
    "rsi_overbought": 70,
    "rsi_oversold": 30,
    "boll_period": 20,
    "boll_dev": 2
}
```

## 6. 风险控制

### 6.1 个股风险控制
- 单股票最大持仓比例：30%
- 单股票最大日交易次数：50次
- 单股票最大日亏损：5000元

### 6.2 行业风险控制
- 单行业最大持仓比例：50%
- 行业集中度上限：70%

### 6.3 市场风险控制
- 大盘风险阈值：3%
- 大盘风险止损：启用

### 6.4 流动性风险控制
- 最小换手率：1%
- 最小成交量：100000股
- 持仓与成交量比例上限：1%

### 6.5 合规风险控制
- 内幕交易检查：启用
- 市场操纵检查：启用
- 监管持股期：6个月

## 7. 系统架构

### 7.1 模块依赖关系

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  分红除权处理模块   │────>│  交易时间管理模块   │────>│  风险控制模块       │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
          ▲                           ▲                           │
          │                           │                           │
          ▼                           ▼                           ▼
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  交易成本计算模块   │────>│  资金账户管理模块   │────>│  股票特有策略模块   │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
```

### 7.2 数据流

1. **行情数据** → **分红除权处理** → **交易时间检查** → **策略分析**
2. **策略信号** → **风险控制检查** → **订单生成** → **交易成本计算**
3. **成交数据** → **资金账户更新** → **持仓管理** → **资产组合分析**

## 8. 扩展建议

### 8.1 数据源扩展
- 集成更多数据源：Wind、东方财富、同花顺等
- 实现数据自动更新和缓存机制

### 8.2 策略扩展
- 实现更多股票特有策略：因子投资、配对交易、事件驱动等
- 支持策略组合和配置优化

### 8.3 风险控制扩展
- 实现VaR风险评估模型
- 支持压力测试和情景分析

### 8.4 回测系统扩展
- 实现股票特有回测指标：夏普比率、最大回撤、信息比率等
- 支持多策略回测和参数优化

## 9. 注意事项

1. **数据安全**：请妥善保管数据源token和券商账号信息
2. **风险控制**：严格遵守风险控制参数，避免过度交易
3. **合规性**：遵守相关法律法规，避免内幕交易和市场操纵
4. **性能优化**：大数据量回测时注意内存使用和计算性能
5. **监控预警**：定期检查系统运行状态，及时处理异常情况

## 10. 故障排查

### 10.1 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|---------|----------|
| 分红除权计算错误 | 分红数据缺失 | 检查分红数据是否完整 |
| 交易成本计算错误 | 券商费率配置错误 | 检查交易成本配置 |
| 策略不产生信号 | 市场条件不满足 | 调整策略参数或等待合适时机 |
| 风险控制拦截订单 | 风险参数设置过严 | 调整风险控制参数 |
| 交易时间判断错误 | 节假日文件过期 | 更新节假日文件 |

### 10.2 日志查看

```bash
# 查看系统日志
tail -f logs/system.log

# 查看策略日志
tail -f logs/strategy.log
```

## 11. 版本说明

| 版本 | 日期 | 功能更新 |
|------|------|----------|
| v1.0.0 | 2024-01-01 | 初始版本，实现核心股票交易功能 |
| v1.1.0 | 2024-06-01 | 增加风险控制模块和股票特有策略 |
| v1.2.0 | 2024-12-01 | 优化交易时间管理和策略性能 |

## 12. 联系方式

- **作者**：Quant Team
- **邮箱**：quant@example.com
- **GitHub**：https://github.com/quant-team/quant-vnpy

---

**免责声明**：本项目仅用于学习和研究，不构成任何投资建议。投资有风险，入市需谨慎。