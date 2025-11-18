from tarfile import TruncatedHeaderError

import pandas as pd
import pytest
from backtester.data.bar_data import BarData
from backtester.order.order_base import Order
from backtester.const import OrderSide, LevelHit


class DummyOrder(Order):
    """Concrete implementation for testing abstract Order base class."""

    def _set_live_status_at_bar(self, bar_data: BarData) -> None:
        self.is_live = True


def make_bar(high: float, low: float, last: float = 0., open_price: float = 0.) -> BarData:
    return BarData(
        open=open_price,
        high=high,
        low=low,
        last=last,
        datetime=pd.Timestamp("2024-01-01 10:00:00"),
    )


def create_order(**kwargs) -> DummyOrder:
    params = dict(
        side=OrderSide.LONG,
        stop_price=95.0,
        target_price=110.0,
        entry_price=100.0,
        quantity=1,
    )
    params.update(kwargs)
    return DummyOrder(**params)


def test_calculate_pl_at_bar_long():
    h, l, last, e = 110, 95, 109, 100
    order = create_order(quantity=2, entry_price=e)
    bar = make_bar(high=h, low=l, last=last)

    pl_best, pl_worse, pl_last  = order._calculate_pl_at_bar(bar)

    assert pl_worse == (l - e) * 2
    assert pl_best == (h - e) * 2
    assert pl_last == (last - e) * 2


def test_calculate_pl_at_bar_short():
    h, l, last, e = 110, 95, 109, 100
    order = create_order(quantity=2, entry_price=e, side=OrderSide.SHORT)
    bar = make_bar(high=h, low=l, last=last)

    pl_best, pl_worse, pl_last  = order._calculate_pl_at_bar(bar)

    assert pl_best == -(l - e) * 2
    assert pl_worse == -(h - e) * 2
    assert pl_last == -(last - e) * 2


@pytest.mark.parametrize(
    "side,low,entry,high,hit",
    [
        (OrderSide.LONG, 94.0, 100, 105.0, LevelHit.STOP),
        (OrderSide.LONG, 95.0, 100, 105.0, LevelHit.STOP),
        (OrderSide.LONG, 96.0, 100, 105.0, LevelHit.NOHIT),
        (OrderSide.LONG, 96.0, 100, 110.0, LevelHit.NOHIT),
        (OrderSide.LONG, 96.0, 100, 111.0, LevelHit.TARGET),

        (OrderSide.SHORT, 95.0, 100, 111.0, LevelHit.STOP),
        (OrderSide.SHORT, 95.0, 100, 110.0, LevelHit.STOP),
        (OrderSide.SHORT, 95.0, 100, 109.0, LevelHit.NOHIT),
        (OrderSide.SHORT, 90.0, 100, 109.0, LevelHit.NOHIT),
        (OrderSide.SHORT, 89.0, 100, 109.0, LevelHit.TARGET),

    ],
)
def test_get_exit_status_at_bar(side, low, entry, high, hit):
    stop = 95.0 if side == OrderSide.LONG else 110.0
    target = 110.0 if side == OrderSide.LONG else 90.0
    order = create_order(entry_price=entry, side=side, stop_price=stop, target_price=target)
    bar = make_bar(high=high, low=low)

    is_hit, *_ = order._get_exit_status_at_bar(bar)

    assert is_hit is hit

