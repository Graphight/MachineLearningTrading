
# Import Libraries
from main.python.MachineLearning.TimeSeriesForecasting.DataCollection import collectAndWriteToCsv
from main.python.MachineLearning.TimeSeriesForecasting.Methods.MultipleSplits import method_multipleSplits
from main.python.MachineLearning.TimeSeriesForecasting.Methods.SlidingWindow import method_slidingWindow

from matplotlib import pyplot


# Setup

market_name = "BTC-ETH"
trade_period = "day"
file_name = "MarketData.csv"
print("Recent closing prices for {} exchange".format(market_name))
collectAndWriteToCsv(market_name, trade_period, file_name)


# Collect and prepare
method_multipleSplits(3, file_name)
# method_slidingWindow(200, file_name)


# Display
pyplot.show()
