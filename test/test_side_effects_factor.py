import unittest

from mlxtend.frequent_patterns import fpgrowth
from metrics.side_effects_factor import side_effects_factor
from arm_utilities import get_closed_itemsets, itemsets_from_closed_itemsets
import datasets.import_datasets as im
from algorithms.rps import rps

class TestSideEffectsFactor(unittest.TestCase):

    original_IS = None
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

    def test_side_effects_factor_with_rps(self):

        # Sensitive closed itemsets whose support needs to be reduced
        sensitive_IS = {frozenset(['1', '2']), frozenset(['4'])}

        # Produce a sanitised DB with sensitive IS's support below sigma_min
        sanitized_closed_IS = rps(reference_model=self.original_Closed_IS,
                                  sensitiveItemsets=sensitive_IS,
                                  supportThreshold=self.sigma_min)

        # Convert from closed to frequent itemsets
        sanitised_F_IS = itemsets_from_closed_itemsets(closed_itemsets=sanitized_closed_IS,
                                                       possible_itemsets=self.original_IS['itemsets'])

        # All frequent itemsets in original database D
        a = set(self.original_IS["itemsets"])

        # All frequent itemsets in sanitised database D'
        b = set(sanitised_F_IS["itemsets"])

        # Find sensitive in original database D'
        c = set(self.original_IS["itemsets"]).intersection(set(sensitive_IS))

        sef = side_effects_factor(a, b, c)
        self.assertEqual(0.0, sef)


if __name__ == '__main__':
    unittest.main()