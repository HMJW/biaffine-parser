# -*- coding: utf-8 -*-

from parser import BiaffineParser, Model
from parser.utils import Corpus
from parser.utils.data import TextDataset, batchify

import torch


class Predict(object):

    def add_subparser(self, name, parser):
        subparser = parser.add_parser(
            name, help='Use a trained model to make predictions.'
        )
        subparser.add_argument('--batch-size', default=5000, type=int,
                               help='batch size')
        subparser.add_argument('--fdata', default='../data/treebanks/codt/test.conll',
                               help='path to dataset')
        subparser.add_argument('--fpred', default='pred.conllx',
                               help='path to predicted result')
        subparser.add_argument('--tree', action='store_true',
                               help='whether to force tree')
        subparser.add_argument('--marg', action='store_true',
                               help='whether to use margin prob')
        subparser.add_argument('--task', default="codt",
                               help='task')
        return subparser

    def __call__(self, config):
        print("Load the model")
        vocab = torch.load(config.vocab)
        assert config.task in vocab.task
        task2id = {t:i for i, t in enumerate(vocab.task)}
        task = task2id[config.task]
        parser = BiaffineParser.load(config.model)
        model = Model(config, vocab, parser)

        print("Load the dataset")
        corpus = Corpus.load(config.fdata, task)
        dataset = TextDataset(vocab.numericalize(corpus, False))
        # set the data loader
        loader = batchify(dataset, config.batch_size)

        print("Make predictions on the dataset")
        corpus.heads, corpus.rels = model.predict(loader)

        print(f"Save the predicted result to {config.fpred}")
        corpus.save(config.fpred)
