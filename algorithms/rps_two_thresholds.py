import random 
import pandas as pd
import copy
from mlxtend.frequent_patterns import fpgrowth

import sys
sys.path.insert(0, '..')
import datasets.import_datasets as im
from charm_algorithm import get_closed_itemsets_Charm as get_closed_itemsets
from support_distribution_graph import dual_support_graph_distribution
from arm_utilities import itemsets_from_closed_itemsets

def recursiveHiding(itemset, support, sensitiveItemset, sortedSensitiveItemsets, model):
    '''
    itemset (set)
    support (float) support of itemset
    sensitiveItemset (set) the sensitive itemset which is a subset of itemset and must be removed
    sensitiveItemsets (set) a set of sensitive itemset
    model (dictionary) where keys are closed itemsets and values is the corresponding support
    '''
    sensitiveItemset = list(sensitiveItemset)
    random.shuffle(sensitiveItemset)        #the item picked should be picked randomally to ensure robustness
    for item in sensitiveItemset:           
        newItemSet=set(itemset)
        newItemSet.remove(item)        
                                        
        noSubsets=True
        for sensitiveItemset in sortedSensitiveItemsets: #can sort cut by only considering itemsets of the correct size
            if len(sensitiveItemset)>len(newItemSet):
                break
            if sensitiveItemset.issubset(newItemSet):
                recursiveHiding(newItemSet, support, sensitiveItemset, sortedSensitiveItemsets, model)
                noSubsets = False

        if noSubsets:
            if frozenset(newItemSet) not in model:
                model[frozenset(newItemSet)] = support



def rps_two_thresholds(model, sensitiveItemsets):
    '''
    model (dictionary) where keys are closed itemsets and values is the corresponding support
    sensitiveItemsets (pandas dataframe) each row is a sensitive itemset
        "itemset": the sensitive itemset
        "upper_threshold": the maximum value we want to hide below
        "lower_threshold": the minimum value we want to hide below
    '''
    #Sort rows by length of itemsets
    sortedSensitiveItemsets = sensitiveItemsets.reindex((sensitiveItemsets["itemset"].str.len()).argsort()).reset_index(drop=True)
    sortedClosedItemsets = sorted(model.keys(), key=lambda x: len(x)) 
    minSizeSensitiveItemset = len(sortedSensitiveItemsets.iloc[[0]])

    minSupport = min(sensitiveItemsets.lower_threshold)
    sensitiveItemsets = set(sortedSensitiveItemsets["itemset"])

    for itemset in sortedClosedItemsets:
        if len(itemset) >= minSizeSensitiveItemset:
            support = model[itemset]
            for sensitiveItemset in sortedSensitiveItemsets.iterrows():
                sigma = random.uniform(sensitiveItemset[1].lower_threshold, sensitiveItemset[1].upper_threshold)
                if support >= sigma:
                    if sensitiveItemset[1].itemset.issubset(itemset):
                        recursiveHiding(itemset, model[itemset], sensitiveItemset[1].itemset, sensitiveItemsets, model)
                        del model[itemset]
                        break
    return model


# def test_case(model, freq_model, sensitiveItemsets, i):
#     new_model = rps_two_thresholds(model.copy(), sensitiveItemsets)
#     freq = itemsets_from_closed_itemsets(closed_itemsets=new_model,
#                                          possible_itemsets=freq_model['itemsets'])
#     print("For test:", i)
#     print(freq)


# #Example
# data = im.import_dataset("toydata")
# model, freq_model = get_closed_itemsets(data, 0.0001)

# #Normal case - hide all below a fixed sigma min (0.3)
# sensitiveItemsets = pd.DataFrame(columns=['itemset', 'upper_threshold', 'lower_threshold'], 
#                                  data=[(frozenset(["4"]), 0.3, 0.3), (frozenset(["1", "2"]), 0.3, 0.3)])
# test_case(model, freq_model, sensitiveItemsets, 1)

# #Hiding randomly within a range 0.3 - 0.2
# sensitiveItemsets = pd.DataFrame(columns=['itemset', 'upper_threshold', 'lower_threshold'], 
#                                  data=[(frozenset(["4"]), 0.3, 0.2), (frozenset(["1", "2"]), 0.3, 0.2)])
# test_case(model, freq_model, sensitiveItemsets, 2)

# #Hiding below manually defined fixed thresholds
# sensitiveItemsets = pd.DataFrame(columns=['itemset', 'upper_threshold', 'lower_threshold'], 
#                                  data=[(frozenset(["4"]), 0.25, 0.25), (frozenset(["1", "2"]), 0.4, 0.4)])
# test_case(model, freq_model, sensitiveItemsets, 3)

# #Hiding randomly below manually defined thresholds 
# sensitiveItemsets = pd.DataFrame(columns=['itemset', 'upper_threshold', 'lower_threshold'], 
#                                  data=[(frozenset(["4"]), 0.25, 0.2), (frozenset(["1", "2"]), 0.3, 0.25)])
# test_case(model, freq_model, sensitiveItemsets, 4)