import pandas as pd
from OptionPlayTranslator import *



if __name__ == '__main__':
    srcDataFrame = pd.read_csv('tslaReduced.csv')
    print('\n')
    df = pd.DataFrame(srcDataFrame)
    df.columns = df.columns.str.strip()
    
    dayGroups = df.groupby('[QUOTE_DATE]', sort=True)


    opt = OPT('TSLA', dayGroups)
    # opt.find_plays(' 2021-03-04', ' 2021-04-19',735,strike_strat='ATM',risk=500,print_play=True,verbose=False)
    predictions = pd.read_csv('tsla_predictions.csv')
    predictions.iloc[0]
    results = []
    for i in range(len(predictions)):  
        pred = predictions.iloc[i]
        pred_list = np.array(pred['Date'].split('-'), dtype=int)
        cur = date(*pred_list)
        if cur.weekday() == 4:
            results.append(opt.find_plays(' 2021-03-04',' '+pred['Date'],float(pred['Pred']),'ATM',100,True,True))