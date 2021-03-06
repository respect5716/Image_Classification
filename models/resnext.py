"""
ResNeXt
Saining Xie, Aggregated Residual Transformations for Deep Neural Networks
https://arxiv.org/abs/1611.05431
"""

import torch.nn as nn


class Bottleneck(nn.Module):
    expansion = 2
    
    def __init__(self, in_C, bottleneck_width, groups, stride):
        super(Bottleneck, self).__init__()
        bn_C = bottleneck_width * groups
        out_C = bn_C * self.expansion

        self.shortcut = nn.Sequential()
        if stride > 1 or in_C != out_C:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_C, out_C, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_C)
            )

        self.conv1 = nn.Conv2d(in_C, bn_C, kernel_size=1, bias=False)
        self.bn1 = nn.BatchNorm2d(bn_C)
        self.relu1 = nn.ReLU()

        self.conv2 = nn.Conv2d(bn_C, bn_C, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(bn_C)
        self.relu2 = nn.ReLU()

        self.conv3 = nn.Conv2d(bn_C, out_C, kernel_size=1, bias=False)
        self.bn3 = nn.BatchNorm2d(out_C)
        self.relu3 = nn.ReLU()

    def forward(self, x):
        shortcut = self.shortcut(x)
        x = self.relu1(self.bn1(self.conv1(x)))
        x = self.relu2(self.bn2(self.conv2(x)))
        x = self.bn3(self.conv3(x))
        x += shortcut
        x = self.relu3(x)
        return x


class ResNeXt(nn.Module):
    def __init__(self, cfg, num_classes=10):
        super(ResNeXt, self).__init__()
        self.bottleneck_width = cfg['bottleneck_width']
        self.groups = cfg['groups']
        self.in_C = cfg['in_C']

        self.head = nn.Sequential(
            nn.Conv2d(3, self.in_C, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(self.in_C),
            nn.ReLU()
        )

        self.layer1 = self._make_layer(cfg['num_blocks'][0], 1)
        self.layer2 = self._make_layer(cfg['num_blocks'][1], 2)
        self.layer3 = self._make_layer(cfg['num_blocks'][2], 2)
        self.layer4 = self._make_layer(cfg['num_blocks'][3], 2)
        
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(self.in_C, num_classes)
        )

    def _make_layer(self, num_blocks, stride):
        strides = [stride] + [1] * (num_blocks - 1)
        layers = []
        for st in strides:
            layers.append(Bottleneck(self.in_C, self.bottleneck_width, self.groups, st))
            self.in_C = Bottleneck.expansion * self.groups * self.bottleneck_width
        self.bottleneck_width *= 2
        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.head(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.classifier(x)
        return x


def ResNeXt50_2x32d():
    cfg = {
        'in_C': 32,
        'groups': 2,
        'bottleneck_width': 32,
        'num_blocks': [3, 4, 6, 3]
    }
    return ResNeXt(cfg)