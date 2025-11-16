from typing import List
from abc import ABC, abstractmethod
from openVVA.trade.trade_base import Trade
from openVVA.trade.trade_group import TradeGroup

class StrategyBase(ABC):

    def __init__(self, name):
        self.trades: TradeGroup
        self.name = name
        self.open_trades: List[Trade] = []
        self.closed_trades: List[Trade] = []

    @abstractmethod
    def build_trades(self, **kwargs):
        # Build the order group here
        pass

    def update_trades(self, **kwargs):
        # Calls the individual order updates
        pass


    def on_new_bar(self, bar_time, row):
        """Called by engine for each bar."""
        self.manage_open_trades(bar_time, row)
        self.check_entry(bar_time, row)

    def manage_open_trades(self, bar_time, row):
        bar_high = row["high"]
        bar_low = row["low"]

        for trade in list(self.open_trades):
            if trade.check_exit(bar_time, bar_high, bar_low):
                self.open_trades.remove(trade)
                self.closed_trades.append(trade)

    @abstractmethod
    def check_entry(self, bar_time, row):
        """Strategies override this."""
        pass

    def open_trade(self, trade: Trade):
        self.open_trades.append(trade)

    def all_trades(self):
        return self.closed_trades + self.open_trades
