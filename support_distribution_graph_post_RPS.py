import datasets.import_datasets as im
import pandas as pd
import seaborn as sns
import matplotlib.pylab as plt
from mlxtend.frequent_patterns import apriori, fpgrowth
from mlxtend.frequent_patterns import association_rules

from arm_utilities import get_closed_itemsets, itemsets_from_closed_itemsets
from algorithms.rps import rps
from algorithms.rps_two_thresholds import rps_two_thresholds

#This creates a support graph for each dataset
#Plot between frequent itemsets > 0 and frequent itemsets < 50,000
#Very slow code, wouldn't suggest trying it
"""
"BMS1", 
            "BMS2", 
            "toydata",
            "uci_retail",
            "mushroom",
            "Belgian_retail",
            "chess", 
            "connect", 
            "mushroom", 
            "pumsb", 
            "pumsb_star", 
            "T40I10D100K", 
            "T10I4D100K", 
            "accidents", 
            "instacart"
"""
datasets = ["toydata"]

def main(dataset):
    y = []
    x = []

    print("Processing:", dataset)
    basket_sets = im.import_dataset(dataset) 
    power_set_of_items = fpgrowth(basket_sets, min_support=(1/len(basket_sets)), use_colnames=True)

    for min_support in range(200, 0, -1):
        #Shhhhh don't tell Natasha
        frequent_itemsets = fpgrowth(basket_sets, min_support=0.005*min_support, use_colnames=True)

        if len(frequent_itemsets)>50000:
            break
        if len(frequent_itemsets) != 0:
            # Compute closed itemsets from database
            closed_itemsets, _ = get_closed_itemsets(basket_sets, 0.005*min_support)

            # Sanitize database
            sanitized_closed_itemsets = rps(model=closed_itemsets,
                                            sensitiveItemsets={frozenset(['1','2']), frozenset(['4'])},
                                            supportThreshold=0.005*min_support)
            sanitized = itemsets_from_closed_itemsets(closed_itemsets=sanitized_closed_itemsets,
                                                            possible_itemsets=power_set_of_items['itemsets'])
            sanitized = sanitized.loc[sanitized["support"] >= 0.005*min_support]
            if len(x) == 0:
                x += [0.005*(min_support+1)]
                y += [0]
            y += [len(sanitized)]
            x += [0.005*min_support]

    plt.title("Number of Frequent Itemsets for Varying Levels of \nSupport for the " + dataset + " Dataset.")
    plt.plot(x, y, label='test_label1', color="turquoise")
    plt.ylim(0,30)
    plt.ylabel("Number of frequent itemsets")
    plt.xlabel("Support threshold")
    plt.fill_between(x, y, color="paleturquoise")
    plt.savefig("supports/"+dataset+"2.png")
    plt.close()

for dataset in datasets:
    main(dataset)