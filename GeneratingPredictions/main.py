import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

from DatasetBuilder import DatasetBuilder
from lstm_model import LSTM

def main():


    window_length = 40 # totalDays
    seq_length = 30 # trainDays

    use_saved_data = True
    if (use_saved_data):
        train_loader = torch.load('train_loader.pth')
        test_loader = torch.load('test_loader.pth')
    else:    
        datasetBuilder = DatasetBuilder()
        train_loader,test_loader = datasetBuilder.buildDataset(window_length, seq_length)
        torch.save(train_loader, 'train_loader.pth')
        torch.save(test_loader, 'test_loader.pth')

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


    
    num_epochs = 10
    
    for epoch in range(num_epochs):
        train_loss = model.train_model(model, train_loader, criterion, optimizer)
        test_loss, test_accuracy = model.evaluate(model, test_loader, criterion)
        print(f"Epoch: {epoch+1}/{num_epochs}, Train Loss: {train_loss:.4f}, Test Loss: {test_loss:.4f}, Test Accuracy: {test_accuracy:.2f}%")



if __name__ == '__main__':
    main()


    