import pandas as pd
from OptionPlayTranslator import *



if __name__ == '__main__':
    srcDataFrame = pd.read_csv('tslaReduced.csv')
    df = pd.DataFrame(srcDataFrame)
    df.columns = df.columns.str.strip()
    
    dayGroups = df.groupby('[QUOTE_DATE]', sort=True)

    print('\ndayGroups first \n', dayGroups.first())


    opt = OPT('TSLA', dayGroups)
    opt.find_plays(' 2019-10-01', ' 2020-01-16',500)


    # rewrite as get_week_chain, takes date and expiration week