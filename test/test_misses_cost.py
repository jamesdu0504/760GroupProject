import unittest

from mlxtend.frequent_patterns import fpgrowth
from metrics.misses_cost import misses_cost
from arm_utilities import get_closed_itemsets, itemsets_from_closed_itemsets
import datasets.import_datasets as im
from algorithms.rps import rps


class TestMissesCost(unittest.TestCase):

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

    def test_misses_cost_with_rps(self):
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

        # Find non-sensitive in original database
        a = set(self.original_DB["itemsets"]).difference(set(sensitive_IS))

        # Find non-sensitive in sanitised database
        b = set(sanitised_DB["itemsets"]).difference(set(sensitive_IS))

        mc = misses_cost(a, b)
        self.assertEqual(mc, 0.0)


if __name__ == '__main__':
    unittest.main()
