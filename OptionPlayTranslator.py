import pandas as pd
import datetime
from datetime import date, timedelta
import numpy as np

class OptionPlayTranslator():

    def __init__(self, ticker, chains:pd.core.groupby.generic.DataFrameGroupBy, predictions=None) -> None:
        self.ticker = ticker
        self.chains = chains # change to not hold in memory
        self.predictions = predictions
    
    def setPredictions(self, predictions) -> None:
        self.predictions = predictions

    def findPlays(self, date, predictionDate):
        startingChain = self.chains.get_group(date)
        print('\n COLUMNS!! \n',startingChain.columns)
        nearest_expiry = self.getNearestExpirationWeek(date, predictionDate)
        print('nearest_expiry ', nearest_expiry)
        endingChain = self.chains.get_group(nearest_expiry)
        
        pred_chain:pd.DataFrame = endingChain.loc[endingChain['[EXPIRE_DATE]'] == nearest_expiry]
        print('\nPRED_CHAIN\n',pred_chain)
        
        # df_expiration_dates = chain.groupby('[EXPIRE_DATE]')
        # exp_week_chain = df_expiration_dates.get_group(nearest_expiry)
        # print('exp_week_chain ', exp_week_chain)
        
        # nearest_expiry_chain = df_expiration_dates.get_group(' ['+str(nearest_expiry)+']')
        




    def getNearestExpirationWeek(self, curDate:str, predictionDate:str) -> str:
        curDate = np.array(curDate.strip().split('-'), dtype=int)
        futDate = np.array(predictionDate.strip().split('-'), dtype=int)
        cur = date(*curDate)
        fut = date(*futDate)

        #### monday = 0, sunday = 6, friday = 4 ####
        
        #TODO: check fut is < last date in datasets (save final dates in memory)
       
        while  fut.weekday() != 4:
            fut += timedelta(1)
        
        assert(fut > cur)
        ret = ' '+fut.strftime('%Y-%m-%d')
        print('ret ', ret)
        return ret
