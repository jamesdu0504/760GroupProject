import pandas as pd
from mlxtend.frequent_patterns import apriori, fpgrowth
from mlxtend.frequent_patterns import association_rules

from arm_utilities import get_closed_itemsets, itemsets_from_closed_itemsets
import datasets.import_datasets as im

from algorithms.rps import rps

"""
Needs a bit of work still
To find parts that need work: ctrl-f @ 
"mushroom": [0.1, 0.2, 0.3],
            "chess":[0.7, 0.75, 0.8],
            "connect":[ 0.8, 0.85, 0.9],
            "BMS1":[0.00085, 0.001, 0.002],
            "BMS2":[0.0005, 0.001, 0.0015]
            
"""

#Hard coding dictionary of datasets to test "Dataset name" : [model threshold, support thresholds...]
datasets = {"Belgian_retail":[0.0005, 0.001, 0.0015]}


def number_frequent_containing_s(frequent, sensitive):
    #Should find the number of frequent itemsets that contain a sensitive itemset
    #@Needs testing
    count = 0
    for _, row in frequent.iterrows():
        for s in sensitive:
            if s.issubset(row["itemsets"]):
                count += 1
                break

    return count

def get_sensitive_itemsets(FI, s):
    #Should return the sensitive itemsets
    sensitive_itemsets = set()

    #Sort first
    FI = FI.sort_values(by=['support'], ascending=False)
    count = 0

    #Loop through finding s highest support sets
    for _, row in FI.iterrows():
        if len(row["itemsets"]) >= 2:
            sensitive_itemsets.add(row["itemsets"])
            count += 1
        if count == s:
            break
    return sensitive_itemsets


def main(datasets):
    #Create the base of a table
    table_11 = pd.DataFrame(columns=['Model',
                               'Support threshold',
                               'Model threshold',
                               'Sensitive itemsets',
                               'Before FI',
                               'Before S itemsets',
                               'After RPS itemsets',
                               'After PGBS itemsets'])

    table_10 = pd.DataFrame(columns=['Dataset',
                                     'Model threshold',
                                     'Number of Closed frequent itemsets',
                                     'Number of frequent itemsets'])

    #Loop through datasets
    for dataset in datasets:
        threshold_model = datasets[dataset][0]

        #Load dataset
        data = im.import_dataset(dataset)
        data = data.astype('bool') #This may be needed for some datasets
        print(dataset, "imported")
        closed_itemsets, fi_model = get_closed_itemsets(data, threshold_model) #0.0005

        new_row = {'Dataset': dataset,
                   'Model threshold': threshold_model,
                   'Number of Closed frequent itemsets': len(closed_itemsets),
                   'Number of frequent itemsets': len(fi_model)}
        table_10 = table_10.append(new_row, ignore_index=True)

        #Loop through support thresholds
        for threshold_min in datasets[dataset][1:]:
            print(dataset, "FI", threshold_min)

            #Find frequent itemsets @Threshold fi_model with threshold_min
            frequent_itemsets = fpgrowth(data, min_support=threshold_min, use_colnames=True) #0.001, 0.0015

            #Loop through number of sensitive itemsets
            for sens_itemsets in [10, 30, 50]:
                print(dataset, sens_itemsets, "sensitive itemsets")
                
                ##### ALL ABOVE HERE WORKS



                #Get sensitive itemsets
                sensitiveItemsets = get_sensitive_itemsets(frequent_itemsets, sens_itemsets)

                #Find number of FI containing sensitive itemsets
                num_FI_containing_s = number_frequent_containing_s(frequent_itemsets, sensitiveItemsets)

                #Find number of FI containing sensitive itemsets after sanitization
                sanitized_closed_itemsets = rps(model=closed_itemsets,
                                                sensitiveItemsets=sensitiveItemsets,
                                                supportThreshold=threshold_min)
                sanitized_database = itemsets_from_closed_itemsets(closed_itemsets=sanitized_closed_itemsets, possible_itemsets=fi_model['itemsets'])



                ##### ALL BELOW HERE WORKS

                #Threshold sanitized database by threshold_min to get frequent itemsets 
                new_fi = sanitized_database.loc[sanitized_database["support"]>= threshold_min]

                #Find number of FI in sanitized database containing sensitive itemsets 
                num_FI_containing_s_RPS = number_frequent_containing_s(sanitized_database, sensitiveItemsets) 
                print(num_FI_containing_s_RPS)

                #Add to row of table @Need to implement PGBS
                new_row = {'Model': dataset,
                           'Model threshold': threshold_model,
                           'Support threshold': threshold_min,
                           'Sensitive itemsets': sens_itemsets,
                           'Before FI':len(frequent_itemsets),
                           'Before S itemsets': num_FI_containing_s,
                           'After RPS itemsets': len(new_fi), #Need to calculate 
                           'After PGBS itemsets': 0
                        }
                print(new_row)
                table_11 = table_11.append(new_row, ignore_index=True)

    table_11.to_csv('table_11.csv')
    table_10.to_csv('table_10.csv')

main(datasets)