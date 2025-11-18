from dataclasses import dataclass
from typing import Union, Optional
from datetime import datetime
from backtester.order.order_base import Order
from backtester.const import OrderSide
from backtester.data.bar_data import BarData


@dataclass
class MarketOrder(Order):
    """
    Market order that fills immediately at the open of the bar (with slippage).
    
    The entry price is set at construction time (typically open + slippage).
    The order becomes live immediately upon creation.
    """
    slippage: float = 0.0  # Slippage in price units (can be positive or negative)
    
    def __post_init__(self):
        """Market orders are live immediately upon creation."""
        if self.entry_time is None:
            # This will be set when the order is created at a specific bar
            pass
        # Market orders start as live (they fill immediately)
        # Note: is_live should be set by the caller after setting entry_time
    
    def update_at_bar(
        self, 
        bar_data: Union[BarData, dict], 
        bar_time: Optional[datetime] = None
    ) -> None:
        """
        Update market order at a new bar.
        
        Market orders are already live, so we just check for exits and update P&L.
        """
        if self.is_closed:
            return

        # Market orders should already be live, but ensure it
        if not self.is_live and self.entry_time is not None:
            self.is_live = True
        
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
    
    @classmethod
    def create_at_bar(
        cls,
        side: OrderSide,
        stop_price: float,
        target_price: float,
        bar_data: Union[BarData, dict],
        bar_time: datetime,
        slippage: float = 0.0,
        quantity: int = 1
    ) -> 'MarketOrder':
        """
        Factory method to create a market order at a specific bar.
        
        The entry price is set to the open of the bar plus slippage.
        For LONG: entry = open + slippage
        For SHORT: entry = open - slippage (slippage is typically positive)
        """

        # Apply slippage: for LONG add slippage, for SHORT subtract slippage
        if side == OrderSide.LONG:
            entry_price = bar_data.open + slippage
        else:  # SHORT
            entry_price = bar_data.open - slippage
        
        order = cls(
            side=side,
            stop_price=stop_price,
            target_price=target_price,
            entry_price=entry_price,
            quantity=quantity,
            slippage=slippage,
            entry_time=bar_time,
            is_live=True  # Market orders fill immediately
        )
        
        return order

