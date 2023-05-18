import requests
import pandas as pd

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
    
        



        
