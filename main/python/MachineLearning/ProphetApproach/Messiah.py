
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


# =================================================
#   ========== STEP TWO : PROCESS DATA ==========
# =================================================
cols_to_drop = ["Open", "High", "Low", "Difference", "Stagnated", "Increased", "Decreased"]
df.drop(cols_to_drop, axis=1, inplace=True)
df = df.sort_values("Timestamp")
df = df.set_index("Timestamp")
df.index = pd.to_datetime(df.index)

# Freq seems to be in ticks (minutes in this case)
freq = 120
sample_data = df["Close"].resample("1T").mean()
decomposition = sm.tsa.seasonal_decompose(sample_data, model="additive", freq=freq)
decomposition.plot()


# =================================================
# ========== STEP THREE : MODEL CREATION ==========
# =================================================
# ARIMA stuff
arima_pdq = determine_best_p_d_q_variables(sample_data)
arima_model = arima_pdq.fit(disp=False)
# print(arima_model.summary().tables[1])
arima_model.plot_diagnostics(figsize=(16, 8))

# Use Facebook"s -Prophet-
prophet_df = pd.DataFrame({"ds": df.index, "y": df["Close"].values})
prophet_model = Prophet(interval_width=0.95)
prophet_model.fit(prophet_df)


# =================================================
#   ========== STEP FOUR : PREDICTIONS ==========
# =================================================
# ARIMA stuff
start_pred = pd.to_datetime(df.index.values[int(df.size * 0.8)])
end_pred = pd.to_datetime(df.index.values[-1]) + pd.DateOffset(minutes=10)
arima_prediction = arima_model.get_prediction(start=start_pred, end=end_pred, dynamic=False)
arima_prediction_ci = arima_prediction.conf_int()

ax = df.plot(label="Observed")
arima_prediction.predicted_mean.plot(ax=ax, label="One-step ahead Forecast", alpha=0.8)

ax.fill_between(arima_prediction_ci.index,
                arima_prediction_ci.iloc[:, 0],
                arima_prediction_ci.iloc[:, 1], color='k', alpha=0.2)
ax.set_xlabel("Timestamp")
ax.set_ylabel("Closing Price")
plt.legend()

# Facebook's -Prophet-
graph_title = "{} -> {} Timeseries ".format(currency_from, currency_to)
graph_x_label = "Timestamp"
graph_y_label = "Closing Price"

prophet_forecast = prophet_model.make_future_dataframe(periods=10, freq="1min")
prophet_forecast = prophet_model.predict(prophet_forecast)

prophet_model.plot(prophet_forecast, xlabel=graph_x_label, ylabel=graph_y_label)
plt.title(graph_title + "< Prophet Forecast >")
plt.legend()


# =================================================
#    ========== STEP FIVE : EVALUATION ==========
# =================================================
# ARIMA MSE
arima_forecast = arima_prediction.predicted_mean[:(end_pred - pd.DateOffset(minutes=10))]
arima_truth = sample_data[start_pred:]
mse = ((arima_forecast - arima_truth) ** 2).mean()
print("The Mean Square Error of our forecast is {}".format(round(mse, 2)))

# Trends and patterns -Prophet-
prophet_model.plot_components(prophet_forecast)
plt.show()

