import unittest

import sys
sys.path.insert(1, '../')

from mlxtend.frequent_patterns import fpgrowth
from metrics.artifactual_patterns import artifactual_patterns
from arm_utilities import get_closed_itemsets, itemsets_from_closed_itemsets
import datasets.import_datasets as im
from algorithms.rps import rps
from algorithms.pgbs import pgbs
import pandas as pd


class TestArtifactualPatterns(unittest.TestCase):

    original_IS = None
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

        # Get frequent itemsets
        cls.original_Freq_IS = cls.original_IS[cls.original_IS["support"] >= cls.sigma_min]

    def test_artifactual_patterns_with_rps(self):

        # Produce a sanitised DB with sensitive IS's support below sigma_min
        sanitized_closed_IS = rps(model=self.original_Closed_IS,
                                  sensitiveItemsets=self.sensitive_IS,
                                  supportThreshold=self.sigma_min)

        # Convert from closed to frequent itemsets
        sanitised_F_IS = itemsets_from_closed_itemsets(closed_itemsets=sanitized_closed_IS,
                                                       possible_itemsets=self.original_IS['itemsets'])

        # All itemsets in original database
        a = set(self.original_Freq_IS["itemsets"])

        # All itemsets in sanitised database
        b = set(sanitised_F_IS[sanitised_F_IS["support"] >= self.sigma_min]["itemsets"])

        af = artifactual_patterns(a, b)
        self.assertEqual(af, 0.0)

    def test_artifactual_patterns_with_pgbs(self):

        # PGBS needs input in this format
        sensitive_IL = pd.DataFrame(
            {'itemset': [list(l) for l in self.sensitive_IS],
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

        # All itemsets in original database
        a = set(original_IS["itemsets"])

        # All itemsets in sanitised database
        b = set(mofidied_F_IS["itemsets"])

        af = artifactual_patterns(a, b)
        self.assertEqual(af, 0.0)


if __name__ == '__main__':
    unittest.main()
