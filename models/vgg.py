import torch.nn as nn

class Block(nn.Module):
    def __init__(self, in_C, out_C):
        super(Block, self).__init__()
        self.conv = nn.Conv2d(in_C, out_C, kernel_size=3, stride=1, padding=1)
        self.bn = nn.BatchNorm2d(out_C)
        self.relu = nn.ReLU(inplace=True)
    
    def forward(self, x):
        return self.relu(self.bn(self.conv(x)))

class VGG(nn.Module):
    def __init__(self, cfg):
        super(VGG, self).__init__()
        self.features = self._make_layer(cfg)
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.classifier = nn.Linear(self.in_C, 10)
    
    def _make_layer(self, cfg):
        layers = []
        self.in_C = 3

        for c in cfg:
            if c == 'M':
                layers.append(nn.MaxPool2d(2))
            else:
                layers.append(Block(self.in_C, c))
                self.in_C = c
        return nn.Sequential(*layers)
    
    def forward(self, x):
        x = self.features(x)
        x = self.avg_pool(x)
        x = x.view((-1, self.in_C))
        x = self.classifier(x)
        return x

def VGG11():
    cfg = [64, 'M', 128, 'M', 256, 256, 'M', 512, 512, 'M', 512, 512, 'M']
    return VGG(cfg)