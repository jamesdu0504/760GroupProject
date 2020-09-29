import unittest

import sys
sys.path.insert(1, '../')

from mlxtend.frequent_patterns import fpgrowth
from metrics.information_loss import information_loss
from arm_utilities import get_closed_itemsets, itemsets_from_closed_itemsets
import datasets.import_datasets as im
from algorithms.rps import rps

class TestMissesCost(unittest.TestCase):

    original_IS = None
    original_NFreq_IS = None
    original_Freq_IS = None
    original_Closed_IS = None

    # Want to hide the sensitive itemsets below this threshold
    sigma_min = 0.3

    @classmethod
    def setUpClass(cls):

        # Get toy data, WARNING! Had to change relative reference for this to work
        basket_sets = im.import_dataset("toydata")

        # Abuse FPGrowth using absolute smallest min support to get all itemsets as frequent itemsets
        sigma_model = 1 / len(basket_sets)
        cls.original_IS = fpgrowth(basket_sets, min_support=sigma_model, use_colnames=True, verbose=False)

        # Compute closed itemsets of original data base
        cls.original_Closed_IS, _ = get_closed_itemsets(basket_sets, sigma_model)

        # Get non-frequent itemsets
        cls.original_NFreq_IS = cls.original_IS[cls.original_IS["support"] < cls.sigma_min]

        # Get frequent itemsets
        cls.original_Freq_IS = cls.original_IS[cls.original_IS["support"] >= cls.sigma_min]

    def test_misses_cost_with_rps(self):

        # Sensitive closed itemsets whose support needs to be reduced
        sensitive_IS = {frozenset(['1', '2']), frozenset(['4'])}

        # Produce a sanitised DB with sensitive IS's support below sigma_min
        sanitized_closed_IS = rps(reference_model=self.original_Closed_IS,
                                  sensitiveItemsets=sensitive_IS,
                                  supportThreshold=self.sigma_min)

        # Convert from closed to frequent itemsets
        sanitised_F_IS = itemsets_from_closed_itemsets(closed_itemsets=sanitized_closed_IS,
                                                       possible_itemsets=self.original_IS['itemsets'])

        # Give all itemsets and supports in D
        a = self.original_Freq_IS           #We want frequent itemsets only

        # Give all itemsets and supports in D'
        b = sanitised_F_IS

        il = information_loss(a, b)
        self.assertEqual(0.3377, round(il,4)) #Using expected IL found in excel


if __name__ == '__main__':
    unittest.main()
