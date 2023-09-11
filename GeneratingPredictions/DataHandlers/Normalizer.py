import pickle
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import os


class Normalizer:

    def __init__ (self):
        
        self.sc_open = MinMaxScaler()
        self.sc_close = MinMaxScaler()
        self.sc_volume = MinMaxScaler()

    def normalize(self, dfs):
        # normalize data 0-1
        for df in dfs:
            df['open'] = self.sc_open.fit_transform(df[['open']])
            df['close'] = self.sc_close.fit_transform(df[['close']])
            df[['volume']] = self.sc_volume.fit_transform(df[['volume']])
        
        # save scaler params
        base_dir = os.getcwd()
        print(base_dir)
        
        data_models_path = os.path.join(base_dir, 'GeneratingPredictions/out')
        print(data_models_path, "\n\n")

        sc_open_params_path = os.path.join(data_models_path, 'sc_open_params.pkl')
        sc_close_params_path = os.path.join(data_models_path, 'sc_close_params.pkl')
        sc_volume_params_path = os.path.join(data_models_path, 'sc_volume_params.pkl')

        with open(sc_open_params_path, 'wb') as f:
            
            pickle.dump({
                'data_min_': self.sc_open.data_min_,
                'data_max_': self.sc_open.data_max_,
                'scale_': self.sc_open.scale_,
                'min_': self.sc_open.min_,
            }, f)
        
        with open(sc_close_params_path, 'wb') as f:
            
            pickle.dump({
                'data_min_': self.sc_close.data_min_,
                'data_max_': self.sc_close.data_max_,
                'scale_': self.sc_close.scale_,
                'min_': self.sc_close.min_,
            }, f)

        with open(sc_volume_params_path, 'wb') as f:
            pickle.dump({
                'data_min_': self.sc_volume.data_min_,
                'data_max_': self.sc_volume.data_max_,
                'scale_': self.sc_volume.scale_,
                'min_': self.sc_volume.min_,
            }, f)
        return dfs
    
    def inverseNormalizeAllFeatures(self, tensor_predictions):
    
        tensor_predictions = tensor_predictions.detach().cpu()
        numpy_array = tensor_predictions.numpy()
        
        dfs = []
        
        for batch in numpy_array:
            df = pd.DataFrame(batch, columns=['open', 'close', 'volume'])
            df['open'] = self.sc_open.inverse_transform(df[['open']])
            df['close'] = self.sc_close.inverse_transform(df[['close']])
            df[['volume']] = self.sc_volume.inverse_transform(df[['volume']])
            dfs.append(df)
        
        return dfs

    def inverseNormalizeOutput(self, tensor_predictions):
    
        tensor_predictions = tensor_predictions.detach().cpu()
        numpy_array = tensor_predictions.numpy()
        
        dfs = []
        
        for batch in numpy_array:
            df = pd.DataFrame(batch, columns=['close'])
            df['close'] = self.sc_close.inverse_transform(df[['close']])
            dfs.append(df)
        
        return dfs




