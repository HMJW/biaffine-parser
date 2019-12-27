# -*- coding: utf-8 -*-

from parser import BiaffineParser, Model
from parser.utils import Corpus
from parser.utils.data import TextDataset, batchify
from parser.metric import Metric
import torch


def evaluate(model, loaders, names, punct):
    assert len(loaders) == len(names)
    total_metric, total_loss = Metric(), 0
    uas, las = [], []
    for loader, name in zip(loaders, names):
        loss, metric = model.evaluate(loader, punct)
        total_metric += metric
        total_loss += loss
        uas.append(metric.uas)
        las.append(metric.las)
        print(f"{name:6} Loss: {loss:.4f} {metric}")
    print(f"{'mixed':8} {total_metric}")
    print(f"{'average':8} UAS: {sum(uas)/len(uas):.2%} LAS: {sum(las)/len(las):.2%}")
    return total_metric

def print_corpus(corpuses, names):
    for c, n in zip(corpuses, names):
        print(f"{n:35} has {len(c):6} sentences")
    print()

class Evaluate(object):

    def add_subparser(self, name, parser):
        subparser = parser.add_parser(
            name, help='Evaluate the specified model and dataset.'
        )
        subparser.add_argument('--batch-size', default=5000, type=int,
                               help='batch size')
        subparser.add_argument('--buckets', default=64, type=int,
                               help='max num of buckets to use')
        subparser.add_argument('--punct', action='store_true',
                               help='whether to include punctuation')
        subparser.add_argument('--fdata', default='../data/treebanks-filtered/codt/test.conll ../data/treebanks-filtered/ctb9/test.conll ../data/treebanks-filtered/hit/test.conll ../data/treebanks-filtered/pmt/test.conll',
                               help='path to dataset')
        subparser.add_argument('--task', default="codt ctb9 hit pmt",
                               help='all treebanks')
        subparser.add_argument('--tree', action='store_true',
                               help='whether to force tree')
        subparser.add_argument('--marg', action='store_true',
                               help='whether to use margin prob')
        return subparser

    def __call__(self, config):
        print("Load the model")
        task = config.task.split()
        vocab = torch.load(config.vocab)
        task2id = {t:i for i,t in enumerate(vocab.task)}
        parser = BiaffineParser.load(config.model)
        model = Model(config, vocab, parser)

        print("Load the dataset")
        fdata = config.fdata.split()
        corpus = [Corpus.load(f, task2id[t]) for f, t in zip(fdata, task)]
        print_corpus(corpus, fdata)
        datasets = [TextDataset(vocab.numericalize(c), config.buckets) for c in corpus]
        # set the data dataset
        loaders = [batchify(dataset, config.batch_size) for dataset in datasets]
        print("Evaluate the dataset")
        evaluate(model, loaders, task, config.punct)

