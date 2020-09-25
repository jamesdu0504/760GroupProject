#from arm_utilities import get_closed_itemsets
from mlxtend.frequent_patterns import fpgrowth
import pandas as pd

import datasets.import_datasets as im

threshold = 0.3

data = im.import_dataset("toydata")
itemsets = fpgrowth(data, min_support=threshold, use_colnames=True)

P = set()
for _, row in itemsets.iterrows():
    if len(row["itemsets"]) == 1:
        if row["support"] > threshold:
            P.add(row["itemsets"])

print(P)