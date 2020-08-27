import pandas as pd
from mlxtend.frequent_patterns import apriori, fpgrowth
from mlxtend.frequent_patterns import association_rules

from arm_utilities import get_closed_itemsets, itemsets_from_closed_itemsets
import datasets.import_datasets as im

from algorithms.rps import rps

"""
Needs a bit of work still
To find parts that need work: ctrl-f @ 
"""

#Hard coding dictionary of datasets to test "Dataset name" : [model threshold, support thresholds...]
datasets = {"mushroom": [0.1, 0.2, 0.3],
            "connect":[ 0.8, 0.85, 0.9],
            "chess":[0.7, 0.75, 0.8],
            "Belgian_retail":[0.0005, 0.001, 0.0015],
            "BMS1":[0.00085, 0.001, 0.002],
            "BMS2":[0.0005, 0.001, 0.0015]}


def number_frequent_containing_s(frequent, s):
    #Should find the number of frequent itemsets that contain a sensitive itemset
    #@Not sure how to do this
    #I think we loop through frequent
    pass

def get_sensitive_itemsets(FI, s):
    #Should return the sensitive itemsets
    sensitve_itemsets = set()

    #@Trying to test this
    for _, row in FI.iterrows():
        if len(row["itemsets"]) > 1:
            print(row["itemsets"])
            sensitve_itemsets.add(row["itemsets"])

    return sensitve_itemsets


def main(datasets):
    #Create the base of a table
    df = pd.DataFrame(columns=['Model',
                               'Support threshold',
                               'Model threshold',
                               'Sensitive itemsets',
                               'Before FI',
                               'Before S itemsets',
                               'After RPS S itemsets',
                               'After PGBS S itemsets'])

    #Loop through datasets
    for dataset in datasets:
        threshold_model = datasets[dataset][0]

        #Load dataset
        data = im.import_dataset(dataset)
        data = data.astype('bool') #This may be needed for some datasets
        closed_itemsets = get_closed_itemsets(data)

        # Gather all itemsets @Needs to be more efficient
        # power_set_of_items = fpgrowth(data, min_support=threshold_model, use_colnames=True)

        #Loop through support thresholds
        for threshold_min in datasets[dataset][1:]:
            print("Finding FI")
            #Find frequent itemsets @Does this use the correct threshold?
            frequent_itemsets = fpgrowth(data, min_support=threshold_model, use_colnames=True)
            
            #Loop through number of sensitive itemsets
            for sens_itemsets in [10, 30, 50]:
                
                #Get sensitive itemsets
                sensitiveItemsets = get_sensitive_itemsets(frequent_itemsets, sens_itemsets)

                #Find number of FI containing sensitive itemsets
                num_FI_containing_s = number_frequent_containing_s(frequent_itemsets, sensitiveItemsets)

                #Find number of FI containing sensitive itemsets after sanitization
                sanitized_closed_itemsets = rps(model=closed_itemsets,
                                    sensitiveItemsets=sensitiveItemsets,
                                    supportThreshold=threshold_min)
                sanitized_database = itemsets_from_closed_itemsets(closed_itemsets=sanitized_closed_itemsets, possible_itemsets=frequent_itemsets['itemsets'])

                #Find number of FI in sanitized database containing sensitive itemsets
                num_FI_containing_s_RPS = number_frequent_containing_s(sanitized_database, sensitiveItemsets)

                #Add to row of table @Need to implement PGBS
                new_row = {'Model': dataset,
                           'Model threshold': threshold_model,
                           'Support Threshold': threshold_min,
                           'Sensitive Itemsets': sens_itemsets,
                           'Before FI':len(frequent_itemsets),
                           'Before S itemsets': num_FI_containing_s,
                           'After RPS S itemsets': num_FI_containing_s_RPS,
                           'After PGBS S itemsets': 0
                        }
                df = df.append(new_row, ignore_index=True)
    return df

main(datasets).to_csv('side_effects_table.csv')