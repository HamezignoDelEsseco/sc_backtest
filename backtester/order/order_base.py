from pandas import Timestamp
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Tuple, Optional, Union
from backtester.data.bar_data import BarData
from backtester.const import OrderSide, LevelHit


@dataclass
class Order(ABC):
    """
    Base class for trading orders.
    
    Orders track their status and P&L statistics. They assume worst-case
    OHLC ordering (non-favorable fills) when updating at each bar.
    """
    side: OrderSide
    stop_price: float
    target_price: float
    entry_price: float = None
    quantity: int = 1
    
    # Status tracking
    is_closed: bool = False
    is_live: bool = False
    exit_price: float = None
    level_hit: LevelHit = LevelHit.NOHIT

    # P&L tracking
    bar_close_pl: float = None
    max_open_pl: float = None
    min_open_pl: float = None
    exit_pl: float = None


    @property
    def sign(self) -> int:
        return 1 if self.side == OrderSide.LONG else -1

    def _calculate_pl_at_bar(self, bar: BarData) -> Tuple[float, float, float]:
        if self.side == OrderSide.LONG:
            max_pl = (bar.high - self.entry_price) * self.quantity
            worse_pl = (bar.low - self.entry_price) * self.quantity
            close_pl = (bar.last - self.entry_price) * self.quantity
        else:
            max_pl = (self.entry_price - bar.low) * self.quantity
            worse_pl = (self.entry_price - bar.high) * self.quantity
            close_pl = (self.entry_price - bar.last) * self.quantity

        return max_pl, worse_pl, close_pl

    def _get_exit_status_at_bar(self, bar_data: BarData) -> Tuple[LevelHit, Union[float, None]]:
        if self.side == OrderSide.LONG:
            if bar_data.low <= self.stop_price:
                return LevelHit.STOP, self.stop_price

            if bar_data.high > self.target_price:
                return LevelHit.TARGET, self.target_price

        if self.side == OrderSide.SHORT:
            if bar_data.low < self.target_price:
                return LevelHit.TARGET, self.target_price

            if bar_data.high >= self.stop_price:
                return LevelHit.STOP, self.stop_price

        return LevelHit.NOHIT, None

    def _set_exit_status_at_bar(self, bar_data: BarData) -> None:
        level_hit, exit_price = self._get_exit_status_at_bar(bar_data)
        self.level_hit = level_hit
        self.exit_price = exit_price

        if level_hit != LevelHit.NOHIT:
            self.is_closed = True
            self.is_live = False
            sign = 1 if  self.side == OrderSide.LONG else -1
            self.exit_pl = sign * (exit_price - self.entry_price)

    def _set_pl_stats(self, bar_data: BarData) -> None:
        """
        Sets the target-aware P&L stats, meaning the best and worse P&L can never exceed the ones defined by the target and stop
        """
        best, worse, close = self._calculate_pl_at_bar(bar_data)
        real_worse = self.sign * (self.stop_price - self.entry_price)
        real_best = self.sign * (self.target_price - self.entry_price)

        target_aware_best = min(best, real_best)
        target_aware_worse = max(worse, real_worse)
        self.bar_close_pl = close

        # Track max and min open P&L
        if self.max_open_pl is None:
            self.max_open_pl = target_aware_best

        if self.min_open_pl is None:
            self.min_open_pl = target_aware_worse

        self.max_open_pl = max(self.max_open_pl, target_aware_best)
        self.min_open_pl = min(self.min_open_pl, target_aware_worse)

    @abstractmethod
    def _set_live_status_at_bar(self, bar: BarData) -> None:
        """Updates the is_live flag"""
        return

    def update_at_bar(self, bar_data: BarData) -> None:
        if self.is_closed:
            return

        if not self.is_live:
            self._set_live_status_at_bar(bar_data)

        if self.is_live:
            assert self.entry_price is not None, "When order is live, the entry price must be set"
            self._set_pl_stats(bar_data)
            self._set_exit_status_at_bar(bar_data)
