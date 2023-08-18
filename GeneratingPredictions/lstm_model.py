import torch
import torch.nn as nn


class LSTM(nn.Module):

    def __init__(self, num_classes, input_size, hidden_size, num_layers, seq_length):
        super(LSTM, self).__init__()
        
        self.num_classes = num_classes
        self.num_layers = num_layers
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.seq_length = seq_length
        
        self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size,
                            num_layers=num_layers, batch_first=True)
        
        self.fc = nn.Linear(hidden_size, num_classes)
       

    def init_hidden(self, batch_size, device):
        h_0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(device)
        c_0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(device)
        return h_0, c_0

    def forward(self, x):
        
        # sequence of BATCHES not relevant, so we init to zeros every time.
        h_0, c_0 = self.init_hidden(x.size(0), x.device)

        # only interested in h_out (hidden cell output) so all other output states are assigned to _
        outputs, (h_out, _) = self.lstm(x, (h_0, c_0))

        # reshape hidden state tensor. i.e. [num_layers, batch_size, hidden_size] -> [numlayers * hidden_size, hidden_size]
        h_out = h_out.view(-1, self.hidden_size)
        
        out = self.fc(h_out)
        
        return out
    

    def train_model(self, model, train_loader, criterion, optimizer):
        self.train() # sets model to training mode. 
        total_loss = 0

        for batch_idx, (data, target) in enumerate(train_loader):
            
            
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            model = model.to(device)
            target = target.to(device)
            # data, target = data.cuda(), target.cuda()
            

            optimizer.zero_grad()  # gradients reset after every forward pass
            outputs = model(data)  # essentially calls forward
            loss = criterion(outputs, target)  # compute loss
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
               
                data, target = data.cuda(), target.cuda()

                outputs = model(data)  # forward pass
                loss = criterion(outputs, target)
                total_loss += loss.item()

                correct_direction = ((predicted > 0) & (target > 0)) | ((predicted < 0) & (target < 0))
                threshold = 0.5
                correst_within_threshold = (predicted - target).abs() < threshold


                _, predicted = outputs.max(1) # _ is actual max values, but predicted is the indicies (predicted class labels). not interested in max values.
                print('target: ',target)
                correct_by_direction_total += correct_direction.float().sum().item()
                correct_by_threshold_total += correst_within_threshold.float().sum().item()
                correct += predicted.eq(target).sum().item() # have to track direction and develop correctness threshold... 
                # correct direction, 
                # correct threshold (normalize by magnitude of move??)
                # is normalization necessary. 
                mse_loss_list.append((predicted - target).pow(2).mean().item())


        average_loss = total_loss / len(test_loader)
        accuracy = 100 * correct / len(test_loader.dataset)

        return average_loss, accuracy,mse_loss_list

    