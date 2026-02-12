"""
回测结果分析器
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
try:
    import matplotlib.pyplot as plt
except ImportError:
    # 如果matplotlib不存在，设置为None
    plt = None
from vnpy.trader.object import TradeData
from vnpy.trader.constant import Direction


class BacktestAnalyzer:
    """回测结果分析器"""
    
    def __init__(self, backtest_results: Optional[Dict[str, Any]] = None):
        """初始化分析器"""
        self.backtest_results = backtest_results
        self.statistics = {}
        self.trades = []
    
    def set_backtest_results(self, backtest_results: Dict[str, Any]):
        """设置回测结果"""
        self.backtest_results = backtest_results
    
    def set_trades(self, trades: List[TradeData]):
        """设置成交记录"""
        self.trades = trades
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """计算统计指标"""
        if not self.backtest_results:
            return {}
        
        # 计算基本指标
        equity_curve = self.backtest_results
        
        # 计算累计收益率
        total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
        
        # 计算年化收益率
        days = (equity_curve.index[-1] - equity_curve.index[0]).days
        annual_return = (1 + total_return) ** (365 / days) - 1
        
        # 计算最大回撤
        drawdown = (equity_curve / equity_curve.cummax()) - 1
        max_drawdown = drawdown.min()
        
        # 计算夏普比率
        daily_returns = equity_curve.pct_change()
        sharpe_ratio = np.sqrt(252) * daily_returns.mean() / daily_returns.std()
        
        # 计算索提诺比率
        negative_returns = daily_returns[daily_returns < 0]
        sortino_ratio = np.sqrt(252) * daily_returns.mean() / negative_returns.std()
        
        # 计算卡马比率
        calmar_ratio = annual_return / abs(max_drawdown)
        
        # 计算胜率
        if self.trades:
            winning_trades = [t for t in self.trades if t.pnl > 0]
            win_rate = len(winning_trades) / len(self.trades)
        else:
            win_rate = 0
        
        self.statistics = {
            "total_return": total_return,
            "annual_return": annual_return,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
            "sortino_ratio": sortino_ratio,
            "calmar_ratio": calmar_ratio,
            "win_rate": win_rate,
            "total_trades": len(self.trades),
            "start_date": equity_curve.index[0],
            "end_date": equity_curve.index[-1]
        }
        
        return self.statistics
    
    def analyze_trades(self) -> Dict[str, Any]:
        """分析成交记录"""
        if not self.trades:
            return {}
        
        # 计算每笔交易的盈亏
        pnls = [t.pnl for t in self.trades]
        
        # 计算交易统计
        trade_analysis = {
            "total_trades": len(self.trades),
            "average_pnl": np.mean(pnls),
            "median_pnl": np.median(pnls),
            "max_profit": max(pnls),
            "max_loss": min(pnls),
            "winning_trades": len([p for p in pnls if p > 0]),
            "losing_trades": len([p for p in pnls if p < 0]),
            "breakeven_trades": len([p for p in pnls if p == 0])
        }
        
        # 计算持仓时间
        if hasattr(self.trades[0], 'trade_time'):
            hold_times = []
            for i in range(1, len(self.trades)):
                if self.trades[i].direction != self.trades[i-1].direction:
                    hold_time = (self.trades[i].trade_time - self.trades[i-1].trade_time).total_seconds() / 3600
                    hold_times.append(hold_time)
            
            if hold_times:
                trade_analysis["average_hold_time"] = np.mean(hold_times)
                trade_analysis["median_hold_time"] = np.median(hold_times)
        
        return trade_analysis
    
    def plot_equity_curve(self, filename: Optional[str] = None):
        """绘制资金曲线"""
        if not self.backtest_results:
            return
        
        plt.figure(figsize=(12, 6))
        plt.plot(self.backtest_results)
        plt.title('Equity Curve')
        plt.xlabel('Date')
        plt.ylabel('Equity')
        plt.grid(True)
        
        if filename:
            plt.savefig(filename)
        else:
            plt.show()
        
        plt.close()
    
    def plot_drawdown(self, filename: Optional[str] = None):
        """绘制回撤曲线"""
        if not self.backtest_results:
            return
        
        drawdown = (self.backtest_results / self.backtest_results.cummax()) - 1
        
        plt.figure(figsize=(12, 6))
        plt.plot(drawdown)
        plt.title('Drawdown')
        plt.xlabel('Date')
        plt.ylabel('Drawdown')
        plt.grid(True)
        
        if filename:
            plt.savefig(filename)
        else:
            plt.show()
        
        plt.close()
    
    def plot_trade_distribution(self, filename: Optional[str] = None):
        """绘制交易分布"""
        if not self.trades:
            return
        
        # 计算每笔交易的盈亏
        pnls = [t.pnl for t in self.trades]
        
        plt.figure(figsize=(12, 6))
        plt.hist(pnls, bins=50)
        plt.title('Trade P&L Distribution')
        plt.xlabel('P&L')
        plt.ylabel('Frequency')
        plt.grid(True)
        
        if filename:
            plt.savefig(filename)
        else:
            plt.show()
        
        plt.close()
    
    def export_report(self, filename: str = "backtest_report.json"):
        """导出回测报告"""
        report = {
            "statistics": self.calculate_statistics(),
            "trade_analysis": self.analyze_trades(),
            "trades": [{
                "trade_id": t.trade_id,
                "symbol": t.symbol,
                "direction": t.direction.value,
                "offset": t.offset.value,
                "price": t.price,
                "volume": t.volume,
                "trade_time": t.trade_time.isoformat(),
                "pnl": t.pnl,
                "commission": t.commission
            } for t in self.trades]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    def generate_summary(self) -> str:
        """生成回测总结"""
        stats = self.calculate_statistics()
        trade_analysis = self.analyze_trades()
        
        summary = f"""回测总结报告

