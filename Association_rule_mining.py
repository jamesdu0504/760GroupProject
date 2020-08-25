#Following this tutorial: https://pbpython.com/market-basket-analysis.html
import pandas as pd
from mlxtend.frequent_patterns import apriori, fpgrowth
from mlxtend.frequent_patterns import association_rules

from arm_utilities import get_closed_itemsets, itemsets_from_closed_itemsets
import datasets.import_datasets as im

from algorithms.rps import rps
from algorithms.rps_two_thresholds import rps_two_thresholds
import time


"""
datasets that work:
- Belgian_retail
- uci_retail
- chess (Apriori runs out of memory with low support) (try 0.9x)
- connect (Apriori runs out of memory with low support) (try 0.9x)
- mushroom
- pumsb (Apriori runs out of memory with low support) (try 0.9x)
- pumsb_star
- T40I10D100K (Very sparse, use low support)
- T10I4D100K (Very sparse, use low support)
- accidents
- instacart
- BMS1
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
    power_set_of_items = fpgrowth(basket_sets, min_support=(1/len(basket_sets)), use_colnames=True)

    # Find frequent itemsets above support threshold min_support
    frequent_itemsets = fpgrowth(basket_sets, min_support=min_support, use_colnames=True)

    # Compute closed itemsets from database
    closed_itemsets = get_closed_itemsets(basket_sets)

    # Recover the original itemsets from the list of closed itemsets
    recovered_itemsets = itemsets_from_closed_itemsets(closed_itemsets=closed_itemsets,
                                                       possible_itemsets=power_set_of_items['itemsets'])
    
    assert recovered_itemsets.equals(power_set_of_items)

    # Sanitize database
    sanitized_closed_itemsets = rps(model=closed_itemsets,
                                    sensitiveItemsets={frozenset(['1','2']), frozenset(['4'])},
                                    supportThreshold=0.3)
    sanitized_database = itemsets_from_closed_itemsets(closed_itemsets=sanitized_closed_itemsets,
                                                       possible_itemsets=power_set_of_items['itemsets'])

    print('Raw Database:')
    print(power_set_of_items)
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