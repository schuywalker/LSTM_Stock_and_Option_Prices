import pandas as pd

class playcf:
    def __init__(self, strat:None, risk:None, pred_date:None, pred_price:None, spot:None, cp:None, position:None, option_return:None, baseline_pnl:None, ):
        self.strat = strat
        self.risk = risk
        self.pred_date = pred_date
        self.pred_price = pred_price
        self.spot = spot
        self.cp = cp
        self.position = position
        self.option_return = option_return
        self.baseline_pnl = baseline_pnl

    def append_to_df(self, df:pd.DataFrame):
        pass
        # df = df.append(self.__dict__, ignore_index=True)
        # return df
