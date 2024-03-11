from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA
from surmount.data import Asset
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # List of assets you're interested in
        self.assets_to_monitor = ["SPY", "TSLA"]
        # Remember the entry_price for SPY to compare for future trades.
        self.spy_entry_price = None
        
    @property
    def interval(self):
        return "1day"

    @property
    def assets(self):
        # The assets that this strategy will handle
        return self.assets_to_monitor

    @property
    def data(self):
        # Provided data will be just Asset data for our assets
        return [Asset(asset) for asset in self.assets_to_monitor]
    
    def run(self, data):
        # This empty dictionary will hold our target allocations
        allocation_dict = {}
        
        # Access historical close prices for SPY and TSLA
        spy_prices = [record["SPY"]["close"] for record in data["ohlcv"]]
        tsla_prices = [record["TSLA"]["close"] for record in data["ohlcv"]]
        
        # Ensure we have at least one price to look at
        if not spy_prices or not tsla_prices:
            return TargetAllocation({})
        
        # Current prices for comparison
        current_spy_price = spy_prices[-1]
        
        # Purchasing logic
        if self.spy_entry_price is None:  # First time run, buy SPY
            self.spy_entry_price = current_spy_price
            allocation_dict["SPY"] = 1.0  # Allocate 100% to SPY
        else:
            # Check if it's the end of the month to potentially buy TSLA
            current_datetime = data["ohlcv"][-1]["SPY"]["date"]  
            if self._is_end_of_month(current_datetime):
                # Only proceed to buy TSLA if SPY is above our purchase price
                if current_spy_price > self.spy_entry_price:
                    allocation_dict["TSLA"] = 1.0  # Allocate 100% to TSLA
                else:
                    allocation_dict["SPY"] = 1.0  # Keep holding SPY
            else:
                # Not end of the month, maintain the current allocation
                allocation_dict["SPY"] = 1.0  # Keep holding SPY
            
        return TargetAllocation(allocation_dict)

    def _is_end_of_month(self, date_str):
        """
        Helper function to determine if the given date is the end of the month.
        
        :param date_str: The date in string format
        :return: True if it's the end of the month, False otherwise
        """
        from datetime import datetime, timedelta
        current_date = datetime.strptime(date_str, "%Y-%m-%d")
        next_day = current_date + timedelta(days=1)
        return current_date.month != next_day.month