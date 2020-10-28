import unittest

import sys
sys.path.insert(1, '../')

from mlxtend.frequent_patterns import fpgrowth
from metrics.expected_information_loss import expected_information_loss
from arm_utilities import get_closed_itemsets, itemsets_from_closed_itemsets
import datasets.import_datasets as im
from algorithms.rps import rps


def get_sensitive_subsets(original, sensitive):
    row_mask = []
    for i, row in original.iterrows():
        for s in sensitive:
            if s.issubset(row["itemsets"]):
                row_mask += [i]
                break
    return original.loc[set(row_mask)]


class TestExpectedInformationLoss(unittest.TestCase):

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

    def test_expected_information_loss_with_rps(self):

        sensitive_IS = {frozenset(['1', '2']), frozenset(['4'])}

        # Give all itemsets and supports in D
        a = self.original_IS

        b = get_sensitive_subsets(self.original_Freq_IS, sensitive_IS)

        eil = expected_information_loss(a, b, self.sigma_min)
        self.assertEqual(0.2289, round(eil,4))


if __name__ == '__main__':
    unittest.main()
