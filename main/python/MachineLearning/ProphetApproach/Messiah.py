
# Import Libraries
import warnings
import itertools
import numpy as np
import matplotlib.pyplot as plt
from pylab import rcParams

import pandas as pd
import statsmodels.api as sm
import matplotlib

from fbprophet import Prophet

from main.python.MachineLearning.ProphetApproach.FunctionsData import collect_and_write_to_csv
from main.python.MachineLearning.ProphetApproach.FunctionsModel import determine_best_p_d_q_variables


# =================================================
#  ========== PRELIM : CONFIG MATPLOTLIB ==========
# =================================================
warnings.filterwarnings("ignore")
plt.style.use("fast")
matplotlib.rcParams["axes.labelsize"] = 14
matplotlib.rcParams["xtick.labelsize"] = 12
matplotlib.rcParams["ytick.labelsize"] = 12
matplotlib.rcParams["text.color"] = "k"
rcParams["figure.figsize"] = 18, 8


# =================================================
#     ========== STEP ONE : GET DATA ==========
# =================================================
currency_from = "NZD"
currency_to = "USD"
interval = "1min"
file_name = "MarketData-{}-{}-{}-interval.csv".format(currency_from, currency_to, interval)
collect_and_write_to_csv(currency_from, currency_to, interval, file_name)
df = pd.read_csv(file_name)

graph_title = "{} -> {} Timeseries".format(currency_from, currency_to)
graph_x_label = "Timestamp"
graph_y_label = "Closing Price"


# =================================================
#   ========== STEP TWO : PROCESS DATA ==========
# =================================================
cols_to_drop = ["Open", "High", "Low", "Difference", "Stagnated", "Increased", "Decreased"]
df.drop(cols_to_drop, axis=1, inplace=True)
df = df.sort_values(["Timestamp"])
df = df.set_index(["Timestamp"])
df.index = pd.to_datetime(df.index)

# Take a peek at the graph
# df.plot(figsize=(15, 6))
# plt.show()

# Take a gander at Dicky-Fuller stuff
decomposition = sm.tsa.seasonal_decompose(df, model="additive", freq=1)
decomposition.plot()


# =================================================
# ========== STEP THREE : MODEL CREATION ==========
# =================================================
# model = determine_best_p_d_q_variables(sample_data)
# results = model.fit(disp=False)
# print(results.summary().tables[1])
# results.plot_diagnostics(figsize=(16, 8))
# plt.show()

# Use Facebook"s -Prophet-
prophet_df = pd.DataFrame({"ds": df.index, "y": df["Close"].values})
prophet_model = Prophet(interval_width=0.95)
prophet_model.fit(prophet_df)


# =================================================
#   ========== STEP FOUR : PREDICTIONS ==========
# =================================================
prophet_forecast = prophet_model.make_future_dataframe(periods=60, freq="1min")
prophet_forecast = prophet_model.predict(prophet_forecast)

plt.figure(figsize=(18, 6))
prophet_model.plot(prophet_forecast, xlabel=graph_x_label, ylabel=graph_y_label)
plt.title(graph_title)
plt.legend()

plt.figure(figsize=(10, 7))
plt.plot(prophet_forecast["ds"], prophet_forecast["trend"], "b-")
plt.xlabel(graph_x_label)
plt.ylabel(graph_y_label)
plt.title(graph_title)
plt.legend()

plt.figure(figsize=(10, 7))
plt.plot(prophet_forecast["ds"], prophet_forecast["yhat"], "b-")
plt.xlabel(graph_x_label)
plt.ylabel(graph_y_label)
plt.title(graph_title)
plt.legend()


# =================================================
#    ========== STEP FIVE : EVALUATION ==========
# =================================================
# Trends and patterns
prophet_model.plot_components(prophet_forecast)
plt.show()

