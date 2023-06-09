import pandas as pd

class DatasetBuilder():

    # stand alone script to remove columns from csv files and save as a new csv for faster load times.
    
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
    
# if __name__ == '__main__':
#     dsb = DatasetBuilder('tsla_2019_2022.csv', 'tslaReduced.csv',' [QUOTE_DATE]',' [UNDERLYING_LAST]', ' [EXPIRE_DATE]',
#        ' [DTE]', ' [C_LAST]',
#         ' [C_BID]', ' [C_ASK]', ' [STRIKE]', ' [P_BID]',
#        ' [P_ASK]', ' [P_LAST]',)

if __name__ == '__main__':
    dsb = DatasetBuilder('./apple/21_master_list.txt', 'AAPL_chains_reduced_21_22Jan.csv',' [QUOTE_DATE]',' [UNDERLYING_LAST]', ' [EXPIRE_DATE]',
        ' [DTE]', ' [C_LAST]',
            ' [C_BID]', ' [C_ASK]', ' [STRIKE]', ' [P_BID]',
        ' [P_ASK]', ' [P_LAST]',)

        
