#Following this tutorial: https://pbpython.com/market-basket-analysis.html
import pandas as pd
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules

# Each import function imports a dataset into the form of a matrix, each row is a transaction
# each column is a item

def import_uci_retail():
    #Retail dataset provided by UC Irvine
    #Uses full dataset
    df = pd.read_excel('./Datasets/Online Retail.xlsx')
    df['Description'] = df['Description'].str.strip()
    df.dropna(axis=0, subset=['InvoiceNo'], inplace=True)
    df['InvoiceNo'] = df['InvoiceNo'].astype('str')
    df = df[~df['InvoiceNo'].str.contains('C')]

    print("Checking input:", df.head())

    basket = (df.groupby(['InvoiceNo', 'Description'])['Quantity'].sum().unstack().reset_index().fillna(0).set_index('InvoiceNo'))

    basket_sets = basket.applymap(encode_units)
    basket_sets.drop('POSTAGE', inplace=True, axis=1)
    basket_sets.columns=basket_sets.columns.str.replace(' ','_')
    return basket_sets

def import_uci_retail_mini():
    #Retail dataset provided by UC Irvine
    #Subsection of this dataset with only transactions from France 
    df = pd.read_excel('./Datasets/Online Retail.xlsx')
    df['Description'] = df['Description'].str.strip()
    df.dropna(axis=0, subset=['InvoiceNo'], inplace=True)
    df['InvoiceNo'] = df['InvoiceNo'].astype('str')
    df = df[~df['InvoiceNo'].str.contains('C')]
    print(df.dtypes)
    print("Checking input:", df.head())
    print(df.head())
    basket = df[df.Country=='France'].groupby(['InvoiceNo', 'Description'])['Quantity'].sum().unstack().reset_index().fillna(0).set_index('InvoiceNo')
    print(df.head())
    basket_sets = basket.applymap(encode_units)
    basket_sets.drop('POSTAGE', inplace=True, axis=1)
    basket_sets.columns=basket_sets.columns.str.replace(' ','_')
    return basket_sets

def import_instacart():
    #Instacart retail dataset
    df = pd.read_csv('./Datasets/order_products__train.csv')
    df = df.drop(['add_to_cart_order', 'reordered'], axis=1)
    df['order_id'] = df['order_id'].astype('str')
    df['product_id'] = df['product_id'].astype('str')
    df['Quantity']=1
    print(df.dtypes)
    df = df.groupby(['order_id', 'product_id'])['Quantity'].sum()
    df = df.unstack().reset_index().fillna(0).set_index('order_id')
    print(df.head())

    print("Checking input:", basket)
    basket_sets = basket.applymap(encode_units)
    return basket_sets


def dataset(name):
    if name == "uci_retail":
        return import_uci_retail()
    elif name == "uci_retail_mini":
        return import_uci_retail_mini()
    elif name == "instacart":
        return import_instacart()

def encode_units(x):
    if x <= 0:
        return 0
    if x >= 1:
        return 1





def main():
    basket_sets = dataset("instacart")
    frequent_itemsets = apriori(basket_sets, min_support=0.1, use_colnames=True)
    print(frequent_itemsets)
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.75)
    print(rules[rules['confidence'] >= 0.2])

main()