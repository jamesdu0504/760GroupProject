from mlxtend.preprocessing import TransactionEncoder
from sklearn.preprocessing import MultiLabelBinarizer
import pandas as pd

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
    grouped = df.groupby("order_id")
    df = grouped.aggregate(lambda x: list(x))

    mlb = MultiLabelBinarizer(sparse_output=True)
    df = df.join(pd.DataFrame.sparse.from_spmatrix(
            mlb.fit_transform(df.pop('product_id')),
                index=df.index, columns=mlb.classes_))

    return df

def import_BMS(filename):
    #This reads the files that come in the format of one line per transaction
    file_object  = open(filename, "r")
    transactions = []
    contents = file_object.readlines()
    for i in range(len(contents)):
        transactions.append(contents[i].rstrip(' -1 -2\n').split(" -1 "))
    file_object.close()
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions)
    basket_sets = pd.DataFrame(te_ary, columns=te.columns_)
    return basket_sets

def import_other(filename):
    #This reads the files that come in the format of one line per transaction
    file_object  = open(filename, "r")
    transactions = []
    contents = file_object.readlines()
    for i in range(len(contents)):
        transactions.append(contents[i].rstrip(' \n').split(" "))
    file_object.close()
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions)
    basket_sets = pd.DataFrame(te_ary, columns=te.columns_)
    print(basket_sets.head())
    return basket_sets

def import_dataset(name):
    if name == "uci_retail":
        return import_uci_retail()
    elif name == "uci_retail_mini":
        return import_uci_retail_mini()
    elif name == "instacart":
        return import_instacart()
    elif name == "T40I10D100K" or name == "T10I4D100K":
        return import_other("./Datasets/"+name+".dat.txt")
    elif name == "BMS1_spmf" or name == "BMS2":
        return import_BMS("./Datasets/"+name+".txt")
    else:
        return import_other("./Datasets/"+name+".dat")

def encode_units(x):
    if x <= 0:
        return 0
    if x >= 1:
        return 1