from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import timedelta

import numpy as np


class IteratorBase(ABC):
    """
    Data Iterator class that encapsulates all
    """

    def __init__(self, dataset):
        self.dataset = dataset

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def __next__(self):
        pass

    def replace(self, data, cur_rec):
        self.dataset.replace(data, cur_rec)


class BatchIterator(IteratorBase):
    """
    implementation of the iterator that iterates over batches of consecutive reviews performed in some range of time
    """
    def __init__(self, dataset, initial_delta, test_interval):
        """
        :param dataset: data over which iterates
        :param initial_delta: only reviews after initial_delta will be tested. Earlier reviews only can
                                appear in a training set
        :param test_interval: all reviews in test_interval range are considered a single batch
        """
        super().__init__(dataset)
        self.initial_delta = timedelta(initial_delta, 0)
        self.test_interval = timedelta(test_interval, 0)

        self.start_date = self.dataset.data.date.min()
        self.end_date = self.dataset.data.date.max()

    def set_params(self, initial_delta, test_interval):
        self.initial_delta = timedelta(initial_delta, 0)
        self.test_interval = timedelta(test_interval, 0)

    def __iter__(self):
        self.to_date = self.initial_delta + self.start_date
        self.test_date = self.to_date + self.test_interval

        self.train = self.dataset.data[
            (self.dataset.data.date < self.to_date) & (self.dataset.data.date >= self.start_date)]
        self.test = self.dataset.data[
            (self.dataset.data.date >= self.to_date) & (self.dataset.data.date < self.test_date)]

        return self

    def __next__(self):
        train = self.train
        test = self.test

        self.train = self.test
        self.test = self.dataset.data[
            (self.dataset.data.date >= self.to_date) & (self.dataset.data.date < self.test_date)]

        self.to_date = self.test_date
        self.test_date = self.to_date + self.test_interval
        if self.to_date > self.end_date:
            raise StopIteration
        return train, test


class OneByOneIterator(IteratorBase):
    """
    implementation of a iterator that iterates over reviews one by one
    """
    def __init__(self, dataset):
        super().__init__(dataset)
        self.data = dataset.data.to_dict('records')

    def __iter__(self):
        self.ind = 0
        return self

    def __next__(self):
        if self.ind + 1 >= len(self.data):
            raise StopIteration
        train = self.data[self.ind]
        test = self.data[self.ind + 1]

        self.ind += 1
        return train, test

    def replace(self, data, rev):
        data = deepcopy(data)
        rev_name = self.dataset.get_revname()
        l = len(data[rev_name])
        data[rev_name][np.random.randint(l)] = rev

        return data
