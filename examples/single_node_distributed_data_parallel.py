import argparse

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

from torchvision import models, datasets
from torchvision import transforms

from pytorchtrainer.trainers import SingleOutputTrainer


def main(args):

    # set up network
    net = models.resnet18()
    net.fc = nn.Linear(512, 10)

    # set up training loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(
        net.parameters(),
        lr = args.lr,
    )

    # drop learning rate by factor of 10 after 80% of epochs and again after 90%
    scheduler = torch.optim.lr_scheduler.MultiStepLR(
        optimizer,
        milestones = [int(args.epochs * 0.8), int(args.epochs * 0.9)],
        gamma = 0.1,
        verbose = True
    )

    # transforms for training and validation
    tforms = {
        'train': transforms.Compose([
            transforms.RandomCrop(size=32, padding=4),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.ToTensor(),
            transforms.Normalize(
                (0.5, 0.5, 0.5),
                (0.5, 0.5, 0.5)
            )
        ]),
        'valid': transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(
                (0.5, 0.5, 0.5),
                (0.5, 0.5, 0.5)
            )
        ])
    }

    # set up pytorch dataset and data loaders
    trainset = datasets.CIFAR10(
        root = './data', train = True,
        download = True, transform = tforms['train']
    )

    validset = datasets.CIFAR10(
        root = './data', train = False,
        download = True, transform = tforms['valid']
    )

    # set up our trainer
    trainer = SingleOutputTrainer(
        train_dataset = trainset,
        valid_dataset = validset,
        batch_size = 1024,
        num_workers = 4,
        net = net,
        crit = criterion,
        device_ids = [0,1],
        ddp = True,
        optimizer = optimizer,
        epochs = args.epochs,
        scheduler = scheduler,
    )

    # train the network
    trainer.fit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cifar10 Training')
    parser.add_argument(
        '--lr', default = 0.0003, type = float,
        help = 'learning rate'
    )
    parser.add_argument(
        '--batch_size', default = 256, type = int,
        help = 'how large are mini-batches'
    )
    parser.add_argument(
        '--epochs', default = 300, type = int,
        help = 'how large are mini-batches'
    )
    parser.add_argument('--debug', action = 'store_true',
        help = 'whether to use soft pseudo labels training'
    )
    args = parser.parse_args()

    main(args)