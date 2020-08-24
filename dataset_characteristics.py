import datasets.import_datasets as im
import pandas as pd

#Takes a very long time to run, probably not worth running when the output 

datasets = ["BMS1", 
            "BMS2", 
            "toydata"
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

def main(datasets):
    df = pd.DataFrame(columns=['Dataset Name',
                               'Number of transactions',
                               'Number of Unique items',
                               'Minimum Transaction Length',
                               'Maximum Transaction Length',
                               'Average Transaction Length'])

    for dataset_name in datasets:
        print("Analysing", dataset_name)
        data = im.import_dataset(dataset_name)
        
        data = data.astype('bool')

        average = 0
        minimum = 100000
        maximum = 0
        for _, row in data.iterrows():
            transaction_len = sum(row)
            #Minimum transaction length
            if minimum > transaction_len:
                minimum = transaction_len

            #Maximum transaction length
            if maximum < transaction_len:
                maximum = transaction_len
                
            #Average transaction length
            average += transaction_len

        new_row = {'Dataset Name':dataset_name,
                   'Number of transactions':data.shape[0],
                   'Number of Unique items':data.shape[1],
                   'Minimum Transaction Length':minimum,
                   'Maximum Transaction Length':maximum,
                   'Average Transaction Length':average/data.shape[0]
                   }

        df = df.append(new_row, ignore_index=True)

    print(df)
    return df

main(datasets).to_csv('Dataset_details.csv')