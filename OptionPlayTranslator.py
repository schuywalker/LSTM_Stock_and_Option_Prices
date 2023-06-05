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

    def find_plays(self, date, pred_date, pred_price=None, strike_strat='ATM',risk=1000,print_play=True,verbose=False):
        
        '''
        date is the date the prediction is made
        pred_date is the date on which the prediction makes a prediction
        '''

        # as of date (present)
        self.chain = options_utils.get_chain(self.dataset, date) # full option chain as of date
        fut_friday = options_utils.select_friday(date, pred_date) # get future friday immediately after prediction date
        self.pred_week = options_utils.slice_week(self.chain, fut_friday) # get contract chain expiring on future friday, as of date

        if self.pred_week.empty:
            # print (f'pred_week empty (no contracts expiring on {fut_friday})') # skip for now. keep going farther out?
            return None

        # as of future friday (truth. in future)
        self.chain_on_pred_date = self.dataset.get_group(pred_date) # full option chain as of future friday (truth in future)
        self.pred_week_on_pred_date = options_utils.slice_week(self.chain_on_pred_date, fut_friday)
        

        # self.pred_week.to_csv('pred_week.csv', index=False, header=True, encoding='utf-8')
        # self.pred_week_on_pred_date.to_csv('pred_week_in_fut.csv', index=False, header=True, encoding='utf-8')
        
        if pred_price is None:
            return None
        
        if (print_play):
            print(f'\n{self.ticker} on {date} predicted to be {pred_price} on {pred_date}')

        return self.make_play(pred_price, strike_strat, risk, print_play, verbose)


    
    def make_play(self, pred_price, strike_strat='ATM',risk=1000, print_play=True,verbose=False):
        assert (risk <= 1000)
        try:
            spot = self.pred_week.iloc[0]['[UNDERLYING_LAST]']
        except Exception as e:
            print(e)
            return None


        bullish = pred_price > spot
        if bullish:
            if strike_strat == 'ATM':
                position = self.pred_week[(self.pred_week['[STRIKE]'] >= spot)].iloc[10]
            elif strike_strat == 'FIND_BEST_STRIKE':
                print('hello world call') 
                # for loop, calc_predicted_PnL, keep saving strike if better, if two in a row are worse (worse is True and this strike is worse) then early stop. 
                    
            cp = 'C'    
        else:
            if strike_strat == 'ATM':
                position = self.pred_week[(self.pred_week['[STRIKE]'] <= spot)].iloc[0]
            elif strike_strat == 'FIND_BEST_STRIKE':
                print('hello world put')
            cp = 'P'
        

        future_spot_truth = self.pred_week_on_pred_date['[UNDERLYING_LAST]'].iloc[0]
        

        true_return = (future_spot_truth - spot) / spot
        position_in_future = self.pred_week_on_pred_date[self.pred_week_on_pred_date['[STRIKE]'] == position['[STRIKE]']]
        
        #shares
        shares_predicted_return = round(((pred_price - spot) / spot)*100,3)
        predicted_baseline_PnL = shares_predicted_return * 1000

        actual_baseline_PnL = ((true_return * 1000) + 1000 ) if bullish else 1000 
        
        premium_paid = position[f'[{cp}_ASK]']
        value_at_expiration = position_in_future[f'[{cp}_BID]'].iloc[0]
        # if type(value_at_expiration) != float:
        #     # print(position, '\n')
        #     return None
        value_at_expiration = float(value_at_expiration)


        # single_contract_PL = value_at_expiration - premium_paid
        qty = risk / premium_paid
        net_option_exposure_value = (value_at_expiration * qty)
        actual_option_PnL = net_option_exposure_value + (1000 - risk)
        
        #option
        strike = position['[STRIKE]']
        predicted_option_return = round(((pred_price - strike) / strike),2)
        predicted_option_PnL = (((pred_price - strike) * 100) * qty) + (1000 - risk)
        
        
        baseline_percent = round((((actual_baseline_PnL / 1000)-1) * 100), 3)
        option_percent = round((((actual_option_PnL / 1000)-1) * 100), 3)

        option_outperformance = actual_option_PnL - actual_baseline_PnL

        if print_play:
            if verbose:
                print('Price on date prediction was made: ',spot,'. Actual share price on predicted date: ',future_spot_truth)
                print(f'Price movement: Actual:{round(true_return*100,2)}% Predicted:{shares_predicted_return}%')
                print(f'Contact value went from { premium_paid } to { value_at_expiration }') 
                print(f'Premium paid: {premium_paid}. Qty: {qty}. Net option exposure value: {net_option_exposure_value}. Actual option PnL: {actual_option_PnL}')
                
            print(f'Predicted baseline return: {shares_predicted_return}% P/L:${int(predicted_baseline_PnL)}. Predicted Option return: {predicted_option_return}% P/L: ${int(predicted_option_PnL)}.' ) 
            print(f'Baseline (shares): {baseline_percent}% P/L:${int(actual_baseline_PnL)}.  Option PnL: {option_percent}% P/L: ${int(actual_option_PnL)}. Result for options:${round(option_outperformance,2)}\n' ) 
        
        return (actual_baseline_PnL, actual_option_PnL, option_outperformance, predicted_baseline_PnL,predicted_option_PnL)