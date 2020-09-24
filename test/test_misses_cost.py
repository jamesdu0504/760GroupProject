import unittest
from mlxtend.frequent_patterns import fpgrowth

from metrics.misses_cost import misses_cost
from arm_utilities import get_closed_itemsets, itemsets_from_closed_itemsets
import datasets.import_datasets as im

from algorithms.rps import rps


class TestMissesCost(unittest.TestCase):

    closed_itemsets = None
    power_set_of_items = None
    recovered_itemsets = None

    @classmethod
    def setUpClass(cls):
        min_support = 0.01  # Support threshold used

        # Insert any of the datasets listed above here to import them
        basket_sets = im.import_dataset("toydata")

        # Gather all itemsets
        cls.power_set_of_items = fpgrowth(basket_sets, min_support=(1 / len(basket_sets)), use_colnames=True, verbose=False)

        # Find frequent itemsets above support threshold min_support
        cls.frequent_itemsets = fpgrowth(basket_sets, min_support=min_support, use_colnames=True)

        # Compute closed itemsets from database
        cls.closed_itemsets, _ = get_closed_itemsets(basket_sets, 1 / len(basket_sets))

        # Recover the original itemsets from the list of closed itemsets
        cls.recovered_itemsets = itemsets_from_closed_itemsets(closed_itemsets=cls.closed_itemsets,
                                                           possible_itemsets=cls.power_set_of_items['itemsets'])

    def test_misses_cost_with_rps(self):
        sanitized_closed_itemsets = rps(reference_model=self.closed_itemsets,
                                        sensitiveItemsets={frozenset(['1', '2']), frozenset(['4'])},
                                        supportThreshold=0.3)

        sanitized_database = itemsets_from_closed_itemsets(closed_itemsets=sanitized_closed_itemsets,
                                                           possible_itemsets=self.power_set_of_items['itemsets'])

        # Must pass non-sensitive itemsets
        mc = misses_cost(self.frequent_itemsets, sanitized_database)

        self.assertEqual(mc, 0.0)


if __name__ == '__main__':
    unittest.main()
