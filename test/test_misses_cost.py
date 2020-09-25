import unittest
from mlxtend.frequent_patterns import fpgrowth

from metrics.misses_cost import misses_cost
from arm_utilities import get_closed_itemsets, itemsets_from_closed_itemsets
import datasets.import_datasets as im

from algorithms.rps import rps


class TestMissesCost(unittest.TestCase):

    power_set_of_items = None
    non_frequent_IS = None
    closed_IS = None

    # Runs once before Class setup
    @classmethod
    def setUpClass(cls):
        min_support = 0.3  # Support threshold used

        # Get toy daya, WARNING! Had to change relative reference for this to work
        basket_sets = im.import_dataset("toydata")

        # Gather all itemsets
        cls.power_set_of_items = fpgrowth(basket_sets, min_support=(1 / len(basket_sets)), use_colnames=True, verbose=False)

        # # Find non_frequent itemsets
        cls.non_frequent_IS = set(cls.power_set_of_items[cls.power_set_of_items["support"] < 0.3]["itemsets"])

        # Compute closed itemsets from database for use in RPS
        cls.closed_IS, itemsets = get_closed_itemsets(basket_sets, 1 / len(basket_sets))

    def test_misses_cost_with_rps(self):

        # Get sanitised closed itemset from RPS
        sanitized_closed_IS = rps(reference_model=self.closed_IS,
                                        sensitiveItemsets={frozenset(['1', '2']), frozenset(['4'])},
                                        supportThreshold=0.3)

        # Get a sanitised database of itemsets using sanitised closed itemsets
        sanitized_DB = itemsets_from_closed_itemsets(closed_itemsets=sanitized_closed_IS,
                                                     possible_itemsets=self.power_set_of_items['itemsets'])

        sanitized_non_freq_IS = sanitized_DB.loc[sanitized_DB["support"] < 0.3]

        # Must pass non-sensitive itemsets
        mc = misses_cost(self.non_frequent_IS, sanitized_non_freq_IS)

        self.assertEqual(mc, 0.0)


if __name__ == '__main__':
    unittest.main()
