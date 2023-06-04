import pandas as pd
import numpy as np
from utils.options_utils import *

class OPT:

    def __init__(self, ticker, dataset:pd.core.groupby.generic.DataFrameGroupBy, pred_date:str = None, predictions=None):
        self.ticker = ticker
        self.predictions = predictions
        self.dataset = dataset # comes in as groupby right now
        
        
        self.chain:pd.DataFrame = None
        self.pred_week:pd.DataFrame = None # contracts expiring immediately after prediction date
        
        self.chain_on_pred_date:pd.DataFrame = None
        self.pred_week_on_pred_date:pd.DataFrame = None

    def find_plays(self, date, pred_date, pred_price=None):
        # add space to dates or strip dates beforehand
        print(f'{self.ticker} on {date} predicted to be {pred_price} on {pred_date} \n')
        '''
        date is the date the prediction is made
        pred_date is the date on which the prediction makes a prediction
        '''

        # as of date (present)
        self.chain = options_utils.get_chain(self.dataset, date) # full option chain as of date
        fut_friday = options_utils.select_friday(date, pred_date) # get future friday immediately after prediction date
        self.pred_week = options_utils.slice_week(self.chain, fut_friday) # get contract chain expiring on future friday, as of date

        # as of future friday (truth. in future)
        self.chain_on_pred_date = self.dataset.get_group(pred_date) # full option chain as of future friday (truth in future)
        self.pred_week_on_pred_date = options_utils.slice_week(self.chain_on_pred_date, fut_friday)
        

        # self.pred_week.to_csv('pred_week.csv', index=False, header=True, encoding='utf-8')
        # self.pred_week_on_pred_date.to_csv('pred_week_in_fut.csv', index=False, header=True, encoding='utf-8')
        
        if pred_price is not None:
            self.make_play(pred_price)

        return self.pred_week
    
    def make_play(self, pred_price, strike_strat='ATM',risk=1000):
        spot = self.pred_week.iloc[0]['[UNDERLYING_LAST]']

        bullish = pred_price > spot
        if bullish:
            position = self.pred_week[(self.pred_week['[STRIKE]'] >= spot)].iloc[0]
            print('\nposition:',position.shape,'\n', position)
            cp = 'C'    
        else:
            position = self.pred_week[(self.pred_week['[STRIKE]'] <= spot)].iloc[0]
            print('\nposition:',position.shape,'\n', position)
            cp = 'P'
        
        predicted_return = (pred_price - spot) / spot
        print('predicted_return: ',predicted_return)

        future_spot_truth = self.pred_week_on_pred_date['[UNDERLYING_LAST]'].iloc[0]
        print('Price on date prediction was made: ',spot,'. Actual share price on predicted date: ',future_spot_truth)
        position_in_future = self.pred_week_on_pred_date[self.pred_week_on_pred_date['[STRIKE]'] == position['[STRIKE]']]
        
        true_return = (future_spot_truth - spot) / spot
        print(f'price return during timeframe: {(int(true_return*100))}%')
        baseline_PnL = (true_return * 1000)
        
        premium_paid = position[f'[{cp}_ASK]']
        value_at_expiration = position_in_future[f'[{cp}_BID]'].iloc[0]

        Option_PnL = (value_at_expiration - premium_paid) / (premium_paid / risk) 
        print(f'baseline_PnL (shares): ${int(baseline_PnL)}.  Option PnL: ${int(Option_PnL)}. Contact value went from { premium_paid } to { value_at_expiration}' ) 
        
        return (baseline_PnL, Option_PnL)