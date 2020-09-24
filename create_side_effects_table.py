import pandas as pd
from mlxtend.frequent_patterns import fpgrowth
from mlxtend.frequent_patterns import association_rules
import time
import copy
import cProfile

from arm_utilities import get_closed_itemsets, itemsets_from_closed_itemsets
import datasets.import_datasets as im
from statistical_measures import IL, IL_expected

from algorithms.rps import rps

#Hard coding dictionary of datasets to test "Dataset name" : [model threshold, support thresholds...]
datasets = {"mushroom":[0.1, 0.2, 0.3],
            "connect":[ 0.8, 0.85, 0.9],
            "chess":[0.7, 0.75, 0.8],
            "BMS1":[0.00085, 0.001, 0.002],
            "BMS2":[0.0005, 0.001, 0.0015],
            "Belgian_retail":[0.0005, 0.001, 0.0015]}


def count_FI_containing_S(freqIS, sensIS):
    #Should find the number of frequent itemsets that contain a sensitive itemset
    count = 0
    for _, row in freqIS.iterrows():
        for s in sensIS:
            if s.issubset(row["itemsets"]):
                count += 1
                break

    return count

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
                                     'Errors',
                                     'Time'])

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
        print(dataset, "imported")

        #Start total timer
        total_time_start = time.time()

        #Convert to closed itemsets
        current_model, freq_IS_in_model_df = get_closed_itemsets(data, sigma_model)

        new_row = {'Dataset': dataset,
                   'Model threshold': sigma_model,
                   'Number of Closed frequent itemsets': len(current_model),
                   'Number of frequent itemsets': len(freq_IS_in_model_df),
                   'Time closed itemsets': time.time()-total_time_start}
        print(new_row)
        table_10 = table_10.append(new_row, ignore_index=True)

        #Loop through support thresholds
        for sigma_min in datasets[dataset][1:]:
            print(dataset, "FI", sigma_min)
            freq_IS_above_sigma_min_df = freq_IS_in_model_df.loc[freq_IS_in_model_df["support"] >= sigma_min]
            
            for k_freq in [10, 30, 50]:
                #Copy the model so we can edit it directly
                copied_model = copy.deepcopy(current_model)

                print(dataset, k_freq, "sensitive itemsets")
                
                #We pick sensitive itemsets here
                sensitive_IS = get_top_k_sensitive_itemsets(freq_IS_above_sigma_min_df, k_freq)
                num_FI_containing_S = count_FI_containing_S(freq_IS_above_sigma_min_df, sensitive_IS)

                #Start timer for RPS portion
                total_time_start = time.time()
                sanitized_closed_IS = rps(model=copied_model, 
                                          sensitiveItemsets=sensitive_IS, 
                                          supportThreshold=sigma_min)
                
                rps_time = time.time()
                # profile = cProfile.Profile()
                # profile.enable()
                sanitized_DB = itemsets_from_closed_itemsets(closed_itemsets=sanitized_closed_IS,
                                                             possible_itemsets=freq_IS_in_model_df['itemsets'])
                # profile.disable()
                # profile.print_stats()

                #Calculate the end time of this iteration
                end_time = time.time() - total_time_start

                #Threshold sanitized database by threshold_min to get frequent itemsets 
                sanitized_freq_IS_sigma_min_df = sanitized_DB.loc[sanitized_DB["support"] >= sigma_min]
                print(f'RPS time: {rps_time - total_time_start}')
                print(f'Itemsets from closed time: {end_time - rps_time}')

                #Find number of FI in sanitized database containing sensitive itemsets
                num_FI_containing_S_RPS = count_FI_containing_S(sanitized_freq_IS_sigma_min_df, sensitive_IS)

                #Add to row of table
                new_row = {'Model': dataset,
                           'Model threshold': sigma_model,
                           'Support threshold': sigma_min,
                           'Sensitive itemsets': k_freq,
                           'Number of FI before sanitization': len(freq_IS_above_sigma_min_df),
                           'Number of FI containing an element of S before sanitization': num_FI_containing_S,
                           'Number of FI after sanitization': len(sanitized_freq_IS_sigma_min_df),
                           'Number of FI containing an element of S after RPS': num_FI_containing_S_RPS,
                           'Side effects': len(sanitized_freq_IS_sigma_min_df)-(len(freq_IS_above_sigma_min_df)-num_FI_containing_S),
                           'Time': end_time}

                print(new_row)
                table_11 = table_11.append(new_row, ignore_index=True)

    table_11.to_csv('table_11.csv')
    table_10.to_csv('table_10.csv')

main(datasets)