@pytest.mark.parametrize(
    "side,low,entry,high,hit,exit_pl",
    [
        (OrderSide.LONG, 94.0, 100, 105.0, LevelHit.STOP, -5),
        (OrderSide.LONG, 95.0, 100, 105.0, LevelHit.STOP, -5),
        (OrderSide.LONG, 96.0, 100, 105.0, LevelHit.NOHIT, None),
        (OrderSide.LONG, 96.0, 100, 110.0, LevelHit.NOHIT, None),
        (OrderSide.LONG, 96.0, 100, 111.0, LevelHit.TARGET, 10),

        (OrderSide.SHORT, 95.0, 100, 111.0, LevelHit.STOP, -10),
        (OrderSide.SHORT, 95.0, 100, 110.0, LevelHit.STOP, -10),
        (OrderSide.SHORT, 95.0, 100, 109.0, LevelHit.NOHIT, None),
        (OrderSide.SHORT, 90.0, 100, 109.0, LevelHit.NOHIT, None),
        (OrderSide.SHORT, 89.0, 100, 109.0, LevelHit.TARGET, 10),

    ],
)
def test_set_exit_status_at_bar(side, low, entry, high, hit, exit_pl):
    stop = 95.0 if side == OrderSide.LONG else 110.0
    target = 110.0 if side == OrderSide.LONG else 90.0
    order = create_order(entry_price=entry, side=side, stop_price=stop, target_price=target)
    bar = make_bar(high=high, low=low)

    order._set_exit_status_at_bar(bar)
    assert order.exit_pl == exit_pl
    assert order.level_hit == hit

@pytest.mark.parametrize(
    "side,low,entry,high,hit,min_pl,max_pl",
    [
        (OrderSide.LONG, 94.0, 100, 105.0, LevelHit.STOP, -5, 5),
        (OrderSide.LONG, 95.0, 100, 105.0, LevelHit.STOP, -5, 5),
        (OrderSide.LONG, 96.0, 100, 105.0, LevelHit.NOHIT, -4, 5),
        (OrderSide.LONG, 96.0, 100, 110.0, LevelHit.NOHIT, -4, 10),
        (OrderSide.LONG, 96.0, 100, 111.0, LevelHit.TARGET, -4, 10),

        (OrderSide.SHORT, 95.0, 100, 111.0, LevelHit.STOP, -10, 5),
        (OrderSide.SHORT, 95.0, 100, 110.0, LevelHit.STOP, -10, 5),
        (OrderSide.SHORT, 95.0, 100, 109.0, LevelHit.NOHIT, -9, 5),
        (OrderSide.SHORT, 90.0, 100, 109.0, LevelHit.NOHIT, -9, 10),
        (OrderSide.SHORT, 89.0, 100, 109.0, LevelHit.TARGET, -9, 10),

    ],
)
def test_set_pl_stats(side, low, entry, high, hit, min_pl, max_pl):
    stop = 95.0 if side == OrderSide.LONG else 110.0
    target = 110.0 if side == OrderSide.LONG else 90.0
    order = create_order(entry_price=entry, side=side, stop_price=stop, target_price=target)
    bar = make_bar(high=high, low=low)
    order._set_pl_stats(bar)
    assert order.min_open_pl == min_pl
    assert order.max_open_pl == max_pl


def test_update_at_bar():
    order = create_order(entry_price=100, side=OrderSide.LONG, stop_price=80, target_price=120)
    bar1 = make_bar(high=105, low=90, last=95)
    bar2 = make_bar(high=104, low=89, last=95)
    bar3 = make_bar(high=140, low=70, last=100)

    assert order.is_live == False

    # bar1
    order.update_at_bar(bar1)
    assert order.is_live == True
    assert order.is_closed == False
    assert order.max_open_pl == 5
    assert order.min_open_pl == -10
    assert order.bar_close_pl == -5
    assert order.level_hit == LevelHit.NOHIT
    assert order.exit_pl is None

    # bar2
    order.update_at_bar(bar2)
    assert order.is_live == True
    assert order.is_closed == False
    assert order.max_open_pl == 5
    assert order.min_open_pl == -11
    assert order.level_hit == LevelHit.NOHIT
    assert order.exit_pl is None

    # bar3
    order.update_at_bar(bar3)
    assert order.is_live == False
    assert order.is_closed == True
    assert order.max_open_pl == 20
    assert order.min_open_pl == -20
    assert order.level_hit == LevelHit.STOP
    assert order.exit_pl == -20
