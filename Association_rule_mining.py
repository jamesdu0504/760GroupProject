#Following this tutorial: https://pbpython.com/market-basket-analysis.html
import pandas as pd
from mlxtend.frequent_patterns import apriori, fpgrowth
from mlxtend.frequent_patterns import association_rules

import datasets.import_datasets as im

from algorithms.rps import rps
import time

def get_closed_itemsets(baskets):
    print('========== Collecting Closed Itemsets ==========')
    # Each itemset has minimum possible support 1/number of baskets, assuming it appears in the database
    print(f'Finding all frequent itemsets with support above: {1/baskets.shape[0]}')
    start_time = time.time()
    itemsets = fpgrowth(baskets, min_support=(1/baskets.shape[0]), use_colnames=True)
    print(f'Time to run fpgrowth with min_sup 0: {time.time() - start_time}')

    su = itemsets.support.unique()

    fredic = {}
    for i in range(len(su)):
        inset = list(itemsets.loc[itemsets.support == su[i]]['itemsets'])
        fredic[su[i]] = inset

    start_time = time.time()
    cl = []
    for index, row in itemsets.iterrows():
        isclose = True
        cli = row['itemsets']
        cls = row['support']
        checkset = fredic[cls]
        for i in checkset:
            if (cli != i):
                if (frozenset.issubset(cli, i)):
                    isclose = False
                    break

        if isclose:
            cl.append((row['itemsets'], row['support']))

    closed_itemset_dict = dict()
    for c, s in cl:
        # c = frozenset([int(c_i) for c_i in c])
        closed_itemset_dict[c] = s

    print(f'Time to find closed itemsets: {time.time() - start_time}')
    print(f'{itemsets.shape[0]} itemsets reduced to {len(cl)} closed itemsets')
    print('================================================\n')
    return closed_itemset_dict


def itemsets_from_closed_itemsets(closed_itemsets, itemsets):
    supports = []
    for itemset in itemsets:
        max_supp = 0
        for closed_itemset, supp in closed_itemsets.items():
            # closed_itemset = frozenset([str(c_i) for c_i in closed_itemset])
            if itemset <= closed_itemset:
                max_supp = max(max_supp, supp)
        supports.append(max_supp)

    df = pd.DataFrame(data={'support': supports, 'itemsets': itemsets})
    return df


"""
Datasets that work:
- Belgian_retail
- uci_retail
- uci_retail_mini
- chess (Apriori runs out of memory with low support) (try 0.9x)
- connect (Apriori runs out of memory with low support) (try 0.9x)
- mushroom
- pumsb (Apriori runs out of memory with low support) (try 0.9x)
- pumsb_star
- T40I10D100K (Very sparse, use low support)
- T10I4D100K (Very sparse, use low support)
- accidents
- instacart
- BMS1_spmf
- BMS2
- toydata (The toy dataset)
"""

def main():
    min_support = 0.01      #Support threshold used
    min_confidence = 0.05   #Confidence threshold used

    print('========== Importing Dataset ==========')
    basket_sets = im.import_dataset("toydata") #Insert any of the datasets listed above here to import them
    print('=======================================\n')

    # Gather all itemsets
    itemsets = fpgrowth(basket_sets, min_support=(1/len(basket_sets)), use_colnames=True)

    # Find frequent itemsets above support threshold min_support
    frequent_itemsets = fpgrowth(basket_sets, min_support=min_support, use_colnames=True)

    # Compute closed itemsets from database
    closed_itemsets = get_closed_itemsets(basket_sets)

    # Recover the original itemsets from the list of closed itemsets
    recovered_itemsets = itemsets_from_closed_itemsets(closed_itemsets=closed_itemsets,
                                                       itemsets=frequent_itemsets['itemsets'])
    assert recovered_itemsets.equals(itemsets)

    # Sanitize database
    sanitized_closed_itemsets = rps(model=closed_itemsets,
                                    sensitiveItemsets={frozenset(['1','2']), frozenset(['4'])},
                                    supportThreshold=0.3)
    sanitized_database = itemsets_from_closed_itemsets(closed_itemsets=sanitized_closed_itemsets,
                                                       itemsets=frequent_itemsets['itemsets'])

    print('Raw Database:')
    print(itemsets)
    print()
    print('Sanitized Database:')
    print(sanitized_database)
    print()
    print(f'Frequent Itemsets above min_sup {min_support}:')
    print(frequent_itemsets)
    print()

    # print(frequent_itemsets)
    if frequent_itemsets.shape[0]>0:
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
        if rules.shape[0] > 0:
            print(rules[rules['confidence'] >= 0.0])
        else:
            print("Confidence too low, no rules were found")
    else:
        print("Support too low, no frequent item sets found")

main()