import math
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from DataHandlers.Normalizer import Normalizer
import pickle
from DatasetBuilder import DatasetBuilder
from lstm_model import LSTM

def main():


    window_length = 40 # totalDays
    seq_length = 30 # trainDays

    sc_price = MinMaxScaler()
    sc_volume = MinMaxScaler()
    normalizer = Normalizer(sc_price, sc_volume)

    use_saved_data = True
    if (use_saved_data):
        train_loader = torch.load('train_loader.pth')
        test_loader = torch.load('test_loader.pth')
        with open('GeneratingPredictions/out/sc_price_params.pkl', 'rb') as f:
            sc_price_params = pickle.load(f)
            # normalizer.sc_price.set_params(**sc_price_params)
            for attribute, value in sc_price_params.items():
                setattr(normalizer.sc_price, attribute, value)

        with open('GeneratingPredictions/out/sc_volume_params.pkl', 'rb') as f:
            sc_volume_params = pickle.load(f)
            # normalizer.sc_volume.set_params(**sc_volume_params)    
            for attribute, value in sc_volume_params.items():
                setattr(normalizer.sc_volume, attribute, value)                 
    else:    
        datasetBuilder = DatasetBuilder()
        train_loader,test_loader = datasetBuilder.buildDataset(normalizer, window_length, seq_length)
        torch.save(train_loader, 'GeneratingPredictions/out/train_loader.pth')
        torch.save(test_loader, 'GeneratingPredictions/out/test_loader.pth')

    print("Is price scaler fitted?", hasattr(normalizer.sc_price, 'scale_') and hasattr(normalizer.sc_price, 'data_min_'))
    print("Is volume scaler fitted?", hasattr(normalizer.sc_volume, 'scale_') and hasattr(normalizer.sc_volume, 'data_min_'))

    num_epochs = 1
    learning_rate = 0.01

    input_size = 3 # features (open close volume)
    hidden_size = 2
    num_layers = 1

    # num_outputs = 3 # adjust to 1 later, only need to open price.

    intermediate_layers_in_forecast = 15

    print('in main')

    

    model = LSTM( input_size=input_size, hidden_size=hidden_size, num_layers=num_layers, seq_length=seq_length, intermediate_layers_in_forecast=intermediate_layers_in_forecast)
    print('model constructed')

    criterion = torch.nn.MSELoss()    # mean-squared error for regression because we're predicting continuous values.
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)


    
    num_epochs = 20
    avg_losses = []

    combined_dfs = []
    
    for epoch in range(num_epochs):
        train_loss = model.train_model(model, train_loader, criterion, optimizer)
        input_data, raw_predictions, ground_truth, avg_test_loss, test_accuracy, mse_loss_list = model.evaluate(model, test_loader, criterion)
        avg_losses.append(avg_test_loss)
        print(f"\nEpoch: {epoch+1}/{num_epochs}, Train Loss: {train_loss:.4f}, Test Loss: {avg_test_loss:.4f}, Test Accuracy: {test_accuracy:.2f}%")
        denormInputData = normalizer.inverseNormalizeBatches(input_data)
        denormPred = normalizer.inverseNormalizeBatches(raw_predictions)
        denormGroundTruth = normalizer.inverseNormalizeBatches(ground_truth)
        for i in range(len(denormInputData)):
            combined_df = pd.concat([denormInputData[i], denormGroundTruth[i], denormPred[i]], axis=0)
            # print(combined_df)
            combined_dfs.append(combined_df)   

    final_df = pd.concat(combined_dfs)
    final_df.to_csv('GeneratingPredictions/out/results.csv', index=False)


        # for i in range(denormPred.shape[0]):
        # print("pred: ",denormPred[i], "\t\t", "ground truth: ",denormGroundTruth[i])
        
        
        

    print("\navg loss over epochs: ",((sum(avg_losses)/len(avg_losses))))


if __name__ == '__main__':
    main()


    