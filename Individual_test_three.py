import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import fpgrowth
from mlxtend.frequent_patterns import association_rules

from charm_algorithm import get_closed_itemsets_Charm as get_closed_itemsets
import datasets.import_datasets as im
from arm_utilities import itemsets_from_closed_itemsets
from support_distribution_graph import dual_support_graph_distribution
from metrics.information_loss import information_loss

from algorithms.SWA import SWA
from algorithms.pgbs import pgbs
from algorithms.rps_two_thresholds import rps_two_thresholds

'''
This runs an experiment measuring info loss and generating a graph for multiple threshold algorithms
'''

def convert_to_sets(sensitive):
    for i in range(len(sensitive)):
        sensitive[i] = set(sensitive[i])
    return sensitive

def get_top_k_sensitive_itemsets(freqIS, num_sensIS):
    #Should return the sensitive itemsets
    sensitive_itemsets = []
    
    #Sort first
    freqIS = freqIS.sort_values(by='support', ascending=False)

    for _, row in freqIS.iterrows():
        if len(row["itemsets"]) >= 2:
            sensitive_itemsets.append(row["itemsets"])
        if len(sensitive_itemsets) == num_sensIS:
            break
    return sensitive_itemsets

def get_disclosures(sensitive_IS, freq_model, sigma_min):
    disclosures = dict()
    for i, itemset in enumerate(sensitive_IS):
        support = freq_model.loc[freq_model['itemsets'] == itemset, 'support'].item()
        threshold = sigma_min[i]/support
        if threshold < 1:
            disclosures[itemset] = threshold
    return disclosures

def main(datasets, experiment):
    for dataset in datasets:
        sigma_model = datasets[dataset][0]
        sigma_min = datasets[dataset][1]
        k_freq = 10
        #Load dataset
        data = im.import_dataset(dataset)
        data = data.astype('bool') #This may be needed for some datasets
        print("\n", dataset, "imported\n")

        #Convert to closed itemsets
        current_model, freq_model = get_closed_itemsets(data, sigma_model)
        freq_original = freq_model.loc[freq_model["support"] >= sigma_min]
        sensitive_IS = get_top_k_sensitive_itemsets(freq_original, k_freq)

        if experiment == "MuRPS-range":
            #Convert to pandas format for MRPS input
            sensitive_IS_pandas = pd.DataFrame(data=[(sensitive_IS), 
                                                    np.array([0.8, 0.79, 0.78, 0.77, 0.76, 0.75, 0.74, 0.73, 0.72, 0.71]), 
                                                    np.array([0.795, 0.785, 0.775, 0.765, 0.755, 0.745, 0.735, 0.725, 0.715, 0.705])]).T
        
        elif experiment == "MuRPS-set":
            #Convert to pandas format for MRPS input
            thresholds = [0.7975, 0.7875, 0.7775, 0.7675, 0.7575, 0.7475, 0.7375, 0.7275, 0.7175, 0.7075]
            sensitive_IS_pandas = pd.DataFrame(data=[(sensitive_IS), 
                                                    np.array(thresholds), 
                                                    np.array(thresholds)]).T

        elif experiment == "SWA-set":
            db = im.convert_to_transaction(data)
            thresholds = [0.7975, 0.7875, 0.7775, 0.7675, 0.7575, 0.7475, 0.7375, 0.7275, 0.7175, 0.7075]
            #Convert to pandas format for SWA input
            sensitive_rules = get_disclosures(sensitive_IS, freq_model, thresholds)
            print(sensitive_rules)
            
            #Run SWA
            SWA(db, sensitive_rules, db.shape[0])

            #Convert to frequent itemsets
            sensitive_IS = convert_to_sets(sensitive_IS)
            data = im.convert_to_matrix(db)
            freq_model_sanitized = fpgrowth(data, min_support=sigma_model, use_colnames=True)
            freq_sanitized = freq_model_sanitized.loc[freq_model_sanitized["support"] >= sigma_min]
        
        elif experiment == "PGBS-set":
            thresholds = [0.7975, 0.7875, 0.7775, 0.7675, 0.7575, 0.7475, 0.7375, 0.7275, 0.7175, 0.7075]
            sensitive_IS_pandas = pd.DataFrame(data=[(sensitive_IS), np.full((len(sensitive_IS)), thresholds)]).T

            sensitive_IS_pandas.columns = ['itemset', 'threshold']

            #Run PGBS
            pgbs(data,sensitive_IS_pandas)

            #Convert to frequent itemsets
            sensitive_IS = convert_to_sets(sensitive_IS)
            freq_model_sanitized = fpgrowth(data, min_support=sigma_model, use_colnames=True)
            freq_sanitized = freq_model_sanitized.loc[freq_model_sanitized["support"] >= sigma_min]

        if experiment[0] == "M":
            sensitive_IS_pandas.columns = ['itemset', 'upper_threshold', 'lower_threshold']
            print(sensitive_IS_pandas)

            #Run RPS random threshold
            sanitized_closed_IS = rps_two_thresholds(model=current_model, 
                                                    sensitiveItemsets=sensitive_IS_pandas)

            #Reproduce frequent itemsets
            freq_model_sanitized = itemsets_from_closed_itemsets(closed_itemsets=sanitized_closed_IS,
                                                        possible_itemsets=freq_model['itemsets'])

        #Plot support graphs
        dual_support_graph_distribution(freq_model, freq_model_sanitized, sigma_model, dataset+"_presentation_"+ experiment +"_"+str(k_freq))
        
        #Calculate and print information loss
        information_l = information_loss(freq_model.copy(), freq_model_sanitized)
        print("Information loss:", information_l)

datasets = {"chess":[0.7, 0.80]}

#MuRPS-Range
#MuRPS-set
#SWA-set
#PGBS-set
experiment = "PGBS-set" 
main(datasets, experiment)