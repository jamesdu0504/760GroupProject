import unittest

import sys
sys.path.insert(1, '../')

from mlxtend.frequent_patterns import fpgrowth
from metrics.hiding_failure import hiding_failure
from arm_utilities import get_closed_itemsets, itemsets_from_closed_itemsets
import datasets.import_datasets as im
from algorithms.rps import rps
from algorithms.pgbs import pgbs

import pandas as pd

def get_sensitive_subsets(original, sensitive):
    row_mask = []
    for i, row in original.iterrows():
        for s in sensitive:
            if s.issubset(row["itemsets"]):
                row_mask += [i]
                break
    return original.loc[set(row_mask)]


class TestHidingFailure(unittest.TestCase):

    basket_sets = None
    original_IS = None
    original_Closed_IS = None

    # Want to hide the sensitive itemsets below this threshold
    sigma_min = 0.3

    @classmethod
    def setUpClass(cls):

        # Get toy data, WARNING! Had to change relative reference for this to work
        cls.basket_sets = im.import_dataset("toydata")

        # Abuse FPGrowth using absolute smallest min support to get all itemsets as frequent itemsets
        sigma_model = 1 / len(cls.basket_sets)
        cls.original_IS = fpgrowth(cls.basket_sets, min_support=sigma_model, use_colnames=True, verbose=False)

        # Compute closed itemsets of original data base
        cls.original_Closed_IS, _ = get_closed_itemsets(cls.basket_sets, sigma_model)

    def test_hiding_failure_with_rps(self):

        # Sensitive closed itemsets whose support needs to be reduced
        sensitive_IS = {frozenset(['1', '2']), frozenset(['4'])}

        # Produce a sanitised DB with sensitive IS's support below sigma_min
        sanitized_closed_IS = rps(model=self.original_Closed_IS,
                                  sensitiveItemsets=sensitive_IS,
                                  supportThreshold=self.sigma_min)

        # Convert from closed to frequent itemsets
        sanitised_F_IS = itemsets_from_closed_itemsets(closed_itemsets=sanitized_closed_IS,
                                                       possible_itemsets=self.original_IS['itemsets'])

        # Old working to look back on
        # # Find sensitive itemsets in original database
        # a = set(self.original_IS["itemsets"]).intersection(set(sensitive_IS))
        #
        # # Find sensitive itemsets in sanitised database
        # b = set(sanitised_F_IS["itemsets"]).intersection(set(sensitive_IS))

        # Find set of frequent itemsets in D
        a = get_sensitive_subsets(self.original_IS.loc[self.original_IS["support"] > self.sigma_min], sensitive_IS)["itemsets"]

        # Find set of frequent itemsets in D'
        b = get_sensitive_subsets(sanitised_F_IS.loc[sanitised_F_IS["support"] > self.sigma_min], sensitive_IS)["itemsets"]

        hf = hiding_failure(a, b)
        self.assertEqual(0.0, hf)


    def test_hiding_failure_with_pgbs(self):

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

        # Give all itemsets and supports in D (original_database)
        sigma_model = 1 / len(original_database)
        original_IS = fpgrowth(original_database, min_support=sigma_model, use_colnames=True, verbose=False)

        # Give all itemsets and supports in D' (modified_database)
        mofidied_F_IS = fpgrowth(modified_database, min_support=sigma_model, use_colnames=True, verbose=False)

        # Find set of frequent itemsets in D
        a = get_sensitive_subsets(original_IS.loc[original_IS["support"] > self.sigma_min], sensitive_IS)["itemsets"]

        # Find set of frequent itemsets in D'
        b = get_sensitive_subsets(mofidied_F_IS.loc[mofidied_F_IS["support"] > self.sigma_min], sensitive_IS)["itemsets"]

        hf = hiding_failure(a, b)
        self.assertEqual(0.0, hf)

if __name__ == '__main__':
    unittest.main()
