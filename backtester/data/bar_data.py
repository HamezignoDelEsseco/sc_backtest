import pandas as pd
from typing import Dict, Any
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class BarData:
    """
    Typed structure for OHLC bar data.
    """
    open: float
    high: float
    low: float
    last: float
    datetime: pd.Timestamp

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BarData':
        assert isinstance(data['datetime'], pd.Timestamp)

        return cls(
            open=float(data['open']),
            high=float(data['high']),
            low=float(data['low']),
            last=float(data.get('last')),
            datetime=data['datetime']
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
