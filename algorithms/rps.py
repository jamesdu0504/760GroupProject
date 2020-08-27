def recursiveHiding(itemset, support, sensitiveItemset, sortedSensitiveItemsets, model):
    '''
    itemset (set)
    support (float) support of itemset
    sensitiveItemset (set) the sensitive itemset which is a subset of itemset and must be removed
    model (dictionary) where keys are closed itemsets and values is the corresponding support
    sensitiveItemsets (set) a set of sensitive itemset
    '''
    
    for item in sensitiveItemset:           
        newItemSet=set(itemset)
        newItemSet.remove(item)        
                                        
        noSubsets=True
        for sensitiveItemset in sortedSensitiveItemsets: 
            if len(sensitiveItemset)>len(newItemSet):               #shortcut
                break
            if sensitiveItemset.issubset(newItemSet):
                recursiveHiding(newItemSet, support, sensitiveItemset, sortedSensitiveItemsets, model)
                noSubsets = False

        if noSubsets:
            if frozenset(newItemSet) not in model:
                model[frozenset(newItemSet)] = support



def rps(model, sensitiveItemsets, supportThreshold):
    '''
    model (dictionary) where keys are closed itemsets and values is the corresponding support
    sensitiveItemsets (set) a set of sensitive itemsets
    supportThreshold (float) minimum support threshold for hiding rules
    '''

    sortedSensitiveItemsets= sorted(sensitiveItemsets, key=lambda x: len(x))
    sortedClosedItemsets = sorted(model.keys(), key=lambda x: len(x))
    minSizeSensitiveItemset =len(sortedSensitiveItemsets[0])

    for itemset in sortedClosedItemsets:
        if len(itemset) >= minSizeSensitiveItemset:
            support = model[itemset]
            if support >= supportThreshold:
                for sensitiveItemset in sortedSensitiveItemsets:
                    if sensitiveItemset.issubset(itemset):
                        recursiveHiding(itemset, model[itemset], sensitiveItemset, sortedSensitiveItemsets, model)
                        del model[itemset]
                        break

    return model


#example

# model = {frozenset([2]): 1.0,
#          frozenset([2, 3]): 0.6,
#          frozenset([2, 4]): 0.7,
#          frozenset([2, 5]): 0.9,
#          frozenset([2, 3, 4]): 0.3,
#          frozenset([2, 3, 5]): 0.5,
#          frozenset([1, 2, 5]): 0.8,
#          frozenset([1, 2, 3, 5]): 0.6,
#          frozenset([1, 2, 4, 5]): 0.6,
#          frozenset([1, 2, 3, 4, 5]): 0.2,
#          }

# sensitiveItemsets = {
#     frozenset([4]),
#     frozenset([1, 2]),
# }

# supportThreshold = 0.3

# print(rps(model, sensitiveItemsets, supportThreshold))