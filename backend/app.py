from flask import Flask, jsonify
from flask_cors import CORS
import requests
import numpy as np
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

API_KEY = '1Z3EV31MAYB1S61O'

def calculate_forecast(prices):
    # Generate a simple forecast using random walk
    forecast = []
    upper_conf = []
    lower_conf = []

    for price in prices:
        forecasted_price = price + np.random.normal(0, 2)
        forecast.append(forecasted_price)
        upper_conf.append(forecasted_price + 5)
        lower_conf.append(forecasted_price - 5)

    return forecast, upper_conf, lower_conf

@app.route('/api/data', methods=['GET'])
def get_data():
    symbol = "WOOD"
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if 'Time Series (Daily)' not in data:
        return jsonify({"error": "Failed to fetch data"}), 500

    time_series = data['Time Series (Daily)']
    prices = [
        {"timestamp": date, "price": float(info['4. close'])}
        for date, info in time_series.items()
    ]

    # Sort prices by date
    prices.sort(key=lambda x: x['timestamp'])

    # Filter to the last 3 years
    three_years_ago = (datetime.now() - timedelta(days=3*365)).strftime('%Y-%m-%d')
    filtered_prices = [price for price in prices if price["timestamp"] >= three_years_ago]

    # Extract price list for forecasting
    price_list = [price['price'] for price in filtered_prices]

    # Calculate forecast and confidence intervals
    forecast, upper_conf, lower_conf = calculate_forecast(price_list)

    # Combine results
    result = []
    for i, price in enumerate(filtered_prices):
        result.append({
            "timestamp": price["timestamp"],
            "actual_price": price["price"],
            "forecast_price": forecast[i],
            "upper_conf": upper_conf[i],
            "lower_conf": lower_conf[i]
        })

    return jsonify({"prices": result})

if __name__ == '__main__':
    app.run(debug=True)