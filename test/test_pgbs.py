import unittest
import pandas as pd

import datasets.import_datasets as im
from mlxtend.frequent_patterns import fpgrowth
from algorithms.pgbs import pgbs
from metrics.information_loss import information_loss


class TestMissesCost(unittest.TestCase):

    def test_pgbs(self):

        basket_sets = im.import_dataset("chess").sample(100) # limit due to testing

        original_database = basket_sets.copy()
        modified_database = basket_sets.copy()

        # We partition the Chess databases into 5 bins, then randomly select 2 itemsets from each bin,
        # assign the minimum support threshold as the minimum support given in the support range
        # This takes a long time, so will just use their values. Table 3: Support ranges for databases.
        sigma_min = min([0.6001, 0.6136, 0.6308, 0.6555, 0.6974])

        sigma_model = 0.5
        original_IS = fpgrowth(original_database, min_support=sigma_model, use_colnames=True)

        # Get 10 sensitive itemsets
        sensitive_IS = original_IS.sample(10)
        sensitive_IS_PGBS = pd.DataFrame({
            'itemset': [list(IS) for IS in sensitive_IS["itemsets"]],
            'threshold': [sigma_min for _ in sensitive_IS["support"]]})

        pgbs(modified_database, sensitive_IS_PGBS)

        # Give all itemsets and supports in D (original_database)
        a = original_IS

        # Give all itemsets and supports in D' (modified_database)
        b = fpgrowth(modified_database, min_support=sigma_model, use_colnames=True)

        il = information_loss(a, b)
        self.assertEqual(0.5542, round(il, 4))


if __name__ == '__main__':
    unittest.main()

