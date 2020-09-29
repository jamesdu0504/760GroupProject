import unittest

from mlxtend.frequent_patterns import fpgrowth
from metrics.misses_cost import misses_cost
from arm_utilities import get_closed_itemsets, itemsets_from_closed_itemsets
import datasets.import_datasets as im
from algorithms.rps import rps


def remove_sensitive_subsets(original, sensitive):
    row_mask = []
    for i, row in original.iterrows():
        for s in sensitive:
            if s.issubset(row["itemsets"]):
                row_mask += [i]
                break
    return original[~original["itemsets"].isin(row_mask)]


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

        # Find set of non-sensitive frequent itemsets in D
        a = remove_sensitive_subsets(self.original_IS, sensitive_IS)

        # Find set of non-sensitive frequent itemsets in D'
        b = remove_sensitive_subsets(sanitised_F_IS, sensitive_IS)

        mc = misses_cost(a, b)
        self.assertEqual(mc, 0.0)


if __name__ == '__main__':
    unittest.main()
