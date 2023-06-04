import pandas as pd
import numpy as np
from utils.options_utils import *

class OPT:

    def __init__(self, ticker, dataset:pd.core.groupby.generic.DataFrameGroupBy, pred_date:str = None, predictions=None):
        self.ticker = ticker
        self.predictions = predictions
        self.dataset = dataset # comes in as groupby right now
        
        pred_date:str = pred_date 
        self.fut_friday:str  = None
        
        self.chain:pd.DataFrame = None
        self.pred_week:pd.DataFrame = None # contracts expiring immediately after prediction date
        
        self.chain_on_fut_friday:pd.DataFrame = None
        self.pred_week_on_fut_friday:pd.DataFrame = None

    def find_plays(self, date, pred_date, pred_price=None):
        # add space to dates or strip dates beforehand
        
        '''
        date is the date the prediction is made
        pred_date is the date on which the prediction makes a prediction
        '''

        # as of date (present)
        self.chain = options_utils.get_chain(self.dataset, date) # full option chain as of date
        self.fut_friday = options_utils.select_friday(date, pred_date) # get future friday immediately after prediction date
        self.pred_week = options_utils.slice_week(self.chain, self.fut_friday) # get contract chain expiring on future friday, as of date

        # as of future friday (truth, future is present)
        self.chain_on_fut_friday = self.dataset.get_group(self.fut_friday) # full option chain as of future friday (truth in future)
        self.pred_week_on_fut_friday = options_utils.slice_week(self.chain_on_fut_friday, self.fut_friday)
        

        # self.pred_week.to_csv('pred_week.csv', index=False, header=True, encoding='utf-8')
        # self.pred_week_on_fut_friday.to_csv('pred_week_in_fut.csv', index=False, header=True, encoding='utf-8')
        
        if pred_price is not None:
            self.make_play(pred_price)

        return self.pred_week
    
    def make_play(self, pred_price, strike_strat='ATM',risk='min'):
        # risk min $100, med $500, max $1000. shares baseline always $1000.
        spot = self.pred_week.iloc[0]['[UNDERLYING_LAST]']
        print('spot ',spot)
        bullish = pred_price > spot
        if bullish:
            position = self.pred_week[(self.pred_week['[STRIKE]'] >= spot)].iloc[0]
            cp = 'C'    
        else:
            position = self.pred_week[(self.pred_week['[STRIKE]'] <= spot)].iloc[0]
            cp = 'P'
        
        predicted_return = pred_price / spot
        print('predicted_return: ',predicted_return)

        # future_spot_truth = self.pred_week_on_fut_friday[0]['[UNDERLYING_LAST]'].iloc[0]
        future_spot_truth = self.pred_week_on_fut_friday['[UNDERLYING_LAST]'].iloc[0]
        print('future spot: ',future_spot_truth)
        position_in_future = self.pred_week_on_fut_friday[self.pred_week_on_fut_friday['[STRIKE]'] == position['[STRIKE]']]
        print('position_in_future: ',position_in_future)
        
        true_return = (future_spot_truth / spot)
        print('true_return: ',true_return, 'x')
        baseline_PnL = true_return * 1000
        print('baseline_PnL: ',baseline_PnL)
        
        premium_paid = position[f'[{cp}_ASK]']
        print('premium_paid: ',premium_paid)
        value_at_expiration = position_in_future[f'[{cp}_BID]']
        print('value_at_expiration: ',value_at_expiration)

        Option_PnL = (value_at_expiration / premium_paid) * 1000
        print('value at expiration: ',value_at_expiration, ' premium paid: ',premium_paid, 'end PnL: ',Option_PnL) 
        