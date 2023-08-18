import yahooquery
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader


tickersForTesting = ['SPY', 'AAPL']
# tickersForTesting = ['SPY', 'AAPL', 'SNAP', 'TSLA']
class DatasetBuilder:

    def __init__(self, tickers=tickersForTesting):
        self.tickers = tickers

    def buildDataset(self, totalDays=40, trainDays=30):
        dfs = []
        for ticker in self.tickers:
            priceHistory = yahooquery.Ticker(ticker, asnychronous=True)
            df = priceHistory.history(period='max', interval='1d')
            df = df.dropna()
            for col in ['date','high', 'low','adjclose','dividends', 'splits']:
                if col in df.columns:
                    df.drop(col, axis=1, inplace=True)
            dfs.append(df)

            # TODO: if splits, separate into 2 different dfs. no samples should overlap a split.

        # print(len(dfs[0]))

        # normalize data 0-1
        sc_price = MinMaxScaler()
        sc_volume = MinMaxScaler()
        for df in dfs:
            df[['open', 'close']] = sc_price.fit_transform(df[['open','close']])
            df[['volume']] = sc_volume.fit_transform(df[['volume']])
        # https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html
        # use inverse_transform to interpret predictions later


        # combine all tickers into 40 day chunks of priceHistory
        windows = []
        for df in dfs:
            for i in range(df['close'].count() // totalDays): # 30 market days training, 10 market days testing
                windows.append(df.iloc[i*totalDays : (i+1)*totalDays])

        print(len(windows))

        windowsValues = [df.values for df in windows] 
        # float 32 is default ^, can reduce open and close to 16 if not normalizing later
        # print(len(windowsValues))
        # print(len(windowsValues[0]))


        # split 30 into X (training samples) and 10 into Y (validation) for each window
        X = np.array([arr[ : trainDays] for arr in windowsValues]) # vstack concatenates along first axis, turning (N,) into (1,N)
        Y = np.array([arr[trainDays : ] for arr in windowsValues])
        print('X.shape: ',X.shape)
        print('Y.shape: ',Y.shape)

        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

        trainX_tensor = torch.Tensor(X_train)
        trainY_tensor = torch.Tensor(Y_train)
        testX_tensor = torch.Tensor(X_test)
        testY_tensor = torch.Tensor(Y_test)

        train_data = TensorDataset(trainX_tensor, trainY_tensor)
        test_data = TensorDataset(testX_tensor, testY_tensor)

        train_loader = DataLoader(train_data, batch_size=5, shuffle=True) # shuffle since samples are taken sequentially but should be evaluated without patterns in the sequence.
        test_loader = DataLoader(test_data, batch_size=5, shuffle=False) # doesn't change model so don't need to shuffle.   

        return train_loader,test_loader