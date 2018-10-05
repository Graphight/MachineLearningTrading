# Import stuff
import warnings
import itertools
import numpy as np
import matplotlib.pyplot as plt
from pylab import rcParams

import pandas as pd
import statsmodels.api as sm
import matplotlib
from fbprophet import Prophet

# Configure the matplotlib stuff
warnings.filterwarnings("ignore")
plt.style.use('fivethirtyeight')
matplotlib.rcParams['axes.labelsize'] = 14
matplotlib.rcParams['xtick.labelsize'] = 12
matplotlib.rcParams['ytick.labelsize'] = 12
matplotlib.rcParams['text.color'] = 'k'
rcParams['figure.figsize'] = 18, 8

# Read in the data
df = pd.read_excel("Superstore.xls")

# ==============================================================
# Data prep
# ==============================================================

fdf = pd.read_excel("Superstore.xls")
furniture = df.loc[df['Category'] == 'Furniture']

cols = ['Row ID', 'Order ID', 'Ship Date', 'Ship Mode', 'Customer ID', 'Customer Name', 'Segment', 'Country', 'City', 'State', 'Postal Code', 'Region', 'Product ID', 'Category', 'Sub-Category', 'Product Name', 'Quantity', 'Discount', 'Profit']
furniture.drop(cols, axis=1, inplace=True)
furniture = furniture.sort_values('Order Date')

furniture = furniture.groupby('Order Date')['Sales'].sum().reset_index()

furniture = furniture.set_index('Order Date')

# Take a peek at the graph
y = furniture['Sales'].resample('MS').mean()
y = y.fillna(y.bfill())

# Take a gander at Dicky-Fuller stuff
decomposition = sm.tsa.seasonal_decompose(y, model='additive')
decomposition.plot()


# ==============================================================
# Actually start doing ML stuff
# ==============================================================

p = d = q = range(0, 2)
pdq = list(itertools.product(p, d, q))
seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]
options = dict()
for param in pdq:
    for param_seasonal in seasonal_pdq:
        try:
            model = sm.tsa.statespace.SARIMAX(y,
                                              order=param,
                                              seasonal_order=param_seasonal,
                                              enforce_stationarity=False,
                                              enforce_invertibility=False)
            results = model.fit(disp=False)
            options[results.aic] = [param, param_seasonal]
            # print('ARIMA{}x{}12 - AIC:{}'.format(param, param_seasonal, results.aic))
        except:
            continue

# Determine the best formation to use
best = min(options.keys())
print("\nThe lowest scoring item returned < {} > which had the params < {} >\n".format(best, options[best]))


# Use this configuration
model = sm.tsa.statespace.SARIMAX(y,
                                  order=(1, 1, 1),
                                  seasonal_order=(1, 1, 0, 12),
                                  enforce_stationarity=False,
                                  enforce_invertibility=False)
results = model.fit(disp=False)

print(results.summary().tables[1])

results.plot_diagnostics(figsize=(16, 8))

pred = results.get_prediction(start=pd.to_datetime("2017-01-01"), dynamic=False)
pred_ci = pred.conf_int()

ax = furniture.plot(label='observed')
pred.predicted_mean.plot(ax=ax, label='One-step ahead Forecast', alpha=.7)

ax.fill_between(pred_ci.index,
                pred_ci.iloc[:, 0],
                pred_ci.iloc[:, 1], color='k', alpha=.2)

ax.set_xlabel('Date')
ax.set_ylabel('Furniture Sales')
plt.legend()

plt.show()

# MSE
# y_forecasted = pred.predicted_mean
# y_truth = y['2017-01-01':]
# mse = ((y_forecasted - y_truth) ** 2).mean()
# print('The Mean Squared Error of our forecasts is {}'.format(round(mse, 2)))
# print('The Root Mean Squared Error of our forecasts is {}'.format(round(np.sqrt(mse), 2)))
#
# # Producing and Visualizing forecasts
# pred_uc = results.get_forecast(steps=100)
# pred_ci = pred_uc.conf_int()
# ax = y.plot(label='observed', figsize=(14, 7))
#
# # figure(5)
# pred_uc.predicted_mean.plot(ax=ax, label='Forecast')
# ax.fill_between(pred_ci.index,
#                 pred_ci.iloc[:, 0],
#                 pred_ci.iloc[:, 1], color='k', alpha=.25)
# ax.set_xlabel('Date')
# ax.set_ylabel('Furniture Sales')
# plt.legend()

# ==============================================================
# Data Exploration stuff
# ==============================================================

