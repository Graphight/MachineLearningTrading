
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

from main.python.MachineLearning.ProphetApproach.FunctionsData import collect_FX_and_write_to_csv, \
    collect_Crypto_and_write_to_csv
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
crypto_currency = "BTC"
physical_currency = "NZD"
file_name = "MarketData-{}-{}-crypto.csv".format(crypto_currency, physical_currency)
# collect_Crypto_and_write_to_csv(crypto_currency, physical_currency, file_name)
df = pd.read_csv(file_name)


# =================================================
#   ========== STEP TWO : PROCESS DATA ==========
# =================================================
cols_to_drop = ["Open_a", "Open_b", "High_a", "High_b", "Low_a", "Low_b", "Close_b", "Volume"]
df.drop(cols_to_drop, axis=1, inplace=True)
df = df.sort_values("Timestamp")
df = df.set_index("Timestamp")
df.index = pd.to_datetime(df.index)

freq = 7
sample_data = df["Close_a"].resample(str(freq) + "D").mean()
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
prophet_df = pd.DataFrame({"ds": df.index, "y": df["Close_a"].values})
prophet_model = Prophet(interval_width=0.95)
prophet_model.fit(prophet_df)


# =================================================
#   ========== STEP FOUR : PREDICTIONS ==========
# =================================================
# ARIMA stuff
# start_pred = pd.to_datetime(df.index.values[int(df.size * 0.8)])  # For real data
start_pred = pd.to_datetime(sample_data.index.values[int(sample_data.size * 0.4)])  # For seasonal guess
# end_pred = pd.to_datetime(df.index.values[-1]) + pd.DateOffset(days=14)
projection = (freq * 3)
end_pred = pd.to_datetime(sample_data.index.values[-1]) + pd.DateOffset(days=projection)
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
graph_title = "{} -> {} Timeseries ".format(crypto_currency, physical_currency)
graph_x_label = "Timestamp"
graph_y_label = "Closing Price"

prophet_forecast = prophet_model.make_future_dataframe(periods=projection)
prophet_forecast = prophet_model.predict(prophet_forecast)

prophet_model.plot(prophet_forecast, xlabel=graph_x_label, ylabel=graph_y_label)
plt.title(graph_title + "< Prophet Forecast >")
plt.legend()


# =================================================
#    ========== STEP FIVE : EVALUATION ==========
# =================================================
# ARIMA MSE
arima_forecast = arima_prediction.predicted_mean[:(end_pred - pd.DateOffset(days=projection))]
arima_truth = sample_data[start_pred:]
mse = ((arima_forecast - arima_truth) ** 2).mean()
print("The Mean Square Error of our forecast is {}".format(round(mse, 2)))

# Trends and patterns -Prophet-
prophet_model.plot_components(prophet_forecast)
plt.show()

