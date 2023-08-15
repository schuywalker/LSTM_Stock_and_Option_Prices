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
    