# furniture = df.loc[df['Category'] == 'Furniture']
# office = df.loc[df['Category'] == 'Office Supplies']
#
# cols = ['Row ID', 'Order ID', 'Ship Date', 'Ship Mode', 'Customer ID', 'Customer Name', 'Segment', 'Country', 'City', 'State', 'Postal Code', 'Region', 'Product ID', 'Category', 'Sub-Category', 'Product Name', 'Quantity', 'Discount', 'Profit']
# furniture.drop(cols, axis=1, inplace=True)
# office.drop(cols, axis=1, inplace=True)
#
# furniture = furniture.sort_values('Order Date')
# office = office.sort_values('Order Date')
#
# furniture = furniture.groupby('Order Date')['Sales'].sum().reset_index()
# office = office.groupby('Order Date')['Sales'].sum().reset_index()
#
# furniture = furniture.set_index('Order Date')
# office = office.set_index('Order Date')
#
# y_furniture = furniture['Sales'].resample('MS').mean()
# y_office = office['Sales'].resample('MS').mean()
#
# furniture = pd.DataFrame({'Order Date':y_furniture.index, 'Sales':y_furniture.values})
# office = pd.DataFrame({'Order Date': y_office.index, 'Sales': y_office.values})
#
# store = furniture.merge(office, how='inner', on='Order Date')
# store.rename(columns={'Sales_x': 'furniture_sales', 'Sales_y': 'office_sales'}, inplace=True)
#
# plt.figure(6, figsize=(20, 8))
# plt.plot(store['Order Date'], store['furniture_sales'], 'b-', label = 'furniture')
# plt.plot(store['Order Date'], store['office_sales'], 'r-', label = 'office supplies')
# plt.xlabel('Date')
# plt.ylabel('Sales')
# plt.title('Sales of Furniture and Office Supplies')
# plt.legend()
#
# first_date = store.ix[np.min(list(np.where(store['office_sales'] > store['furniture_sales'])[0])), 'Order Date']
#
# print("Office supplies first time produced higher sales than furniture is {}.".format(first_date.date()))
#
#
# # Use Facebook's -Prophet-
# furniture = furniture.rename(columns={'Order Date': 'ds'})
# furniture = furniture.rename(columns={'Sales': 'y'})
# furniture_model = Prophet(interval_width=0.95)
# furniture_model.fit(furniture)
#
# office = office.rename(columns={'Order Date': 'ds', 'Sales': 'y'})
# office_model = Prophet(interval_width=0.95)
# office_model.fit(office)
#
# furniture_forecast = furniture_model.make_future_dataframe(periods=36, freq='MS')
# furniture_forecast = furniture_model.predict(furniture_forecast)
#
# office_forecast = office_model.make_future_dataframe(periods=36, freq='MS')
# office_forecast = office_model.predict(office_forecast)
#
# plt.figure(7, figsize=(18, 6))
# furniture_model.plot(furniture_forecast, xlabel = 'Date', ylabel = 'Sales')
# plt.title('Furniture Sales');
#
# plt.figure(8, figsize=(18, 6))
# office_model.plot(office_forecast, xlabel = 'Date', ylabel = 'Sales')
# plt.title('Office Supplies Sales');
#
# # Compare forecasts
# furniture_names = ['furniture_%s' % column for column in furniture_forecast.columns]
# office_names = ['office_%s' % column for column in office_forecast.columns]
#
# merge_furniture_forecast = furniture_forecast.copy()
# merge_office_forecast = office_forecast.copy()
#
# merge_furniture_forecast.columns = furniture_names
# merge_office_forecast.columns = office_names
#
# forecast = pd.merge(merge_furniture_forecast, merge_office_forecast, how = 'inner', left_on = 'furniture_ds', right_on = 'office_ds')
#
# forecast = forecast.rename(columns={'furniture_ds': 'Date'}).drop('office_ds', axis=1)
#
#
# # Visualise trend
#
# plt.figure(9, figsize=(10, 7))
# plt.plot(forecast['Date'], forecast['furniture_trend'], 'b-')
# plt.plot(forecast['Date'], forecast['office_trend'], 'r-')
# plt.legend(); plt.xlabel('Date'); plt.ylabel('Sales')
# plt.title('Furniture vs. Office Supplies Sales Trend');
#
# plt.figure(10, figsize=(10, 7))
# plt.plot(forecast['Date'], forecast['furniture_yhat'], 'b-')
# plt.plot(forecast['Date'], forecast['office_yhat'], 'r-')
# plt.legend(); plt.xlabel('Date'); plt.ylabel('Sales')
# plt.title('Furniture vs. Office Supplies Estimate');
#
#
# # Trends and patterns
# furniture_model.plot_components(furniture_forecast);
# office_model.plot_components(office_forecast);

plt.show()