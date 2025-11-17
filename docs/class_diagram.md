# Backtester Class Diagram

This document shows the UML class diagram for the backtester framework.

```mermaid
classDiagram
    class OrderSide {
        <<enumeration>>
        LONG
        SHORT
    }

    class BarData {
        <<dataclass>>
        +float open
        +float high
        +float low
        +Optional[float] close
        +Optional[pd.Timestamp] datetime
        +float last
        +from_dict(data: Dict) BarData
        +from_dataclass(obj: Any) BarData
        +to_dict() Dict
    }

    class Order {
        <<abstract>>
        +OrderSide side
        +float stop_price
        +float target_price
        +float entry_price
        +int quantity
        +bool is_closed
        +bool is_live
        +pd.Timestamp entry_time
        +pd.Timestamp exit_time
        +float exit_price
        +float closed_pl
        +float open_pl
        +float max_open_pl
        +float min_open_pl
        +_calculate_pl(price: float) float
        +_check_stop_hit(bar_data: BarData) Tuple[bool, Optional[float]]
        +_check_target_hit(bar_data: BarData) Tuple[bool, Optional[float]]
        +_update_pl_stats(bar_data: BarData) None
        +update_at_bar(bar_data: Union[BarData, dict], bar_time: Optional[pd.Timestamp]) None*
    }

    class MarketOrder {
        <<dataclass>>
        +float slippage
        +update_at_bar(bar_data: Union[BarData, dict], bar_time: Optional[pd.Timestamp]) None
        +create_at_bar(side: OrderSide, stop_price: float, target_price: float, bar_data: Union[BarData, dict], bar_time: pd.Timestamp, slippage: float, quantity: int) MarketOrder
    }

    class LimitOrder {
        <<dataclass>>
        +_check_limit_touched(bar_data: BarData) bool
        +update_at_bar(bar_data: Union[BarData, dict], bar_time: Optional[pd.Timestamp]) None
    }

    OrderSide --> Order : uses
    Order <|-- MarketOrder : extends
    Order <|-- LimitOrder : extends
    BarData --> Order : used by
    Order ..> BarData : updates with
```

## Class Descriptions

### OrderSide (Enum)
Enumeration for order direction:
- `LONG`: Long position
- `SHORT`: Short position

### BarData (Dataclass)
Typed structure for OHLC bar data with IDE autocompletion support:
- Core fields: `open`, `high`, `low`, `close`, `datetime`
- Property: `last` (alias for `close`)
- Factory methods: `from_dict()`, `from_dataclass()`
- Conversion: `to_dict()`

### Order (Abstract Base Class)
Base class for all trading orders:
- Tracks order status (`is_live`, `is_closed`)
- Tracks P&L statistics (`open_pl`, `closed_pl`, `max_open_pl`, `min_open_pl`)
- Assumes worst-case OHLC ordering for fills
- Abstract method: `update_at_bar()` must be implemented by subclasses

### MarketOrder
Market order that fills immediately:
- Entry price = bar open ± slippage
- Becomes live immediately upon creation
- Factory method: `create_at_bar()` for convenient creation

### LimitOrder
Limit order that activates when price touches limit:
- Entry price is the limit price (known at construction)
- Starts inactive until limit is touched
- Becomes live when price touches limit within a bar

## Relationships

- **OrderSide → Order**: Orders use `OrderSide` enum to specify direction
- **Order ← MarketOrder/LimitOrder**: Both order types extend the abstract `Order` class
- **BarData → Order**: Orders use `BarData` objects to update their state
- **Order ..> BarData**: Orders receive `BarData` as input for updates (dependency)


