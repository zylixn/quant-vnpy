from vnpy_ctastrategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)
from vnpy.trader.constant import Interval
import torch
import torch.nn as nn
import numpy as np
from collections import deque
import joblib


class LSTMStrategy(CtaTemplate):
    """基于LSTM的CTA交易策略"""

    author = "vnpy社区"

    # 可调参数
    lstm_window = 60
    hidden_size = 32
    num_layers = 2
    dropout = 0.2
    predict_threshold = 0.02
    fixed_size = 1

    # 内部变量
    model = None
    scaler = None
    feature_buffer = deque(maxlen=lstm_window)
    last_predict = 0.0

    parameters = [
        "lstm_window",
        "hidden_size",
        "num_layers",
        "dropout",
        "predict_threshold",
        "fixed_size",
    ]
    variables = ["last_predict"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar, interval=Interval.MINUTE)
        self.am = ArrayManager(self.lstm_window + 10)

        # 构建LSTM模型
        self.build_model()

    def build_model(self):
        """构建并加载预训练的LSTM模型"""
        input_size = 5  # close, high, low, volume, open_interest
        self.model = LSTMModel(
            input_size=input_size,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers,
            dropout=self.dropout,
        )
        # 假设模型与scaler已提前训练并保存
        try:
            self.model.load_state_dict(torch.load("lstm_model.pth", map_location="cpu"))
            self.scaler = joblib.load("lstm_scaler.pkl")
            self.model.eval()
            self.write_log("LSTM模型与scaler加载成功")
        except Exception as e:
            self.write_log(f"模型加载失败: {e}")
            self.model = None
            self.scaler = None

    def on_init(self):
        """
        策略初始化回调
        """
        self.write_log("策略初始化")
        self.load_bar(10)

    def on_start(self):
        """
        策略启动回调
        """
        self.write_log("策略启动")

    def on_stop(self):
        """
        策略停止回调
        """
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        """
        收到行情tick推送
        """
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        """
        收到K线推送
        """
        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        # 更新特征缓存
        feature = np.array([
            bar.close_price,
            bar.high_price,
            bar.low_price,
            bar.volume,
            bar.open_interest or 0,
        ]).reshape(1, -1)

        if self.scaler:
            feature = self.scaler.transform(feature).flatten()
        self.feature_buffer.append(feature)

        if len(self.feature_buffer) < self.lstm_window:
            return

        # 预测下一根K线涨跌概率
        if self.model:
            x = np.array(self.feature_buffer).reshape(1, self.lstm_window, -1)
            with torch.no_grad():
                prob = self.model(torch.tensor(x, dtype=torch.float32)).item()
            self.last_predict = prob
            self.put_event()

            # 交易逻辑
            if prob > 0.5 + self.predict_threshold:
                if self.pos == 0:
                    self.buy(bar.close_price + 5, self.fixed_size)
                elif self.pos < 0:
                    self.cover(bar.close_price + 5, abs(self.pos))
                    self.buy(bar.close_price + 5, self.fixed_size)
            elif prob < 0.5 - self.predict_threshold:
                if self.pos == 0:
                    self.short(bar.close_price - 5, self.fixed_size)
                elif self.pos > 0:
                    self.sell(bar.close_price - 5, abs(self.pos))
                    self.short(bar.close_price - 5, self.fixed_size)

    def on_order(self, order: OrderData):
        """
        收到委托推送
        """
        pass

    def on_trade(self, trade: TradeData):
        """
        收到成交推送
        """
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        收到止损单推送
        """
        pass


class LSTMModel(nn.Module):
    """简单的LSTM预测模型"""

    def __init__(self, input_size, hidden_size, num_layers, dropout=0.2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
        )
        self.fc = nn.Linear(hidden_size, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return self.sigmoid(out).squeeze(-1)
