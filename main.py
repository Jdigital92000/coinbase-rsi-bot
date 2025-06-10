import os
import time
import cbpro
import pandas as pd
import numpy as np

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'BTC-USD'
TRADE_AMOUNT = '0.001'

api_key = os.getenv("COINBASE_API_KEY")
api_secret = os.getenv("COINBASE_API_SECRET")
api_passphrase = os.getenv("COINBASE_API_PASSPHRASE")

auth_client = cbpro.AuthenticatedClient(api_key, api_secret, api_passphrase)

def get_rsi(data, period=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def fetch_price_data():
    public_client = cbpro.PublicClient()
    historic_rates = public_client.get_product_historic_rates(TRADE_SYMBOL, granularity=3600)
    df = pd.DataFrame(historic_rates, columns=['time', 'low', 'high', 'open', 'close', 'volume'])
    df['close'] = df['close'].astype(float)
    df.sort_values('time', inplace=True)
    return df

def trade():
    df = fetch_price_data()
    df['rsi'] = get_rsi(df['close'])
    current_rsi = df['rsi'].iloc[-1]
    print(f"Current RSI: {current_rsi}")

    if current_rsi < RSI_OVERSOLD:
        # Buy signal
        print("RSI low - placing buy order")
        auth_client.place_market_order(product_id=TRADE_SYMBOL, side='buy', funds='20')
    elif current_rsi > RSI_OVERBOUGHT:
        # Sell signal
        print("RSI high - placing sell order")
        auth_client.place_market_order(product_id=TRADE_SYMBOL, side='sell', size=TRADE_AMOUNT)

if __name__ == "__main__":
    while True:
        try:
            trade()
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(3600)  # Run every hour