#
# Demo:
# python3 bin/transfer_learning.py --epochs 3 --pretrained True --save_folder spam --attribute neck_design_labels
# 
from utils.datasets import create_dataset
from utils.train import train_model
from utils.models import create_model
import torchvision
from torch import nn
import torch
import torch.optim as optim
from torch.optim import lr_scheduler
from torch.autograd import Variable
import numpy as np
import time
import argparse
from pathlib import Path


parser = argparse.ArgumentParser(description='FashionAI')
parser.add_argument('--model', type=str, default='resnet34', metavar='M',
                    help='model name')
parser.add_argument('--optimizer', type=str, default='Adam', metavar='O',
                    help='Chosed optimizer')
parser.add_argument('--attribute', type=str, default='coat_length_labels', metavar='A',
                    help='fashion attribute (default: coat_length_labels)')
parser.add_argument('--epochs', type=int, default=50, metavar='N',
                    help='number of epochs to train (default: 50)')
parser.add_argument('--save_folder', type=str, default='resnet34', metavar='S',
                    help='Subdir of ./log directory to save model.pth files')
parser.add_argument('--pretrained', type=str, default='False', metavar='P', 
                    choices=['True', 'False'],
                    help='If True, only train last layer of model')
args = parser.parse_args()


AttrKey = {
    'coat_length_labels':8,
    'collar_design_labels':5,
    'lapel_design_labels':5,
    'neck_design_labels':5,
    'neckline_design_labels':10,
    'pant_length_labels':6,
    'skirt_length_labels':6,
    'sleeve_length_labels':9, }

# Create dataloader
out = create_dataset(args.attribute)
dataloaders = out['dataloaders']
dataset_sizes = out['dataset_sizes']

# Create CNN model
use_gpu = torch.cuda.is_available()
model_conv = create_model(model_key=args.model,
                          pretrained=eval(args.pretrained),
                          num_of_classes=AttrKey[args.attribute],
                          use_gpu=use_gpu)

criterion = nn.CrossEntropyLoss()

# Observe that only parameters of final layer are being optimized as
# opoosed to before.
if eval(args.pretrained):
    parameters_totrain = model_conv.fc.parameters()
else:
    parameters_totrain = model_conv.parameters()

# Choose optimizer for training
if args.optimizer == 'SGD':
    optimizer_conv = optim.SGD(parameters_totrain, lr=0.001, momentum=0.9)
elif args.optimizer == 'Adam':
    optimizer_conv = optim.Adam(parameters_totrain, lr=0.001)

# Decay LR by a factor of 0.1 every 7 epochs
exp_lr_scheduler = lr_scheduler.StepLR(optimizer_conv, step_size=7, gamma=0.1)

# Kick off the train
model_conv = train_model(model_conv,
                         criterion,
                         optimizer_conv,
                         exp_lr_scheduler,
                         dataloaders,
                         dataset_sizes,
                         use_gpu,
                         num_epochs=args.epochs)

# Save model parameters
save_folder = Path('log') / Path(args.save_folder)
if not save_folder.exists():
    save_folder.mkdir(parents=True)

# Save model
torch.save(model_conv.state_dict(), str(save_folder / Path(args.attribute+'.pth')))
print('Saved to {}'.format(str(save_folder / Path(args.attribute+'.pth'))))
