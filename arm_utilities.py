from mlxtend.frequent_patterns import fpgrowth
import pandas as pd

import time


def get_closed_itemsets(baskets, threshold):
    print('========== Collecting Closed Itemsets ==========')
    # Each itemset has minimum possible support 'threshold', assuming it appears in the database
    print(f'Finding all frequent itemsets with support above: {threshold}')
    start_time = time.time()
    itemsets = fpgrowth(baskets, min_support=threshold, use_colnames=True)
    print(f'Time to run fpgrowth with min_sup 0: {time.time() - start_time}')

    su = itemsets.support.unique()

    fredic = {}
    for i in range(len(su)):
        inset = list(itemsets.loc[itemsets.support == su[i]]['itemsets'])
        fredic[su[i]] = inset

    start_time = time.time()
    cl = []
    print(itemsets.shape)
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

    print("Stage 1 done", len(cl))
    closed_itemset_dict = dict()
    for c, s in cl:
        # c = frozenset([int(c_i) for c_i in c])
        closed_itemset_dict[c] = s

    print(f'Time to find closed itemsets: {time.time() - start_time}')
    print(f'{itemsets.shape[0]} itemsets reduced to {len(cl)} closed itemsets')
    print('================================================\n')
    return closed_itemset_dict


def itemsets_from_closed_itemsets(closed_itemsets, possible_itemsets):
    supports = []
    for itemset in possible_itemsets:
        max_supp = 0
        for closed_itemset, supp in closed_itemsets.items():
            # closed_itemset = frozenset([str(c_i) for c_i in closed_itemset])
            if itemset <= closed_itemset:
                max_supp = max(max_supp, supp)
        supports.append(max_supp)

    df = pd.DataFrame(data={'support': supports, 'itemsets': possible_itemsets})
    return df