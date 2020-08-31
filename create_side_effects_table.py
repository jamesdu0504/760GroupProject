import pandas as pd
from mlxtend.frequent_patterns import fpgrowth
from mlxtend.frequent_patterns import association_rules

from arm_utilities import get_closed_itemsets, itemsets_from_closed_itemsets
import datasets.import_datasets as im
from statistical_measures import IL, IL_expected

from algorithms.rps import rps

#Hard coding dictionary of datasets to test "Dataset name" : [model threshold, support thresholds...]
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
                                     'Number of FI containing an element of S after PGBS',
                                     'Errors'])

    table_10 = pd.DataFrame(columns=['Dataset',
                                     'Model threshold',
                                     'Number of Closed frequent itemsets',
                                     'Number of frequent itemsets'])
    #Loop through datasets
    for dataset in datasets:
        sigma_model = datasets[dataset][0]

        #Load dataset
        data = im.import_dataset(dataset)
        data = data.astype('bool') #This may be needed for some datasets
        print(dataset, "imported")
        current_model, freq_IS_in_model_df = get_closed_itemsets(data, sigma_model)

        # Testing if expected information loss being calculated from closed itemsets


        new_row = {'Dataset': dataset,
                   'Model threshold': sigma_model,
                   'Number of Closed frequent itemsets': len(current_model),
                   'Number of frequent itemsets': len(freq_IS_in_model_df)}
        print(new_row)
        table_10 = table_10.append(new_row, ignore_index=True)

        #Loop through support thresholds
        for sigma_min in datasets[dataset][1:]:
            print(dataset, "FI", sigma_min)
            freq_IS_above_sigma_min_df = freq_IS_in_model_df.loc[freq_IS_in_model_df["support"] >= sigma_min]

            for k_freq in [10, 30, 50]:
                print(dataset, k_freq, "sensitive itemsets")

                sensitive_IS = get_top_k_sensitive_itemsets(freq_IS_above_sigma_min_df, k_freq)
                
                num_FI_containing_S = count_FI_containing_S(freq_IS_above_sigma_min_df, sensitive_IS)

                sanitized_closed_IS= rps(reference_model=current_model,
                                            sensitiveItemsets=sensitive_IS,
                                            supportThreshold=sigma_min)


                sanitized_DB = itemsets_from_closed_itemsets(closed_itemsets=sanitized_closed_IS,
                                                             possible_itemsets=freq_IS_in_model_df['itemsets'])

                #Threshold sanitized database by threshold_min to get frequent itemsets 
                sanitized_freq_IS_sigma_min_df = sanitized_DB.loc[sanitized_DB["support"] >= sigma_min]


                #Find number of FI in sanitized database containing sensitive itemsets
                num_FI_containing_S_RPS = count_FI_containing_S(sanitized_freq_IS_sigma_min_df, sensitive_IS)

                print(IL_expected(freq_IS_in_model_df, sigma_min))
                print(IL(freq_IS_in_model_df, sanitized_DB))


                #Add to row of table @Need to implement PGBS

                new_row = {'Model': dataset,
                           'Model threshold': sigma_model,
                           'Support threshold': sigma_min,
                           'Sensitive itemsets': k_freq,
                           'Number of FI before sanitization':len(freq_IS_above_sigma_min_df),
                           'Number of FI containing an element of S before sanitization': num_FI_containing_S,
                           'Number of FI after sanitization':len(sanitized_freq_IS_sigma_min_df),
                           'Number of FI containing an element of S after RPS': num_FI_containing_S_RPS,
                           'Errors': len(sanitized_freq_IS_sigma_min_df)-(len(freq_IS_above_sigma_min_df)-num_FI_containing_S)}

                print(new_row)
                table_11 = table_11.append(new_row, ignore_index=True)

    table_11.to_csv('table_11.csv')
    table_10.to_csv('table_10.csv')

main(datasets)