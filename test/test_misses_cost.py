import unittest

import sys
sys.path.insert(1, '../')

from mlxtend.frequent_patterns import fpgrowth
from metrics.misses_cost import misses_cost
from arm_utilities import get_closed_itemsets, itemsets_from_closed_itemsets
import datasets.import_datasets as im
from algorithms.rps import rps
import pandas as pd
from algorithms.pgbs import pgbs



def remove_sensitive_subsets(original, sensitive):
    row_mask = []
    for i, row in original.iterrows():
        for s in sensitive:
            if s.issubset(row["itemsets"]):
                row_mask += [i]
                break
    return original.loc[set(original.index) - set(row_mask)]


class TestMissesCost(unittest.TestCase):

    original_IS = None
    original_NFreq_IS = None
    original_Freq_IS = None
    original_Closed_IS = None

    # Want to hide the sensitive itemsets below this threshold
    sigma_min = 0.3

    # Sensitive closed itemsets whose support needs to be reduced
    sensitive_IS = {frozenset(['1', '2']), frozenset(['4'])}

    # Get toy data, WARNING! Had to change relative reference for this to work
    basket_sets = im.import_dataset("toydata")

    @classmethod
    def setUpClass(cls):

        # Abuse FPGrowth using absolute smallest min support to get all itemsets as frequent itemsets
        sigma_model = 1 / len(cls.basket_sets)
        cls.original_IS = fpgrowth(cls.basket_sets, min_support=sigma_model, use_colnames=True, verbose=False)

        # Compute closed itemsets of original data base
        cls.original_Closed_IS, _ = get_closed_itemsets(cls.basket_sets, sigma_model)

        # Get non-frequent itemsets
        cls.original_NFreq_IS = cls.original_IS[cls.original_IS["support"] < cls.sigma_min]

        # Get frequent itemsets
        cls.original_Freq_IS = cls.original_IS[cls.original_IS["support"] >= cls.sigma_min]

    def test_misses_cost_with_rps(self):

        # Produce a sanitised DB with sensitive IS's support below sigma_min
        sanitized_closed_IS = rps(model=self.original_Closed_IS,
                                  sensitiveItemsets=self.sensitive_IS,
                                  supportThreshold=self.sigma_min)

        # Convert from closed to frequent itemsets
        sanitised_F_IS = itemsets_from_closed_itemsets(closed_itemsets=sanitized_closed_IS,
                                                       possible_itemsets=self.original_IS['itemsets'])

        # Find set of non-sensitive frequent itemsets in D
        a = remove_sensitive_subsets(self.original_Freq_IS, self.sensitive_IS)

        # Find set of non-sensitive frequent itemsets in D'
        b = remove_sensitive_subsets(sanitised_F_IS[sanitised_F_IS["support"] >= self.sigma_min], self.sensitive_IS)

        mc = misses_cost(a, b)
        self.assertEqual(mc, 0.0)

    def test_misses_cost_with_pgbs(self):

        # Sensitive closed itemsets whose support needs to be reduced
        sensitive_IS = {frozenset(['1', '2']), frozenset(['4'])}

        # PGBS needs input in this format
        sensitive_IL = pd.DataFrame(
            {'itemset': [list(l) for l in sensitive_IS],
             'threshold': [self.sigma_min, self.sigma_min]})

        original_database = self.basket_sets.copy()
        modified_database = self.basket_sets.copy()

        # No return value, instead it modifies input database in place
        pgbs(modified_database, sensitive_IL)

        # Get all itemsets and supports in D (original_database)
        sigma_model = 1 / len(original_database)
        original_IS = fpgrowth(original_database, min_support=sigma_model, use_colnames=True, verbose=False)

        # Get all itemsets and supports in D' (modified_database)
        mofidied_F_IS = fpgrowth(modified_database, min_support=sigma_model, use_colnames=True, verbose=False)

        # Find set of non-sensitive frequent itemsets in D
        a = remove_sensitive_subsets(original_IS, self.sensitive_IS)

        # Find set of non-sensitive frequent itemsets in D'
        b = remove_sensitive_subsets(mofidied_F_IS[mofidied_F_IS["support"] >= self.sigma_min], self.sensitive_IS)

        mc = misses_cost(a, b)
        self.assertEqual(mc, 0.18181818181818182)

if __name__ == '__main__':
    unittest.main()
