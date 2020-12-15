import datasets.import_datasets as im
import pandas as pd
import seaborn as sns
import matplotlib.pylab as plt
from mlxtend.frequent_patterns import apriori, fpgrowth
from mlxtend.frequent_patterns import association_rules

import random

def support_graph_distribution(frequent_itemsets, min_support, name):
    #Draw the frequent itemsets distribution
    # frequent_itemsets: original frequent itemsets mined with support > min_support
    # name: name of the dataset
    plt.title("Number of Frequent Itemsets for Varying Levels of \nSupport for the " + name + " Dataset.")
    plt.hist(frequent_itemsets['support'], 
             bins=300, 
             density=False, 
             histtype='bar', 
             cumulative=-1, 
             range=(max(min_support, 0), frequent_itemsets['support'].max()),
             color="dodgerblue")

    plt.ylabel("Number of frequent itemsets")
    plt.xlabel("Support threshold")
    plt.savefig("supports/"+name+".png")
    plt.close()


def dual_support_graph_distribution(frequent_itemsets_A, frequent_itemsets_B, min_support, name):
    #Draw the sanitized and unsanitized frequent itemsets distributions over each other
    # frequent_itemsets_A: original frequent itemsets mined with support > min_support
    # frequent_itemsets_B: sanitised frequent itemsets mined with support > min_support
    # name: name of the dataset

    plt.title("Number of Frequent Itemsets for Varying Levels of \nSupport for the original and sanitised " + name + " Dataset.")
    plt.hist(frequent_itemsets_A['support'], 
             bins=300, 
             density=False, 
             histtype='bar', 
             cumulative=-1, 
             range=(max(min_support, 0), frequent_itemsets_A['support'].max()),
             color="dodgerblue",
             label="Original")

    plt.hist(frequent_itemsets_B['support'], 
             bins=300, 
             density=False, 
             histtype='bar', 
             cumulative=-1, 
             range=(max(min_support, 0), frequent_itemsets_B['support'].max()),
             color="yellow",
             alpha=0.8,
             label="Sanitised")

    plt.legend()

    plt.ylabel("Number of frequent itemsets")
    plt.xlabel("Support threshold")
    plt.savefig("supports/"+name+"_dual.png")
    plt.close()

def main(dataset, min_sup):
    #Manually assigning minimum supports
    datasets = {"toydata": 0.005,
                "BMS1": 0.00085, 
                "BMS2": 0.0005, 
                "uci_retail": 0.005,
                "mushroom": 0.1,
                "Belgian_retail": 0.0005,
                "chess": 0.7, 
                "connect": 0.8, 
                "pumsb": 0.83, 
                "pumsb_star": 0.38, 
                "T40I10D100K": 0.011, 
                "T10I4D100K": 0.001, 
                "accidents": 0.38, 
                "instacart": 0.005}

    for key, value in datasets.items():
        main(key, value)

    print("Processing:", dataset)
    basket_sets = im.import_dataset(dataset)
    
    #Plot the support distribution
    frequent_itemsets = fpgrowth(basket_sets, min_support=min_sup, use_colnames=True)
    support_graph_distribution(frequent_itemsets, min_sup, dataset)

    #Example of plotting the dual distributions
    # #Plot the dual distribution by randomly reducing some values for testing
    # copy = frequent_itemsets.copy()
    # copy.dropna(inplace=True) #This is needed for some reason?
    # for i in range(copy.shape[0]//2):
    #     copy.loc[random.randint(0, copy.shape[0]), ["support"]] = copy.loc[random.randint(0, copy.shape[0]-1), ["support"]]/2

    # dual_support_graph_distribution(frequent_itemsets, copy, min_sup, dataset)

