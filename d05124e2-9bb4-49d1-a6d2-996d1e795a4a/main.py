from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import ATR
from surmount.logging import log
import pandas as pd

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the tickers to trade
        self.tickers = ["SPY", "QQQ"]
        # Placeholder for the days to stay in cash after high volatility
        self.cash_hold_days = 10
        # Record of the last day when switched to cash due to high volatility
        self.last_cash_switch = pd.Timestamp.min

    @property
    def interval(self):
        # Using daily data to evaluate strategy
        return "1day"

    @property
    def assets(self):
        # The assets that are being traded
        return self.tickers

    def run(self, data):
        # Check if we are within the cash hold period
        current_date = pd.Timestamp(data["ohlcv"][-1][self.tickers[0]]["date"])
        if (current_date - self.last_cash_switch).days <= self.cash_hold_days:
            # Stay in cash if within the hold period
            return TargetAllocation({})

        allocation_dict = {}
        for ticker in self.tickers:
            # Calculate the 14-day Average True Range (ATR) as a volatility measure
            atr_values = ATR(ticker, data["ohlcv"], 14)
            if atr_values is None:
                # ATR calculation did not return any values, default to no position
                allocation_dict[ticker] = 0
                continue
            
            # Calculate the recent average volatility as a percentage of the price
            recent_price = data["ohlcv"][-1][ticker]["close"]
            recent_volatility = atr_values[-1] / recent_price * 100
            
            if recent_volatility > 10:
                # If recent volatility is above 10%, switch to cash by not allocating
                self.last_cash_switch = current_date
                return TargetAllocation({})
            else:
                # Allocate evenly between SPY and QQQ in other cases
                allocation_dict[ticker] = 0.5
            
        return TargetAllocation(allocation_dict)