基本信息
--------
开始日期: {stats.get('start_date')}
结束日期: {stats.get('end_date')}
总交易次数: {stats.get('total_trades')}

绩效指标
--------
总收益率: {stats.get('total_return', 0):.2%}
年化收益率: {stats.get('annual_return', 0):.2%}
最大回撤: {stats.get('max_drawdown', 0):.2%}
夏普比率: {stats.get('sharpe_ratio', 0):.2f}
索提诺比率: {stats.get('sortino_ratio', 0):.2f}
卡马比率: {stats.get('calmar_ratio', 0):.2f}
胜率: {stats.get('win_rate', 0):.2%}

交易分析
--------
平均盈亏: {trade_analysis.get('average_pnl', 0):.2f}
中位数盈亏: {trade_analysis.get('median_pnl', 0):.2f}
最大盈利: {trade_analysis.get('max_profit', 0):.2f}
最大亏损: {trade_analysis.get('max_loss', 0):.2f}
盈利交易: {trade_analysis.get('winning_trades', 0)}
亏损交易: {trade_analysis.get('losing_trades', 0)}
平本交易: {trade_analysis.get('breakeven_trades', 0)}
"""
        
        return summary


class ReportGenerator:
    """报告生成器"""
    
    @staticmethod
    def generate_html_report(analyzer: BacktestAnalyzer, filename: str = "backtest_report.html"):
        """生成HTML报告"""
        summary = analyzer.generate_summary()
        
        html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>回测报告</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
        }}
        h1, h2, h3 {{
            color: #333;
        }}
        .summary {{
            background-color: #f5f5f5;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .stats {{
            background-color: #e8f4f8;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .trades {{
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
    </style>
</head>
<body>
    <h1>回测报告</h1>
    
    <div class="summary">
        <h2>摘要</h2>
        <pre>{summary}</pre>
    </div>
    
    <div class="stats">
        <h2>详细统计</h2>
        <table>
            <tr>
                <th>指标</th>
                <th>值</th>
            </tr>
            <tr>
                <td>总收益率</td>
                <td>{analyzer.statistics.get('total_return', 0):.2%}</td>
            </tr>
            <tr>
                <td>年化收益率</td>
                <td>{analyzer.statistics.get('annual_return', 0):.2%}</td>
            </tr>
            <tr>
                <td>最大回撤</td>
                <td>{analyzer.statistics.get('max_drawdown', 0):.2%}</td>
            </tr>
            <tr>
                <td>夏普比率</td>
                <td>{analyzer.statistics.get('sharpe_ratio', 0):.2f}</td>
            </tr>
            <tr>
                <td>索提诺比率</td>
                <td>{analyzer.statistics.get('sortino_ratio', 0):.2f}</td>
            </tr>
            <tr>
                <td>卡马比率</td>
                <td>{analyzer.statistics.get('calmar_ratio', 0):.2f}</td>
            </tr>
            <tr>
                <td>胜率</td>
                <td>{analyzer.statistics.get('win_rate', 0):.2%}</td>
            </tr>
            <tr>
                <td>总交易次数</td>
                <td>{analyzer.statistics.get('total_trades', 0)}</td>
            </tr>
        </table>
    </div>
    
    <div class="trades">
        <h2>交易记录</h2>
        <table>
            <tr>
                <th>交易ID</th>
                <th>合约</th>
                <th>方向</th>
                <th>开平</th>
                <th>价格</th>
                <th>数量</th>
                <th>时间</th>
                <th>盈亏</th>
                <th>佣金</th>
            </tr>
            {''.join([f'<tr><td>{t.trade_id}</td><td>{t.symbol}</td><td>{t.direction.value}</td><td>{t.offset.value}</td><td>{t.price:.2f}</td><td>{t.volume}</td><td>{t.trade_time}</td><td>{t.pnl:.2f}</td><td>{t.commission:.2f}</td></tr>' for t in analyzer.trades[:100]])}
        </table>
    </div>
</body>
</html>
        """
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_template)
    
    @staticmethod
    def generate_pdf_report(analyzer: BacktestAnalyzer, filename: str = "backtest_report.pdf"):
        """生成PDF报告"""
        try:
            from fpdf import FPDF
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # 添加标题
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="回测报告", ln=1, align="C")
            
            # 添加摘要
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, txt="摘要", ln=1)
            
            pdf.set_font("Arial", size=12)
            summary = analyzer.generate_summary()
            pdf.multi_cell(0, 5, txt=summary)
            
            # 添加详细统计
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, txt="详细统计", ln=1)
            
            pdf.set_font("Arial", size=12)
            stats = analyzer.calculate_statistics()
            for key, value in stats.items():
                if isinstance(value, float):
                    pdf.cell(100, 10, txt=f"{key}:", ln=0)
                    pdf.cell(100, 10, txt=f"{value:.2f}", ln=1)
                else:
                    pdf.cell(100, 10, txt=f"{key}:", ln=0)
                    pdf.cell(100, 10, txt=str(value), ln=1)
            
            pdf.output(filename)
        except ImportError:
            print("请安装fpdf库以生成PDF报告")
