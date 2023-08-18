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

    datasetBuilder = DatasetBuilder()
    train_loader,test_loader = datasetBuilder.buildDataset(window_length, seq_length)

    num_epochs = 1
    learning_rate = 0.01

    input_size = 1
    hidden_size = 2
    num_layers = 1

    num_classes = 1

    print('in main')



    model = LSTM(num_classes, input_size, hidden_size, num_layers, seq_length=seq_length)
    print('model constructed')

    criterion = torch.nn.MSELoss()    # mean-squared error for regression
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)


    
    num_epochs = 10
    
    for epoch in range(num_epochs):
        train_loss = model.train_model(model, train_loader, criterion, optimizer)
        test_loss, test_accuracy = model.evaluate(model, test_loader, criterion)
        print(f"Epoch: {epoch+1}/{num_epochs}, Train Loss: {train_loss:.4f}, Test Loss: {test_loss:.4f}, Test Accuracy: {test_accuracy:.2f}%")



if __name__ == '__main__':
    main()


    