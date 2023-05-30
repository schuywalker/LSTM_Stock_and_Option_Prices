import pandas as pd
import datetime

class OptionPlayTranslator():

    def __init__(self, ticker, chains:pd.core.groupby.generic.DataFrameGroupBy, predictions=None) -> None:
        self.ticker = ticker
        self.chains = chains
        self.predictions = predictions
    
    def setPredictions(self, predictions) -> None:
        self.predictions = predictions

    def findPlays(self, date, predictionDate):
        chain = self.chains.get_group(date)
        print(type(chain), ' is chain type\n')
        print('chain.head() ',chain.head())
        expirationDates = chain['[EXPIRE_DATE]'].unique()
        

