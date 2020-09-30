import pandas as pd
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
from statistical_measures import IL, IL_expected

from algorithms.rps import rps

#Hard coding dictionary of datasets to test "Dataset name" : [model threshold, support thresholds...]
datasets = {"BMS1":[0.00085, 0.001, 0.002],
            "BMS2":[0.0005, 0.001, 0.0015],
            "mushroom":[0.1, 0.2, 0.3],
            "connect":[ 0.8, 0.85, 0.9],
            "chess":[0.7, 0.75, 0.8],
            "Belgian_retail":[0.0005, 0.001, 0.0015],
            "T40I10D100K":[0.011, 0.015, 0.02],
            "T10I4D100K":[0.001, 0.0015, 0.002]}

def count_FI_containing_S(freqIS, sensIS):
    #Should find the number of frequent itemsets that contain a sensitive itemset
    count = 0
    for _, row in freqIS.iterrows():
        for s in sensIS:
            if s.issubset(row["itemsets"]):
                count += 1
                break

    return count

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
    #Create the base of a table
    table_11 = pd.DataFrame(columns=['Model',
                                     'Support threshold',
                                     'Model threshold',
                                     'Sensitive itemsets',
                                     'Number of FI before sanitization',
                                     'Number of FI containing an element of S before sanitization',
                                     'Number of FI after sanitization',
                                     'Number of FI containing an element of S after RPS',
                                     'Hiding failure',
                                     'Artifactual patterns',
                                     'Misses cost',
                                     'Side effects factor',
                                     'Information loss',
                                     'Information loss expected',
                                     'RPS Time'])

    table_10 = pd.DataFrame(columns=['Dataset',
                                     'Model threshold',
                                     'Number of Closed frequent itemsets',
                                     'Number of frequent itemsets',
                                     'Time closed itemsets'])

    #Loop through datasets
    for dataset in datasets:
        sigma_model = datasets[dataset][0]

        #Load dataset
        data = im.import_dataset(dataset)
        data = data.astype('bool') #This may be needed for some datasets
        print("\n", dataset, "imported\n")

        #Start total timer
        total_time_start = time.time()

        #Convert to closed itemsets
        current_model, freq_model = get_closed_itemsets(data, sigma_model)

        new_row = {'Dataset': dataset,
                   'Model threshold': sigma_model,
                   'Number of Closed frequent itemsets': len(current_model),
                   'Number of frequent itemsets': len(freq_model),
                   'Time closed itemsets': time.time()-total_time_start}
                   
        print(new_row)
        table_10 = table_10.append(new_row, ignore_index=True)
        table_10.to_csv('table_10.csv')

        #Loop through support thresholds
        for sigma_min in datasets[dataset][1:]:
            print("\n", dataset, "FI:", sigma_min)
            
            #Find original frequent itemsets at frequency sigma min
            freq_original = freq_model.loc[freq_model["support"] >= sigma_min]

            for k_freq in [10, 30, 50]:
                #Copy the model so we can edit it directly
                copied_model = copy.deepcopy(current_model)

                print("-", dataset, ":", k_freq, "Sensitive itemsets")
                
                #We pick sensitive itemsets here
                sensitive_IS = get_top_k_sensitive_itemsets(freq_original, k_freq)
                num_FI_containing_S = count_FI_containing_S(freq_original, sensitive_IS)

                #Start timer for RPS portion
                total_time_start = time.time()

                #Run RPS
                sanitized_closed_IS = rps(model=copied_model, 
                                          sensitiveItemsets=sensitive_IS, 
                                          supportThreshold=sigma_min)

                #Reproduce frequent itemsets
                sanitized_DB = itemsets_from_closed_itemsets(closed_itemsets=sanitized_closed_IS,
                                                             possible_itemsets=freq_model['itemsets'])

                rps_time = time.time()

                #Calculating metrics
                #Variables needed
                freq_sanitized = sanitized_DB.loc[sanitized_DB["support"] >= sigma_min]

                freq_sanitized_sensitive = get_sensitive_subsets(freq_sanitized, sensitive_IS)
                freq_original_sensitive = get_sensitive_subsets(freq_original, sensitive_IS)

                freq_sanitized_nonsensitive = remove_sensitive_subsets(freq_sanitized, sensitive_IS)["itemsets"]
                freq_original_nonsensitive = remove_sensitive_subsets(freq_original, sensitive_IS)["itemsets"]

                #Calculation of metrics
                hiding_f = hiding_failure(freq_original_sensitive["itemsets"], freq_sanitized_sensitive["itemsets"])
                artifactual_p = artifactual_patterns(set(freq_original["itemsets"]), set(freq_sanitized["itemsets"]))
                misses_c = misses_cost(freq_original_nonsensitive, freq_sanitized_nonsensitive)
                side_effect_fac = side_effects_factor(set(freq_original["itemsets"]), set(freq_sanitized["itemsets"]), set(freq_original_sensitive["itemsets"]))

                information_l = information_loss(freq_original.copy(), freq_sanitized)
                expected_information_l = expected_information_loss(freq_original.copy(), freq_original_sensitive.copy(), sigma_min)

                #Calculate the end time of this iteration
                end_time = rps_time - total_time_start

                #Threshold sanitized database by threshold_min to get frequent itemsets 
                print(f'- RPS time: {end_time}')

                #Plot support graphs
                dual_support_graph_distribution(freq_model, sanitized_DB, sigma_model, dataset+"_"+str(sigma_min)+"_"+str(k_freq))

                #Find number of FI in sanitized database containing sensitive itemsets
                num_FI_containing_S_RPS = count_FI_containing_S(freq_sanitized, sensitive_IS)

                #Add to row of table
                new_row = {'Model': dataset,
                           'Model threshold': sigma_model,
                           'Support threshold': sigma_min,
                           'Sensitive itemsets': k_freq,
                           'Number of FI before sanitization': len(freq_original),
                           'Number of FI containing an element of S before sanitization': num_FI_containing_S,
                           'Number of FI after sanitization': len(freq_sanitized),
                           'Number of FI containing an element of S after RPS': num_FI_containing_S_RPS,
                           'Hiding failure': hiding_f,
                           'Artifactual patterns': artifactual_p,
                           'Misses cost': misses_c,
                           'Side effects factor': side_effect_fac,
                           'Information loss': information_l,
                           'Information loss expected': expected_information_l,
                           'RPS Time': end_time}

                #Update after each one just so we are sure we are recording results
                table_11 = table_11.append(new_row, ignore_index=True)
                table_11.to_csv('table_11.csv')

main(datasets)