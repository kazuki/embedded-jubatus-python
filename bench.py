import random
import timeit

import numpy as np
from scipy.sparse import csr_matrix

from jubatus.common import Datum
from jubatus.classifier.types import LabeledDatum
from embedded_jubatus import Classifier


CONFIG = {
    "method": "perceptron",
    "converter": {
        "num_filter_types": {},
        "num_filter_rules": [],
        "string_filter_types": {},
        "string_filter_rules": [],
        "num_types": {},
        "num_rules": [
            {"key": "*", "type": "num"}
        ],
        "string_types": {},
        "string_rules": [
            {"key": "*", "type": "space",
             "sample_weight": "bin", "global_weight": "bin"}
        ]
    },
    "parameter": {}
}


def gen_datum(cols, rows, density):
    ret = []
    for i in range(rows):
        d = Datum()
        for j in range(cols):
            if random.random() < density:
                d.add_number(str(j), random.random())
        ret.append(d)
    return ret

def gen_ndarray(cols, rows, density):
    ret = np.zeros((rows, cols))
    for i in range(rows):
        for j in range(cols):
            if random.random() < density:
                ret[i, j] = random.random()
    return ret

def gen_csr(cols, rows, density):
    return csr_matrix(gen_ndarray(cols, rows, density))

def gen_label_list(rows, kinds):
    ret = [None] * rows
    for i in range(rows):
        ret[i] = str(int(random.uniform(0, kinds)))
    return ret

def gen_label_ndarray(rows, kinds):
    ret = np.zeros(rows, dtype='i4')
    for i in range(rows):
        ret[i] = int(random.uniform(0, kinds))
    return ret


def bench(cols, rows, density, label_kinds):
    array = gen_ndarray(cols, rows, density)
    labels = gen_label_ndarray(rows, label_kinds)
    sparse = gen_csr(cols, rows, density)
    datum_list = [
        LabeledDatum(l, d)
        for l, d in zip(gen_label_list(rows, label_kinds), gen_datum(cols, rows, density))
    ]

    def create():
        return Classifier(CONFIG)

    def run0():
        c = create()
        c.train(datum_list)

    def run1():
        c = create()
        c.partial_fit(array, labels)

    def run2():
        c = create()
        c.partial_fit(sparse, labels)

    def run(stmt):
        return min(timeit.repeat(stmt=stmt, repeat=5, number=1))

    print('rows={}, cols={}, density={}, labels={}'.format(rows, cols, density, label_kinds))
    print('  datum:   {}'.format(run(run0)))
    print('  ndarray: {}'.format(run(run1)))
    print('      csr: {}'.format(run(run2)))


bench(10, 10000, 1.0, 2)
bench(10000, 10, 1.0, 2)
bench(10000, 1000, 0.001, 2)
