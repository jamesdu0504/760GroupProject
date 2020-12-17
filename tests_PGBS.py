import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import fpgrowth
from mlxtend.frequent_patterns import association_rules
import time
import copy

from metrics.misses_cost import misses_cost
from metrics.hiding_failure import hiding_failure
from metrics.artifactual_patterns import artifactual_patterns
from metrics.side_effects_factor import side_effects_factor
from metrics.information_loss import information_loss
from metrics.expected_information_loss import expected_information_loss

from support_distribution_graph import dual_support_graph_distribution

from charm_algorithm import get_closed_itemsets_Charm as get_closed_itemsets
from arm_utilities import itemsets_from_closed_itemsets
import datasets.import_datasets as im

from algorithms.pgbs import pgbs

#Hard coding dictionary of datasets to test "Dataset name" : [model threshold, support thresholds...]
# datasets = {"BMS1":[0.00085, 0.001, 0.002],
#             "BMS2":[0.0005, 0.001, 0.0015],
#             "connect":[ 0.8, 0.85, 0.9],
#             "chess":[0.7, 0.75, 0.8],
#             "Belgian_retail":[0.0005, 0.001, 0.0015],
#             "T40I10D100K":[0.011, 0.015, 0.02],
#             "T10I4D100K":[0.001, 0.0015, 0.002],
#             "mushroom":[0.1, 0.2, 0.3]}

datasets = {"Belgian_retail":[0.0005, 0.001, 0.0015]}

def count_FI_containing_S(freqIS, sensIS):
    #Should find the number of frequent itemsets that contain a sensitive itemset
    count = 0
    for _, row in freqIS.iterrows():
        for s in sensIS:
            if s.issubset(row["itemsets"]):
                count += 1
                break
    return count

def convert_to_sets(sensitive):
    for i in range(len(sensitive)):
        sensitive[i] = set(sensitive[i])
    return sensitive

def get_sensitive_subsets(original, sensitive):
    row_mask = []
    for i, row in original.iterrows():
        for s in sensitive:
            if s.issubset(row["itemsets"]):
                row_mask += [i]
                break
    return original.loc[set(row_mask)]

def remove_sensitive_subsets(original, sensitive):
    row_mask = []
    for i, row in original.iterrows():
        for s in sensitive:
            if s.issubset(row["itemsets"]):
                row_mask += [i]
                break
    return original.loc[set(original.index) - set(row_mask)]

def get_top_k_sensitive_itemsets(freqIS, num_sensIS):
    #Should return the sensitive itemsets
    sensitive_itemsets = []
    
    #Sort first
    freqIS = freqIS.sort_values(by='support', ascending=False)

    for _, row in freqIS.iterrows():
        if len(row["itemsets"]) >= 2:
            sensitive_itemsets.append(list(row["itemsets"]))
        if len(sensitive_itemsets) == num_sensIS:
            break
    return sensitive_itemsets

