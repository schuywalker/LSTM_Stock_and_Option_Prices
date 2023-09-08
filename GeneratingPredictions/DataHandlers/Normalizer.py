import pickle
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import os


class Normalizer:

    def __init__ (self,sc_price: MinMaxScaler, sc_volume: MinMaxScaler):
        self.sc_price = sc_price
        self.sc_volume = sc_volume

    def normalize(self, dfs):
        # normalize data 0-1
        for df in dfs:
            df[['open', 'close']] = self.sc_price.fit_transform(df[['open','close']])
            df[['volume']] = self.sc_volume.fit_transform(df[['volume']])
        
        # save scaler params
        base_dir = os.getcwd()
        print(base_dir)
        
        data_models_path = os.path.join(base_dir, 'GeneratingPredictions/Models')
        print(data_models_path, "\n\n")

        sc_price_params_path = os.path.join(data_models_path, 'sc_price_params.pkl')
        sc_volume_params_path = os.path.join(data_models_path, 'sc_volume_params.pkl')

        with open(sc_price_params_path, 'wb') as f:
            
            pickle.dump({
                'data_min_': self.sc_price.data_min_,
                'data_max_': self.sc_price.data_max_,
                'scale_': self.sc_price.scale_
            }, f)

        with open(sc_volume_params_path, 'wb') as f:
            pickle.dump({
                'data_min_': self.sc_price.data_min_,
                'data_max_': self.sc_price.data_max_,
                'scale_': self.sc_price.scale_
            }, f)
        return dfs
    
    def inverseNormalizeBatches(self, tensor_predictions):
    
        tensor_predictions = tensor_predictions.detach().cpu()
        numpy_array = tensor_predictions.numpy()
        
        dfs = []
        
        for batch in numpy_array:
            df = pd.DataFrame(batch, columns=['open', 'close', 'volume'])
            df[['open', 'close']] = self.sc_price.inverse_transform(df[['open', 'close']])
            df[['volume']] = self.sc_volume.inverse_transform(df[['volume']])
            dfs.append(df)
        
        return dfs






