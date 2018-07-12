
# Import Libraries
import numpy

from main.python.MachineLearning.TimeSeriesForecasting.Methods.Stationarity import test_stationarity, movingAverage, \
    exponentialWeighted

from pandas import read_csv

from matplotlib.pylab import rcParams
rcParams["figure.figsize"] = 15, 6


def method_slidingWindow(window_size, file_name):
    data = read_csv(file_name, parse_dates=["TimeStamp"], index_col="TimeStamp")
    # test_stationarity(data, window_size)
    exponentialWeighted(data, window_size)

    # data = series.values
    # front = 0
    # for i in range(window_size, len(data)):
    #     train, test = data[front:i], data[i:i+1]
    #     print("Training observations: {}".format(len(train)))
    #     print("Testing observations: {}".format(len(test)))
    #     print("Total observations: {}\n".format(len(train) + len(test)))
    #     pyplot.plot(train)
    #     pyplot.plot([None for x in train] + [y for y in test])
    #     front += 1
