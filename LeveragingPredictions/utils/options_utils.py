import pandas as pd
import datetime
from datetime import date, timedelta
import numpy as np


class options_utils:
    
    @staticmethod
    def select_friday(curDate:str, predictionDate:str) -> str:
        curDate = np.array(curDate.strip().split('-'), dtype=int)
        futDate = np.array(predictionDate.strip().split('-'), dtype=int)
        cur = date(*curDate)
        fut = date(*futDate)

        #### monday = 0, sunday = 6, friday = 4 ####
        #TODO: check fut is < last date in datasets (save final dates in memory)
    
        while  fut.weekday() != 4:
            fut += timedelta(1)
        
        assert(fut > cur)
        fut_friday = ' '+fut.strftime('%Y-%m-%d')
        return fut_friday
    
    @staticmethod
    def get_chain(chain:pd.core.groupby.generic.DataFrameGroupBy, date: str) -> pd.DataFrame:
        ret = chain.get_group(date)
        # print(ret.size, ' chain size')
        return ret
    
    @staticmethod
    def slice_week(chain:pd.DataFrame, friday: str):
        filt = chain['[EXPIRE_DATE]'] == friday
        week = chain[filt]
        # assert(not week.empty)
        # print(week.shape, ' week slice shape')
        return week
    
