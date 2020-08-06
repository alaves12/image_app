import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.utils.model_zoo as model_zoo
from collections import OrderedDict
import torchvision.models as models
from torch.autograd import Variable
import math

class refineblock(nn.Module):
    def __init__(self, in_planes):
        super(refineblock, self).__init__()

        self.conv_refin = nn.Conv2d(in_planes, 20, 3, 1, 1)
        self.tanh = nn.Tanh()
        
        self.conv1010 = nn.Conv2d(20, 1, kernel_size=1, stride=1, padding=0)  # 1mm
        self.conv1020 = nn.Conv2d(20, 1, kernel_size=1, stride=1, padding=0)  # 1mm
        self.conv1030 = nn.Conv2d(20, 1, kernel_size=1, stride=1, padding=0)  # 1mm
        self.conv1040 = nn.Conv2d(20, 1, kernel_size=1, stride=1, padding=0)  # 1mm
        self.refine3 = nn.Conv2d(20 + 4, 20, kernel_size=3, stride=1, padding=1)
        ##
        self.refine4 = nn.Conv2d(20, 20, kernel_size=3, stride=1, padding=1)
        self.refine5 = nn.Conv2d(20, 20, kernel_size=7, stride=1, padding=3)
        self.refine6 = nn.Conv2d(20, 3, kernel_size=7, stride=1, padding=3)
        ##
        self.upsample = F.upsample
        self.relu = nn.ReLU(inplace=True)
        self.sig = nn.Sigmoid()
    
    def forward(self, x):

        x9 = self.relu(self.conv_refin(x))


        shape_out = x9.data.size()
        shape_out = shape_out[2:4]
        x101 = F.avg_pool2d(x9, 32)
        x102 = F.avg_pool2d(x9, 16)
        x103 = F.avg_pool2d(x9, 8)
        x104 = F.avg_pool2d(x9, 4)
        x1010 = self.upsample(self.relu(self.conv1010(x101)), size=shape_out, mode='bilinear',align_corners=True)
        x1020 = self.upsample(self.relu(self.conv1020(x102)), size=shape_out, mode='bilinear',align_corners=True)
        x1030 = self.upsample(self.relu(self.conv1030(x103)), size=shape_out, mode='bilinear',align_corners=True)
        x1040 = self.upsample(self.relu(self.conv1040(x104)), size=shape_out, mode='bilinear',align_corners=True)
        dehaze = torch.cat((x1010, x1020, x1030, x1040, x9), 1)

        dehaze = self.tanh(self.refine3(dehaze))
        dehaze = self.relu(self.refine4(dehaze))
        dehaze = self.relu(self.refine5(dehaze))     
        
        dehaze = self.refine6(dehaze)
        return dehaze


class Unet(nn.Module):
    def __init__(self):
        super(Unet, self).__init__()

        self.refine = refineblock(19)
        
        encoder = []
        decoder = []
        def encodeblock(in_f, out_f, firstblock=False):
            layers=[]
            if firstblock:
                layers.append(nn.BatchNorm2d(in_f))
            
            layers.append(nn.LeakyReLU(0.2, inplace=False))
            layers.append(nn.Conv2d(in_f, out_f, 3, 2, 1))
            layers.append(nn.BatchNorm2d(out_f))
            layers.append(nn.LeakyReLU(0.2, inplace=False))
            return layers
        
        def decodeblock(in_f, out_f, firstblock=False):
            layers=[]
            
            layers.append(nn.LeakyReLU(0.2, inplace=False))
            layers.append(nn.ConvTranspose2d(in_f, out_f, kernel_size=2, stride=2))
            layers.append(nn.BatchNorm2d(out_f))
            layers.append(nn.LeakyReLU(0.2, inplace=False))
            return layers



        en_channels = [16,32,64]
        in_filters = 3
           
        self.encoder1 = nn.Sequential(*encodeblock(in_filters, en_channels[0], firstblock=True))
        self.encoder2 = nn.Sequential(*encodeblock(en_channels[0], en_channels[1]))
        self.encoder3 = nn.Sequential(*encodeblock(en_channels[1], en_channels[2]))
        
        de_channels = [32,32,16]

        self.decoder1 = nn.Sequential(*decodeblock(en_channels[2], de_channels[0], firstblock=True))
        self.decoder2 = nn.Sequential(*decodeblock(de_channels[0] + en_channels[1], de_channels[1]))
        self.decoder3 = nn.Sequential(*decodeblock(de_channels[1] + en_channels[0], de_channels[2]))


    def forward(self, x):
        x1 = self.encoder1(x)
        x2 = self.encoder2(x1)
        x3 = self.encoder3(x2)

        x4 = self.decoder1(x3)
        x41 = torch.cat([x4, x2], dim=1)
        x5 = self.decoder2(x41)
        x51 = torch.cat([x5, x1], dim=1)
        x6 = self.decoder3(x51)


        x12 = torch.cat([x,x6], dim=1)
        dehaze = self.refine(x12)

        return dehaze

class JointDiscriminator(nn.Module):
    def __init__(self, input_shape):
        super(JointDiscriminator, self).__init__()

        self.input_shape = input_shape
        in_channels, in_height, in_width = self.input_shape
        patch_h, patch_w = int(in_height / 2 ** 4), int(in_width / 2 ** 4)
        self.output_shape = (1, patch_h, patch_w)

        def discriminator_block(in_filters, out_filters, first_block=False):
            layers = []
            layers.append(nn.Conv2d(in_filters, out_filters, kernel_size=3, stride=1, padding=1))
            if not first_block:
                layers.append(nn.BatchNorm2d(out_filters))
            layers.append(nn.LeakyReLU(0.2, inplace=False))
            layers.append(nn.Conv2d(out_filters, out_filters, kernel_size=3, stride=2, padding=1))
            layers.append(nn.BatchNorm2d(out_filters))
            layers.append(nn.LeakyReLU(0.2, inplace=False))
            return layers

        layers = []
        in_filters = in_channels
        for i, out_filters in enumerate([64, 128, 256, 512]):
            layers.extend(discriminator_block(in_filters, out_filters, first_block=(i == 0)))
            in_filters = out_filters

        layers.append(nn.Conv2d(out_filters, 1, kernel_size=3, stride=1, padding=1))
        layers.append(nn.Sigmoid())

        self.model = nn.Sequential(*layers)

    def forward(self, img_1,img_2):
        img = torch.cat((img_1,img_2),1)
        return self.model(img)

        
            
            