def main(datasets):
    #Create the base of a table
    table_11 = pd.DataFrame(columns=['Model',
                                     'Support threshold',
                                     'Model threshold',
                                     'Sensitive itemsets',
                                     'Number of FI before sanitization',
                                     'Information loss expected',
                                     'Number of FI after sanitization',
                                     'Number of FI containing an element of S after RPS',
                                     'Hiding failure',
                                     'Artifactual patterns',
                                     'Misses cost',
                                     'Side effects factor',
                                     'Information loss',
                                     'PGBS time'])

    #Loop through datasets
    for dataset in datasets:
        sigma_model = datasets[dataset][0]

        #Load dataset
        data = im.import_dataset(dataset)
        data = data.astype('bool') #This may be needed for some datasets
        print("\n", dataset, "imported\n")

        #Get frequent itemsets
        freq_model = fpgrowth(data, min_support=sigma_model, use_colnames=True) 

        #Loop through support thresholds
        for sigma_min in datasets[dataset][1:]:
            print("\n", dataset, "FI:", sigma_min)
            
            #Find original frequent itemsets at frequency sigma min
            freq_original = freq_model.loc[freq_model["support"] >= sigma_min]

            for k_freq in [10, 30, 50]:
                print("-", dataset, ":", k_freq, "Sensitive itemsets")

                #Copy the transactions so we can edit it directly
                copied_data = data.copy()
                
                #We pick sensitive itemsets here
                sensitive_IS = get_top_k_sensitive_itemsets(freq_original, k_freq)

                #Start timer for PGBS portion
                total_time_start = time.time()

                #Convert to pandas format for PGBS input
                sensitive_IS_pandas = pd.DataFrame(data=[(sensitive_IS), np.full((len(sensitive_IS)), sigma_min)]).T

                sensitive_IS_pandas.columns = ['itemset', 'threshold']

                #Run PGBS
                print("Running PGBS")
                pgbs(copied_data,sensitive_IS_pandas)
                print("PGBS run")
                pgbs_time = time.time()

                sensitive_IS = convert_to_sets(sensitive_IS)
                
                print("FPGrowth")
                #Reproduce frequent itemsets
                freq_model_sanitized = fpgrowth(copied_data, min_support=sigma_model, use_colnames=True)
                
                #Calculating metrics
                #Variables needed
                freq_sanitized = freq_model_sanitized.loc[freq_model_sanitized["support"] >= sigma_min]

                #Sensitive subsets of frequent itemsets
                freq_sanitized_sensitive = get_sensitive_subsets(freq_sanitized, sensitive_IS)
                freq_original_sensitive = get_sensitive_subsets(freq_original, sensitive_IS)

                #Non sensitive subset of frequent itemsets
                freq_sanitized_nonsensitive = remove_sensitive_subsets(freq_sanitized, sensitive_IS)["itemsets"]
                freq_original_nonsensitive = remove_sensitive_subsets(freq_original, sensitive_IS)["itemsets"]

                #Calculation of metrics
                freq_original_sensitive.to_csv("original.csv")
                freq_sanitized_sensitive.to_csv("sanitized.csv")
                print("len:", len(freq_original_sensitive["itemsets"]), len(freq_sanitized_sensitive["itemsets"]))

                hiding_f = hiding_failure(freq_original_sensitive["itemsets"], freq_sanitized_sensitive["itemsets"])
                artifactual_p = artifactual_patterns(set(freq_original["itemsets"]), set(freq_sanitized["itemsets"]))
                misses_c = misses_cost(freq_original_nonsensitive.copy(), freq_sanitized_nonsensitive.copy())
                side_effect_fac = side_effects_factor(set(freq_original["itemsets"]), set(freq_sanitized["itemsets"]), set(freq_original_sensitive["itemsets"]))

                #Information loss between frequent itemsets in original and sanitized at sigma model
                information_l = information_loss(freq_model.copy(), freq_model_sanitized)

                #Expected information loss if all sensitive frequent itemsets had their support reduced to sigma min
                expected_information_l = expected_information_loss(freq_model.copy(), freq_original_sensitive.copy(), sigma_min)

                #Calculate the end time of this iteration
                end_time = pgbs_time - total_time_start

                #Threshold sanitized database by threshold_min to get frequent itemsets 
                print(f'- PGBS time: {end_time}')

                #Plot support graphs
                dual_support_graph_distribution(freq_model, freq_model_sanitized, sigma_model, dataset+"_PGBS_"+str(sigma_min)+"_"+str(k_freq))

                #Find number of FI in sanitized database containing sensitive itemsets
                num_FI_containing_S_RPS = count_FI_containing_S(freq_sanitized, sensitive_IS)

                #Add to row of table
                new_row = {'Model': dataset,
                           'Model threshold': sigma_model,
                           'Support threshold': sigma_min,
                           'Sensitive itemsets': k_freq,
                           'Number of FI before sanitization': len(freq_original),
                           'Information loss expected': expected_information_l,
                           'Number of FI after sanitization': len(freq_sanitized),
                           'Number of FI containing an element of S after RPS': num_FI_containing_S_RPS,
                           'Hiding failure': hiding_f,
                           'Artifactual patterns': artifactual_p,
                           'Misses cost': misses_c,
                           'Side effects factor': side_effect_fac,
                           'Information loss': information_l,
                           'PGBS time': end_time}

                #Update after each one just so we are sure we are recording results
                table_11 = table_11.append(new_row, ignore_index=True)
                table_11.to_csv('table_pgbs.csv')

main(datasets)