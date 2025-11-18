from dataclasses import dataclass
from backtester.order.order_base import Order
from backtester.const import OrderSide
from backtester.data.bar_data import BarData


@dataclass
class LimitOrder(Order):
    def _set_live_status_at_bar(self, bar_data: BarData) -> None :
        if self.is_live:
            return

        if self.side == OrderSide.LONG:
            self.is_live = bar_data.high > self.entry_price

        else:
            self.is_live = bar_data.low < self.entry_price
    
    def update_at_bar(self, bar_data: BarData) -> None:
        if self.is_closed:
            return

        self._set_live_status_at_bar(bar_data)

        # If not yet live, check if limit is touched
        if not self.is_live:
            if self._check_limit_touched(bar_data):
                # Limit touched, order becomes live
                self.is_live = True
                if self.entry_time is None:
                    self.entry_time = bar_time if bar_time is not None else datetime.now()
                # Entry price is already set (the limit price)
            else:
                # Limit not touched, order remains inactive
                return
        
        # Order is live, check for exits and update P&L
        # Check if stop or target is hit (stop has priority)
        stop_hit, stop_price = self._check_stop_hit_at_bar(bar_data)
        target_hit, target_price = self._check_target_hit_at_bar(bar_data)
        
        if stop_hit:
            # Stop loss hit
            self.is_closed = True
            self.is_live = False
            self.exit_price = stop_price
            self.exit_time = bar_time if bar_time is not None else datetime.now()
            self.closed_pl = self._calculate_pl_at_bar(stop_price)
            self.open_pl = 0.0
        elif target_hit:
            # Target hit
            self.is_closed = True
            self.is_live = False
            self.exit_price = target_price
            self.exit_time = bar_time if bar_time is not None else datetime.now()
            self.closed_pl = self._calculate_pl_at_bar(target_price)
            self.open_pl = 0.0
        else:
            # Order still open, update P&L stats
            self._set_pl_stats(bar_data)

