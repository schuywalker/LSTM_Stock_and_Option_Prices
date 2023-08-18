import torch
import torch.nn as nn


# x input sequence: 
# (seq_len, batch_size, input_size)
# 
# hidden cell (h_0) and initial cell (c_0) input sequence: 
# (num_layers * num_directions, batch_size, hidden_size)

class LSTM(nn.Module):

    def __init__(self, input_size, hidden_size, num_layers, seq_length, intermediate_layers_in_forecast):
        super(LSTM, self).__init__()
        
        
        self.num_layers = num_layers
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.seq_length = seq_length
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size,
                            num_layers=num_layers, batch_first=True)
        # batch_first= changes shape (batch_size, seq_len, features).
        
        
        self.intermediate_layers = intermediate_layers_in_forecast
        # experiment with this later ^^
        # heuristic is between hidden_size and output size (10 days * 3 features = 30).
        # normal rules apply - higher is more powerful, costly, and risks overfitting

        self.forecast = nn.Sequential(
            nn.Linear(hidden_size, self.intermediate_layers),
            nn.ReLU(),
            nn.Linear(self.intermediate_layers, 10 * 3)  # 10 days of forecasts, 3 features each
        )

        self.fc = nn.Linear(hidden_size, input_size)
       

    def init_hidden(self, batch_size, device):
        h_0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(device)
        c_0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(device)
        return h_0, c_0

    def forward(self, x):
        # sequence of BATCHES not relevant, so we init to zeros every time.
        
        h_0, c_0 = self.init_hidden(x.size(0), x.device) # x.size(1) is batch size
        print ('x.shape:', x.shape, 'h_0.shape:', h_0.shape, 'c_0.shape:', c_0.shape)
        lstm_out, (hn, cn) = self.lstm(x, (h_0, c_0))
        print ('lstm_out.shape ',lstm_out.shape, 'hn.shape ',hn.shape, 'cn.shape ',cn.shape)
        
        last_hidden_state = hn[-1]
        print('hn shape', hn.shape, 'hn[-1].shape ', hn[-1].shape)
        forecast_out = self.forecast(last_hidden_state)
        print('\n forecast out shape:\n',forecast_out.shape)
        forecast3D = forecast_out.view(x.size(0),10,3)
        print('forecast3D.shape ',forecast3D.shape)
        print('forecast3D[0] ',forecast3D[0])
        return forecast3D
        # return forecast.view(x.size(0), 10, 3)
         
        # out = self.fc(lstm_out) 
        # print('out.shape ',out.shape)
        # return out
    

    def train_model(self, model, train_loader, criterion, optimizer):
        self.train() # sets model to training mode. 
        total_loss = 0
        
        model = model.to(self.device)

        for batch_idx, (data, target) in enumerate(train_loader):
 
            data, target = data.to(self.device), target.to(self.device)
            print('data.shape ',data.shape, ' target.shape: ', target.shape)

            optimizer.zero_grad()  # gradients reset after every forward pass
            outputs = model(data)  # essentially calls forward. outputs.shape is 30,1 currently
            print('outputs.shape: ',outputs.shape,' target.shape: ',target.shape,'\n\n')
            loss = criterion(outputs, target)  
            loss.backward()  # backward pass
            optimizer.step()  # update the model parameters

            total_loss += loss.item()

        average_loss = total_loss / len(train_loader)
        return average_loss

    
    
    def evaluate(self, model, test_loader, criterion):
        self.eval() # activate evaluation mode
        total_loss = 0
        correct_by_direction_total = 0
        correct_by_threshold_total = 0
       
        correct = 0

        mse_loss_list = []

        with torch.no_grad():  # no need to compute gradients during evaluation
            for data, target in test_loader:
               
                data, target = data.to(self.device), target.to(self.device)

                outputs = model(data)  # forward pass
                loss = criterion(outputs, target)
                total_loss += loss.item()

                # correct_direction = ((predicted > 0) & (target > 0)) | ((predicted < 0) & (target < 0))
                threshold = 0.5
                correst_within_threshold = (predicted - target).abs() < threshold


                _, predicted = outputs.max(1) # _ is actual max values, but predicted is the indicies (predicted class labels). not interested in max values.
                print('target: ',target)
                # correct_by_direction_total += correct_direction.float().sum().item()
                correct_by_threshold_total += correst_within_threshold.float().sum().item()
                correct += predicted.eq(target).sum().item() # have to track direction and develop correctness threshold... 
                # correct direction, 
                # correct threshold (normalize by magnitude of move??)
                # is normalization necessary. 
                mse_loss_list.append((predicted - target).pow(2).mean().item())


        average_loss = total_loss / len(test_loader)
        accuracy = 100 * correct / len(test_loader.dataset)

        return average_loss, accuracy,mse_loss_list

    