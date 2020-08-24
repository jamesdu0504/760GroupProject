import datasets.import_datasets as im
import pandas as pd
import seaborn as sns
import matplotlib.pylab as plt
from mlxtend.frequent_patterns import apriori, fpgrowth
from mlxtend.frequent_patterns import association_rules

#This creates a support graph for each dataset
#Plot between frequent itemsets > 0 and frequent itemsets < 50,000
#Very slow code, wouldn't suggest trying it

datasets = ["BMS1", 
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
            "instacart"]

def main(dataset):
    y = []
    x = []

    print("Processing:", dataset)
    basket_sets = im.import_dataset(dataset) 
    for min_support in range(200, 0, -1):
        frequent_itemsets = fpgrowth(basket_sets, min_support=0.005*min_support, use_colnames=True)
        if len(frequent_itemsets)>50000:
            break
        if len(frequent_itemsets) != 0:
            if len(x) == 0:
                x += [0.005*(min_support+1)]
                y += [0]
            y += [len(frequent_itemsets)]
            x += [0.005*min_support]

    plt.title("Number of Frequent Itemsets for Varying Levels of \nSupport for the " + dataset + " Dataset.")
    plt.plot(x, y, label='test_label1', color="turquoise")
    plt.ylabel("Number of frequent itemsets")
    plt.xlabel("Support threshold")
    plt.fill_between(x, y, color="paleturquoise")
    plt.savefig("supports/"+dataset+".png")
    plt.close()

for dataset in datasets:
    main(dataset)