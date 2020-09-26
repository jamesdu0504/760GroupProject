import unittest

from mlxtend.frequent_patterns import fpgrowth
from metrics.side_effects_factor import side_effects_factor
from arm_utilities import get_closed_itemsets, itemsets_from_closed_itemsets
import datasets.import_datasets as im
from algorithms.rps import rps

class TestSideEffectsFactor(unittest.TestCase):

    min_support = 0.3
    original_DB = None
    basket_sets = None

    @classmethod
    def setUpClass(cls):

        # Get toy data, WARNING! Had to change relative reference for this to work
        cls.basket_sets = im.import_dataset("toydata")

        # Gather all itemsets from the original database by setting minimum support possible
        cls.original_DB = fpgrowth(cls.basket_sets, min_support=(1 / len(cls.basket_sets)), use_colnames=True,
                                   verbose=False)

    def test_side_effects_factor_with_rps(self):
        # Compute closed itemsets of original DB
        closed_IS, itemsets = get_closed_itemsets(self.basket_sets, 1 / len(self.basket_sets))

        # Get sanitised closed itemsets using RPS
        sensitive_IS = {frozenset(['1', '2']), frozenset(['4'])}
        sanitized_closed_IS = rps(reference_model=closed_IS,
                                  sensitiveItemsets=sensitive_IS,
                                  supportThreshold=self.min_support)

        # Get a sanitised database of itemsets using sanitised closed itemsets
        sanitised_DB = itemsets_from_closed_itemsets(closed_itemsets=sanitized_closed_IS,
                                                     possible_itemsets=self.original_DB['itemsets'])

        # All itemsets in original database
        a = set(self.original_DB["itemsets"])

        # All itemsets in sanitised database
        b = set(sanitised_DB["itemsets"])

        # Find sensitive in original database
        c = set(self.original_DB["itemsets"]).intersection(set(sensitive_IS))

        sef = side_effects_factor(a, b, c)
        self.assertEqual(0.0, sef)


if __name__ == '__main__':
    unittest.main()
