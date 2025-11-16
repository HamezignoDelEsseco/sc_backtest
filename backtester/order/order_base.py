import pandas as pd
from dataclasses import dataclass
from backtester.const import OrderSide

@dataclass
class Order:
    side: OrderSide
    stop_price: float
    target_price: float

    exit_time: pd.Timestamp = None
    entry_time: pd.Timestamp = None
    entry_price: float = None
    exit_price: float = None
    closed: bool = False
    pnl_points: float = 0.0
    live: bool = False

    def trade_live(self, entry_price): # Will be relevant for limit orders
        self.entry_price = entry_price
        self.live = True

    def check_exit(self, **bardata):
        if self.closed:
            return False

        # Be very conservative with trades success / loss
        # - Price must cross for target to hit
        # - Assumes worst price hits first
        pass

    # Computes the PL and sets the exit to true if the conditions match
    def close_trade(self, **bardata):
        pass
