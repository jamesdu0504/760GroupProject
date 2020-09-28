#from arm_utilities import get_closed_itemsets
from mlxtend.frequent_patterns import fpgrowth
import pandas as pd

import datasets.import_datasets as im
from arm_utilities import get_closed_itemsets
from charm_algorithm import get_closed_itemsets_new
from charm_2 import charm

def main(dataset_name, threshold):
    data = im.import_dataset(dataset_name)

    # CI_n = get_closed_itemsets_new(data, threshold)[0]
    CI_n = charm(data, threshold)
    print(CI_n.keys())
    CI_o = get_closed_itemsets(data, threshold)[0]

    same = []
    have = []
    missing = []
    for CI in CI_o:
        if CI in CI_n:
            same += [CI]
        else:
            missing += [CI]

    for CI in CI_n:
        if not CI in CI_o:
            have += [CI]
    
    print("Similar closed:", len(same))
    print("Need to remove:", len(have))
    print("Need to add to:", len(missing))


datasets = {"BMS1":[0.00085, 0.001, 0.002],
    "BMS2":[0.0005, 0.001, 0.0015],
    "Belgian_retail":[0.0005, 0.001, 0.0015],
    "mushroom":[0.1, 0.2, 0.3],
    "connect":[ 0.8, 0.85, 0.9],
    "chess":[0.7, 0.75, 0.8]}

# for dataset, v in datasets.items():
#     print(dataset, v[0])
#     main(dataset, v[0])

main('chess', 0.7)
# main('toydata', 0.0001)

"""
Should have:
{frozenset({'2'}): 1.0, 
frozenset({'2', '5'}): 0.9, 
frozenset({'2', '1', '5'}): 0.8, 
frozenset({'2', '3'}): 0.6, 
frozenset({'2', '4'}): 0.7, 
frozenset({'2', '1', '5', '4'}): 0.6, 
frozenset({'2', '3', '5'}): 0.5, 
frozenset({'2', '3', '1', '5'}): 0.4, 
frozenset({'2', '3', '4'}): 0.3}

Have:
frozenset({'2', '5', '4'}): 0.6, 
frozenset({'1', '2'}): 0.8, 

frozenset({'3', '2'}): 0.6, 
frozenset({'2', '4'}): 0.7, 
frozenset({'5', '1', '2', '4'}): 0.6,
frozenset({'2', '3', '5'}): 0.5, 
{frozenset({'5', '1', '3', '2'}): 0.4, 
frozenset({'2', '5'}): 0.9, 
frozenset({'2'}): 1.0}
"""