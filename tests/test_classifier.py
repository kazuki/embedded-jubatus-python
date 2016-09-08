import json
import unittest

from embedded_jubatus import Classifier
from jubatus.classifier.types import EstimateResult
from jubatus.classifier.types import LabeledDatum
from jubatus.common import Datum


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


class TestClassifier(unittest.TestCase):
    def test_invalid_configs(self):
        self.assertRaises(TypeError, Classifier)
        self.assertRaises(ValueError, Classifier, 'hoge')
        self.assertRaises(ValueError, Classifier, {})
        self.assertRaises(TypeError, Classifier, {'method': 'hoge'})
        self.assertRaises(RuntimeError, Classifier,
                          {'method': 'hoge', 'converter': {}})
        invalid_config = dict(CONFIG)
        invalid_config['method'] = 'hoge'
        self.assertRaises(RuntimeError, Classifier, invalid_config)

    def test_num(self):
        x = Classifier(CONFIG)
        self.assertEqual(2, x.train([
            ('Y', Datum({'x': 1})),
            ('N', Datum({'x': -1})),
        ]))

        def _test_classify(x):
            y = x.classify([
                Datum({'x': 1}),
                Datum({'x': -1})
            ])
            self.assertEqual(['Y', 'N'], [list(sorted(
                z, key=lambda x:x.score, reverse=True))[0].label for z in y])
            self.assertEqual(x.get_labels(), {'N': 1, 'Y': 1})

        _test_classify(x)
        model = x.dump()

        x.clear()
        self.assertEqual({}, x.get_labels())
        x.set_label('Y')
        x.set_label('N')
        self.assertEqual({'N': 0, 'Y': 0}, x.get_labels())
        x.delete_label(u'Y')
        self.assertEqual({'N': 0}, x.get_labels())

        x = Classifier(CONFIG)
        x.load(model)
        _test_classify(x)
        self.assertEqual(CONFIG, json.loads(x.get_config()))

    def test_str(self):
        x = Classifier(CONFIG)
        self.assertEqual(2, x.train([
            ('Y', Datum({'x': 'y'})),
            ('N', Datum({'x': 'n'})),
        ]))
        y = x.classify([
            Datum({'x': 'y'}),
            Datum({'x': 'n'})
        ])
        self.assertEqual(['Y', 'N'], [list(sorted(
            z, key=lambda x:x.score, reverse=True))[0].label for z in y])

    def test_types(self):
        x = Classifier(CONFIG)
        x.train([
            LabeledDatum('Y', Datum({'x': 'y'})),
            LabeledDatum('N', Datum({'x': 'n'})),
        ])
        y = x.classify([
            Datum({'x': 'y'}),
            Datum({'x': 'n'})
        ])
        self.assertIsInstance(y[0][0], EstimateResult)
        self.assertEqual(['Y', 'N'], [list(sorted(
            z, key=lambda x:x.score, reverse=True))[0].label for z in y])
