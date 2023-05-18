import requests
import pandas as pd
import sys

class DatasetBuilder():
    
    def __init__(self, srcName:str, destName:str, *desiredColumns) -> None:
        srcDataFrame = pd.read_csv(srcName)
        # print(srcDataFrame.columns)
        columns = srcDataFrame.columns
        for c in desiredColumns:
            assert(c in columns)
        newDataFrame = pd.DataFrame()
        for column in desiredColumns:
            newDataFrame[column] = srcDataFrame[column]
        newDataFrame.to_csv(destName, index=False, header=True, encoding='utf-8')
    
if __name__ == '__main__':
    dsb = DatasetBuilder('tsla_2019_2022.csv', 'tslaReduced.csv',' [UNDERLYING_LAST]', ' [EXPIRE_DATE]',
       ' [EXPIRE_UNIX]', ' [DTE]', ' [C_DELTA]')
        
'''
headers in kaggle tsla_2019_2022.csv. have to add single quotes like 'col' or usually ' col'
Index(['[QUOTE_UNIXTIME]', ' [QUOTE_READTIME]', ' [QUOTE_DATE]',
       ' [QUOTE_TIME_HOURS]', ' [UNDERLYING_LAST]', ' [EXPIRE_DATE]',
       ' [EXPIRE_UNIX]', ' [DTE]', ' [C_DELTA]', ' [C_GAMMA]', ' [C_VEGA]',
       ' [C_THETA]', ' [C_RHO]', ' [C_IV]', ' [C_VOLUME]', ' [C_LAST]',
       ' [C_SIZE]', ' [C_BID]', ' [C_ASK]', ' [STRIKE]', ' [P_BID]',
       ' [P_ASK]', ' [P_SIZE]', ' [P_LAST]', ' [P_DELTA]', ' [P_GAMMA]',
       ' [P_VEGA]', ' [P_THETA]', ' [P_RHO]', ' [P_IV]', ' [P_VOLUME]',
       ' [STRIKE_DISTANCE]', ' [STRIKE_DISTANCE_PCT]'],
'''
        


        
