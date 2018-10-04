
from requests import get
from decimal import Decimal

import csv

# Global
API_KEY = "GRYVIVFOM0RKLZXP"

def collect_and_write_to_csv(currency_from, currency_to, interval, file_name):
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


def extract_data(file_name):
    data = []
    with open(file_name, newline='') as csv_file:
        lines = csv.reader(csv_file, delimiter=',', quotechar='\"')
        first = True
        for line in lines:
            if first:
                first = False
            else:
                values = [line[0],
                          float(line[1]),
                          float(line[2]),
                          float(line[3]),
                          float(line[4]),
                          float(line[5]),
                          int(line[6]),
                          int(line[7]),
                          int(line[8])]
                data.insert(0, values)
    return data