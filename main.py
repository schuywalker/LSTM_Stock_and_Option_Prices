import pandas as pd
from OptionPlayTranslator import *



if __name__ == '__main__':
    srcDataFrame = pd.read_csv('tslaReduced.csv')
    df = pd.DataFrame(srcDataFrame)
    df.columns = df.columns.str.strip()
    
    dayGroups = df.groupby('[QUOTE_DATE]', sort=True)

    print('\ndayGroups first \n', dayGroups.first())


    OPT = OptionPlayTranslator('AAPL', dayGroups)
    OPT.findPlays(' 2019-10-01', ' 2022-10-25')