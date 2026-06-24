import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader

class HealthNet(nn.Module):
    def __init__(self, input_dim):
        super(HealthNet, self).__init__()
        self.fc1 = nn.Linear(input_dim, 32)
        self.fc2 = nn.Linear(32, 16)
        self.fc3 = nn.Linear(16, 8)
        self.fc4 = nn.Linear(8, 1)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        return torch.sigmoid(self.fc4(x))

def train(net, trainloader, epochs):
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(net.parameters(), lr=0.001)
    net.train()
    for _ in range(epochs):
        for data, target in trainloader:
            optimizer.zero_grad()
            output = net(data)
            # Ensure outputs are in [0, 1] and handle NaNs for stability
            output = torch.nan_to_num(output, nan=0.5)
            output = torch.clamp(output, 1e-7, 1.0 - 1e-7)
            loss = criterion(output, target.view(-1, 1).float())
            loss.backward()
            optimizer.step()

def test(net, testloader):
    criterion = nn.BCELoss()
    correct, total, loss = 0, 0, 0.0
    net.eval()
    with torch.no_grad():
        for data, target in testloader:
            outputs = net(data)
            # Ensure outputs are in [0, 1] and handle NaNs for stability
            outputs = torch.nan_to_num(outputs, nan=0.5)
            outputs = torch.clamp(outputs, 1e-7, 1.0 - 1e-7)
            loss += criterion(outputs, target.view(-1, 1).float()).item()
            predicted = (outputs > 0.5).float()
            total += target.size(0)
            correct += (predicted == target.view(-1, 1).float()).sum().item()
    if len(testloader) == 0:
        return 0.0, 0.0
    return loss / len(testloader), correct / total