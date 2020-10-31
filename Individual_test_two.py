import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import fpgrowth
from mlxtend.frequent_patterns import association_rules

from charm_algorithm import get_closed_itemsets_Charm as get_closed_itemsets
from algorithms.rps_two_thresholds import rps_two_thresholds
import datasets.import_datasets as im
from arm_utilities import itemsets_from_closed_itemsets
from support_distribution_graph import dual_support_graph_distribution
from metrics.information_loss import information_loss

'''
This runs an individual run to get a distribution graph
'''

def get_top_k_sensitive_itemsets(freqIS, num_sensIS):
    #Should return the sensitive itemsets
    sensitive_itemsets = set()
    
    #Sort first
    freqIS = freqIS.sort_values(by='support', ascending=False)

    for _, row in freqIS.iterrows():
        if len(row["itemsets"]) >= 2:
            sensitive_itemsets.add(row["itemsets"])
        if len(sensitive_itemsets) == num_sensIS:
            break
    return sensitive_itemsets

def main(datasets):
    for dataset in datasets:
        sigma_model = datasets[dataset][0]
        sigma_min = datasets[dataset][1]
        k_freq = 30
        #Load dataset
        data = im.import_dataset(dataset)
        data = data.astype('bool') #This may be needed for some datasets
        print("\n", dataset, "imported\n")

        #Convert to closed itemsets
        current_model, freq_model = get_closed_itemsets(data, sigma_model)
        freq_original = freq_model.loc[freq_model["support"] >= sigma_min]
        sensitive_IS = get_top_k_sensitive_itemsets(freq_original, k_freq)

        for k in range(0, 30):
            copied_model = current_model.copy()
            sigma_lower = 0.85 - k*0.005

            #Convert to pandas format for MRPS input
            sensitive_IS_pandas = pd.DataFrame(data=[(sensitive_IS), 
                                                        np.full((len(sensitive_IS)), sigma_min), 
                                                        np.full((len(sensitive_IS)), sigma_lower)]).T

            sensitive_IS_pandas.columns = ['itemset', 'upper_threshold', 'lower_threshold']

            #Run RPS random threshold
            sanitized_closed_IS = rps_two_thresholds(model=copied_model, 
                                                    sensitiveItemsets=sensitive_IS_pandas)

            #Reproduce frequent itemsets
            sanitized_DB = itemsets_from_closed_itemsets(closed_itemsets=sanitized_closed_IS,
                                                        possible_itemsets=freq_model['itemsets'])

            #Plot support graphs
            #dual_support_graph_distribution(freq_model, sanitized_DB, sigma_model, dataset+"_presentation_"+str(sigma_lower)+"_"+str(k_freq))
            
            information_l = information_loss(freq_model.copy(), sanitized_DB)
            print(sigma_lower, ",", information_l)

datasets = {"chess":[0.7, 0.85]}
main(datasets)