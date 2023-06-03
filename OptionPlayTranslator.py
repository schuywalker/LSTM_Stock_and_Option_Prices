import pandas as pd
import numpy as np
from utils.options_utils import *

class OPT:

    def __init__(self, ticker, dataset:pd.core.groupby.generic.DataFrameGroupBy, pred_date:str = None, predictions=None):
        self.ticker = ticker
        self.predictions = predictions
        self.dataset = dataset # comes in as groupby right now
        pred_date = pred_date 
        self.fut_friday:str  = None
        self.pred_week:pd.DataFrame = None # contracts expiring immediately after prediction date
        self.chain_on_fut_friday:pd.DataFrame = None
        self.pred_week_on_fut_friday:pd.DataFrame = None

    def find_plays(self, date, pred_date, pred_price):
        # add space to dates or strip dates beforehand
        
        '''
        date is the date the prediction is made
        pred_date is the date on which the prediction makes a prediction
        '''

        # as of date (present)
        self.chain = options_utils.get_chain(self.dataset, date) # full option chain as of date
        self.fut_friday = options_utils.select_friday(date, pred_date) # get future friday immediately after prediction date
        self.pred_week = options_utils.slice_week(self.chain, self.fut_friday) # get contract chain expiring on future friday, as of date
        self.pred_week.to_csv('pred_week.csv', index=False, header=True, encoding='utf-8')

        # as of future friday (truth, future is present)
        self.chain_on_fut_friday = self.dataset.get_group(self.fut_friday) # full option chain as of future friday (truth in future)
        self.pred_week_on_fut_friday = options_utils.slice_week(self.chain_on_fut_friday, self.fut_friday)
        self.pred_week_on_fut_friday.to_csv('pred_week_in_fut.csv', index=False, header=True, encoding='utf-8')
        
        return self.pred_week