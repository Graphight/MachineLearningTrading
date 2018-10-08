
from requests import get
from decimal import Decimal

import csv

# Global
API_KEY = "GRYVIVFOM0RKLZXP"


def collect_FX_and_write_to_csv(currency_from, currency_to, interval, file_name):
    # Setup
    global API_KEY
    url = "https://www.alphavantage.co/query?function=FX_INTRADAY&"
    # url = "https://www.alphavantage.co/query?function=FX_DAILY&"
    url += "from_symbol={}&".format(currency_from)
    url += "to_symbol={}&".format(currency_to)
    url += "interval={}&".format(interval)
    url += "outputsize=full&apikey={}".format(API_KEY)
    decimal_places = Decimal(10) ** -8

    # Collect
    response = get(url).json()

    # Write to file
    with open(file_name, "w", newline="") as csvfile:
        field_names = ["Timestamp", "Open", "High", "Low", "Close", "Difference",
                       "Stagnated", "Increased", "Decreased"]
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        timeseries = response["Time Series FX ({})".format(interval)]

        total_inc = 0
        total_dec = 0
        total_stg = 0

        for tick in timeseries.items():
            timestamp = tick[0]
            values = tick[1]
            open_value = Decimal(values["1. open"]).quantize(decimal_places)
            high_value = Decimal(values["2. high"]).quantize(decimal_places)
            low_value = Decimal(values["3. low"]).quantize(decimal_places)
            close_value = Decimal(values["4. close"]).quantize(decimal_places)

            difference = (close_value - open_value).quantize(decimal_places)
            if close_value == open_value:
                difference = 0

            increased = 0
            if close_value > open_value:
                increased = 1
                total_inc += 1

            decreased = 0
            if close_value < open_value:
                decreased = 1
                total_dec += 1

            stagnated = 0
            if (increased + decreased) == 0:
                stagnated = 1
                total_stg += 1

            writer.writerow({"Timestamp": timestamp,
                             "Open": open_value,
                             "High": high_value,
                             "Low": low_value,
                             "Close": close_value,
                             "Difference": difference,
                             "Stagnated": stagnated,
                             "Increased": increased,
                             "Decreased": decreased})

    print("\nTotal {} = {}".format("incr", total_inc))
    print("Total {} = {}".format("decr", total_dec))
    print("Total {} = {}\n".format("stag", total_stg))


def collect_Crypto_and_write_to_csv(crypto_currency, physical_currency, file_name):
    # Setup
    global API_KEY
    url = "https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&"
    url += "symbol={}&".format(crypto_currency)
    url += "market={}&".format(physical_currency)
    url += "outputsize=full&apikey={}".format(API_KEY)
    decimal_places = Decimal(10) ** -8

    # Collect
    response = get(url).json()

    # Write to file
    with open(file_name, "w", newline="") as csvfile:
        field_names = ["Timestamp", "Open_a", "Open_b", "High_a", "High_b",
                       "Low_a", "Low_b", "Close_a", "Close_b", "Volume"]
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        timeseries = response["Time Series (Digital Currency Daily)"]

        for tick in timeseries.items():
            values = tick[1]
            open_a = Decimal(values["1a. open ({})".format(physical_currency)]).quantize(decimal_places)
            open_b = Decimal(values["1b. open ({})".format("USD")]).quantize(decimal_places)
            high_a = Decimal(values["2a. high ({})".format(physical_currency)]).quantize(decimal_places)
            high_b = Decimal(values["2b. high ({})".format("USD")]).quantize(decimal_places)
            low_a = Decimal(values["3a. low ({})".format(physical_currency)]).quantize(decimal_places)
            low_b = Decimal(values["3b. low ({})".format("USD")]).quantize(decimal_places)
            close_a = Decimal(values["4a. close ({})".format(physical_currency)]).quantize(decimal_places)
            close_b = Decimal(values["4b. close ({})".format("USD")]).quantize(decimal_places)
            volume = Decimal(values["5. volume"]).quantize(decimal_places)
            writer.writerow({"Timestamp": (tick[0]),
                             "Open_a": open_a,
                             "Open_b": open_b,
                             "High_a": high_a,
                             "High_b": high_b,
                             "Low_a": low_a,
                             "Low_b": low_b,
                             "Close_a": close_a,
                             "Close_b": close_b,
                             "Volume": volume})
