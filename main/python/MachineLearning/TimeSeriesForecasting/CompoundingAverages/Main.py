# Import Libraries
from requests import get
from csv import DictWriter
from decimal import Decimal


def collectAndWriteToCsv(marketName, period, fileName):

    # Setup
    url = 'https://bittrex.com/api/v2.0/pub/market/getTicks?marketName={}&tickInterval={}'.format(marketName, period)
    decimalPlaces = Decimal(10) ** -8

    # Collect
    response = get(url)
    print("Response status code: {}".format(response.status_code))


    # Write to file
    with open(fileName, "w", newline="") as csvfile:
        fieldNames = ["TimeStamp", "ClosingPrice"]
        writer = DictWriter(csvfile, fieldnames=fieldNames)
        writer.writeheader()

        for tick in response.json()["result"]:
            writer.writerow({"TimeStamp": tick["T"][0:10], "ClosingPrice": Decimal(tick["C"]).quantize(decimalPlaces)})


def main():
    # Setup
    market_name = "ETH-LTC"
    trade_period = "second"
    file_name = "MarketData-Seconds-{}.csv".format(market_name)
    window_size = 100
    print("Recent closing prices for {} exchange".format(market_name))
    collectAndWriteToCsv(market_name, trade_period, file_name)

    # Collect and prepare
    data = read_csv(file_name, parse_dates=["TimeStamp"], index_col="TimeStamp")
    # method_multipleSplits(3, file_name)
    # method_slidingWindow(100, file_name)

    # ===== Stationarity =====
    test_stationarity(data, window_size)
    # movingAverage(data, window_size)
    # exponentialWeighted(data, window_size)
    # ts_log_diff = differencing_log(data, window_size)
    # ts_raw_diff = differencing_raw(data, window_size)
    # ts_log_decompose = decomposing(data, window_size)

    # ===== Forecasting =====
    # function_autocorrelation(data, window_size)
    # function_partial_autocorrelation(data, window_size)
    # model_ar(data, window_size)
    # model_ma(data, window_size)
    model_combined(data, window_size)
    # predictions(data, window_size)
    predictions_better(data, window_size)

    # Display
    # pyplot.plot(data)
    pyplot.show()
