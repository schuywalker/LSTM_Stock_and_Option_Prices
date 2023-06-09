import pandas as pd
from OptionPlayTranslator import *



if __name__ == '__main__':
    # #TSLA
    # srcDataFrame = pd.read_csv('tslaReduced.csv')
    # print('\n')
    # df = pd.DataFrame(srcDataFrame)
    # df.columns = df.columns.str.strip()
    
    # dayGroups = df.groupby('[QUOTE_DATE]', sort=True)


    # opt = OPT('TSLA', dayGroups)
    # # opt.find_plays(' 2021-03-04', ' 2021-04-19',735,strike_strat='ATM',risk=500,print_play=True,verbose=False)
    # predictions = pd.read_csv('tsla_predictions.csv')
    # predictions.iloc[0]
    # results = []
    # for i in range(len(predictions)):  
    #     pred = predictions.iloc[i]
    #     pred_list = np.array(pred['Date'].split('-'), dtype=int)
    #     cur = date(*pred_list)
    #     if cur.weekday() == 4:
    #         results.append(opt.find_plays(' 2021-03-04',' '+pred['Date'],float(pred['Pred']),'FIND_BEST_STRIKE',1000,True,True))
    
    
    #AAPL
    srcDataFrame = pd.read_csv('AAPL_chains_reduced_21_22Jan.csv')
    print('\n')
    df = pd.DataFrame(srcDataFrame)
    df.columns = df.columns.str.strip()

    print(df.columns)
    
    dayGroups = df.groupby('[QUOTE_DATE]', sort=True)


    opt = OPT('AAPL', dayGroups)
    # opt.find_plays(' 2021-03-04', ' 2021-04-19',735,strike_strat='ATM',risk=500,print_play=True,verbose=False)
    predictions = pd.read_csv('apple_predictions.csv')
    predictions.iloc[0]
    results = []
    ATM_outperformances = []
    for i in range(len(predictions)):  
        pred = predictions.iloc[i]
        pred_list = np.array(pred['Date'].split('-'), dtype=int)
        cur = date(*pred_list)
        if cur.weekday() == 4:
            day = opt.find_plays(' 2021-03-04',' '+pred['Date'],float(pred['Pred']),'ATM',1000,True,True)
            results.append(day)
            if day:
                ATM_outperformances.append(day[2])
        
    opt = OPT('AAPL', dayGroups)
    # opt.find_plays(' 2021-03-04', ' 2021-04-19',735,strike_strat='ATM',risk=500,print_play=True,verbose=False)
    predictions = pd.read_csv('apple_predictions.csv')
    predictions.iloc[0]
    results = []
    FTB_outperformances = []
    for i in range(len(predictions)):  
        pred = predictions.iloc[i]
        pred_list = np.array(pred['Date'].split('-'), dtype=int)
        cur = date(*pred_list)
        if cur.weekday() == 4:
            day = opt.find_plays(' 2021-03-04',' '+pred['Date'],float(pred['Pred']),'FIND_BEST_STRIKE',1000,True,True)
            results.append(day)
            if day:
                FTB_outperformances.append(day[2])
    # print('avg option outperformance:', np.mean(outperformances))

    print('ATM_outperformances \t FTB_outperformances')
    for i in range(len(ATM_outperformances)):
        print(f'{round((ATM_outperformances[i]),2)} \t\t {round(FTB_outperformances[i],2)}')
        

    