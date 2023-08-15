import yahooquery
import pandas as pd
import numpy as np


tickers = ['SPY', 'AAPL', 'SNAP', 'TSLA']
dfs = []
for ticker in tickers:
    priceHistory = yahooquery.Ticker(ticker, asnychronous=True)
    df = priceHistory.history(period='max', interval='1d')
    df = df.dropna()
    for col in ['date','high', 'low','adjclose','dividends', 'splits']:
        if col in df.columns:
            df.drop(col, axis=1, inplace=True)
    dfs.append(df)

    # TODO: if splits, separate into 2 different dfs. no samples should overlap a split.


samples = []
for df in dfs:
    for i in range(df['close'].count()//40): # 30 market days training, 10 market days testing
        samples.append(df.iloc[i*30:(i+1)*30])

print(len(samples))


samplesTemp = [np.around(df.values, 3).astype(np.float32) for df in samples] # convert to ndarrays, reduce float64 for computation costs.
# float16 works for every stock except BRKA, but volume needs float32. test later to see if we can get away with mixed floats in matrix ops



print(samplesTemp[0][0])


X = np.vstack([arr[:30] for arr in samplesTemp]) # vstack concatenates along first axis, turning (N,) into (1,N)
Y = np.vstack([arr[30:] for arr in samplesTemp])

print(X[0])