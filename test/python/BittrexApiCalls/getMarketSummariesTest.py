
# Import Libraries
import requests
import json
from decimal import *

# Setup
market_name = 'BTC-ETH'
period = 'day'
url = 'https://bittrex.com/api/v2.0/pub/market/getTicks?marketName={}&tickInterval={}'.format(market_name, period)

# Collect ticks
response = requests.get(url)
print(response.status_code)

# Display the tick responses
DECIMAL_PLACES = Decimal(10) ** -8
for tick in response.json()['result']:
    result = ""
    result += "timestamp: {} \t".format(tick['T'])
    result += "timestamp: {} \t".format(Decimal(tick['O']).quantize(DECIMAL_PLACES))
    result += "timestamp: {} \t".format(Decimal(tick['H']).quantize(DECIMAL_PLACES))
    result += "timestamp: {} \t".format(Decimal(tick['L']).quantize(DECIMAL_PLACES))
    result += "timestamp: {} \t".format(Decimal(tick['C']).quantize(DECIMAL_PLACES))
    print(result)

