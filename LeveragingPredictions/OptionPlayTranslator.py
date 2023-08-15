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
        # save to self to optimize performance later

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
        
        self.pred_week_on_pred_date

        # self.pred_week.to_csv('pred_week.csv', index=False, header=True, encoding='utf-8')
        # self.pred_week_on_pred_date.to_csv('pred_week_in_fut.csv', index=False, header=True, encoding='utf-8')
        
        if pred_price is None:
            return None
        
        if (print_play):
            print(f'\n{self.ticker} on {date} predicted to be {pred_price} on {pred_date}')

        return self.make_play(pred_price, strike_strat, risk, print_play, verbose)

    def calc_predicted_option_PnL(self, contract, cp, pred_price, risk, ):
        premium_per_contract = float(contract[f'[{cp}_ASK]'])
        if premium_per_contract <= 0:
            return -999,999
        qty = risk / premium_per_contract

        #option prediction 
        strike = float(contract['[STRIKE]'])
        if cp == 'C':
            predicted_intrinsic_value = (pred_price - strike)*100
        elif cp == 'P':
            predicted_intrinsic_value = (strike - pred_price)*100
        
        predicted_option_PnL = ((predicted_intrinsic_value - premium_per_contract) * qty) + (1000 - risk) # - premium_paid

        return predicted_option_PnL



    
    def make_play(self, pred_price, strike_strat='ATM',risk=1000, print_play=True,verbose=False):
        assert (risk <= 1000)
        try:
            spot = self.pred_week.iloc[0]['[UNDERLYING_LAST]']
            # print('spot ' , spot, 'type', type(spot))
            spot = float(spot)
        except Exception as e:
            print(e)
            return None

        bullish = pred_price > spot
        if bullish:
            # look at calls
            cp = 'C'    
            filt = (self.pred_week['[STRIKE]'].astype(float) >= spot)
            
            
            position = self.pred_week[filt].iloc[0] # is ATM val and default starting position for FBS
            # if strike_strat == 'ATM':
            #     position = self.pred_week[(self.pred_week['[STRIKE]'] >= spot)].iloc[0]
            # elif strike_strat == 'FIND_BEST_STRIKE':
        
            if strike_strat == 'FIND_BEST_STRIKE':
                best = -999
                otm_calls = self.pred_week[filt]
                for i in range(len(otm_calls)):
                    pnl = self.calc_predicted_option_PnL(otm_calls.iloc[i], cp, pred_price, risk)
                    # print(f'ran calc predicted option PnL {i}')
                    if pnl > best:
                        best = pnl
                        position = otm_calls.iloc[i]
                    else:
                        break

  
        else:
            # look at puts
            cp = 'P'
            filt = (self.pred_week['[STRIKE]'].astype(float) <= spot)
            position = self.pred_week[filt].iloc[-1] # default value, satisfies ATM. index goes backwards here
            # if strike_strat == 'ATM' :
                # position = self.pred_week[(self.pred_week['[STRIKE]'] <= spot)]
                # # print(position)
                # position = self.pred_week[(self.pred_week['[STRIKE]'] <= spot)].iloc[-1]
            # elif strike_strat == 'FIND_BEST_STRIKE':
            if strike_strat == 'FIND_BEST_STRIKE':
                best = -999 
                otm_puts = self.pred_week[filt]
                
                # assert(otm_puts.iloc[len(otm_puts)-1] == otm_puts.iloc[-1])
                # prev_was_worse = False
                for i in range(len(otm_puts)-1,0,-1):
                    pnl = self.calc_predicted_option_PnL(otm_puts.iloc[i], cp, pred_price, risk)
                    if pnl > best:
                        best = pnl
                        position = otm_puts.iloc[i]
                    else:
                        break
            
        
        # print('spot: ', spot, 'cp', cp, 'strike', position['[STRIKE]'], 'ask', position[f'[{cp}_ASK]'], 'bid', position[f'[{cp}_BID]'])
        
        future_spot_truth = self.pred_week_on_pred_date['[UNDERLYING_LAST]'].iloc[0]
    
        true_return = (float(future_spot_truth) - spot) / spot
        position_in_future = self.pred_week_on_pred_date[self.pred_week_on_pred_date['[STRIKE]'].astype(float) == float(position['[STRIKE]'])]
        
        #shares
        shares_predicted_return_percent = round(((pred_price - spot) / spot)*100,3)
        # shares_predicted_return = round(((pred_price - spot) / spot),3)
        predicted_baseline_PnL = ((shares_predicted_return_percent/100) * 1000) + 1000

        actual_baseline_PnL = ((true_return * 1000) + 1000 ) if bullish else 1000 
        

        #options
        premium_per_contract = round(float(position[f'[{cp}_ASK]'])*100, 2)
        value_at_expiration = (position_in_future[f'[{cp}_BID]'].astype(float).iloc[0])*100
        # print(position, '\n')
        
        try :
            value_at_expiration = round((float(value_at_expiration)),2)
        except Exception as e:
            return None

        # single_contract_PL = value_at_expiration - premium_per_contract
        qty = round((risk / premium_per_contract), 5)
        
        #actual
        option_exposure_expiration_value = round((value_at_expiration * qty),2)
        actual_option_PnL = option_exposure_expiration_value + (1000 - risk)

        # only works for call right now
        #option prediction 
        strike = float(position['[STRIKE]'])
        predicted_intrinsic_value = (pred_price - strike)*100 # single contract intrinsice value at expiration
        predicted_option_PnL = ((predicted_intrinsic_value - premium_per_contract) * qty) + (1000 - risk) # - premium_paid
        predicted_option_return = round((((predicted_option_PnL / 1000)-1)),2) 
        
        
        baseline_percent = round((((actual_baseline_PnL / 1000)-1) * 100), 3)
        actual_option_percent = round((((actual_option_PnL / 1000)-1) * 100), 3)

        option_outperformance = actual_option_PnL - actual_baseline_PnL

        if print_play:
            if verbose:
                print('Price on date prediction was made: ',spot,'. Actual share price on predicted date: ',future_spot_truth)
                print(f'Price movement: Actual: {round(true_return*100,2)}% Predicted: {shares_predicted_return_percent}%')
                print(f'{strike_strat} contract value went from { premium_per_contract } to { value_at_expiration }') 
                print(f'Premium paid: {risk} ({premium_per_contract} * Qty: {qty}). Option exposure expiration value: {option_exposure_expiration_value}. Actual option PnL: {actual_option_PnL}')
                
            print(f'Predicted: baseline return: {shares_predicted_return_percent}% P/L:${int(predicted_baseline_PnL)}. Predicted Option return: {predicted_option_return*100}% P/L: ${int(predicted_option_PnL)}.' ) 
            print(f'Actual: baseline (shares): {baseline_percent}% P/L:${int(actual_baseline_PnL)}.  Option PnL: {actual_option_percent}% P/L: ${int(actual_option_PnL)}. Result for options:${round(option_outperformance,2)}\n' ) 
        
        return (actual_baseline_PnL, actual_option_PnL, option_outperformance, predicted_baseline_PnL,predicted_option_PnL)