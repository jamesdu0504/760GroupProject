from mlxtend.preprocessing import TransactionEncoder
from sklearn.preprocessing import MultiLabelBinarizer
import pandas as pd


# Each import function imports a dataset into the form of a matrix, each row is a transaction
# each column is a item

def import_uci_retail():
    #Retail dataset provided by UC Irvine
    #Uses full dataset
    df = pd.read_excel('./datasets/Online Retail.xlsx')
    df['Description'] = df['Description'].str.strip()
    df.dropna(axis=0, subset=['InvoiceNo'], inplace=True)
    df['InvoiceNo'] = df['InvoiceNo'].astype('str')
    df = df[df.Description != 'Postage']
    df = df[~df['InvoiceNo'].str.contains('C')]
    df = df[df.Quantity > 0]
    df['Quantity'] = 1
    basket = (df.groupby(['InvoiceNo', 'Description'])['Quantity'].sum().unstack().reset_index().fillna(0).set_index('InvoiceNo'))
    basket_sets = basket.applymap(encode_units)
    basket_sets.columns=basket_sets.columns.str.replace(' ','_')
    return basket_sets

def import_instacart():
    #Instacart retail dataset
    df = pd.read_csv('./datasets/order_products__train.csv')
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
    file_object = open(filename, "r")
    transactions = []
    contents = file_object.readlines()
    for i in range(len(contents)):
        transactions.append(contents[i].rstrip(' \n').split(" "))
    file_object.close()
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions)
    basket_sets = pd.DataFrame(te_ary, columns=te.columns_)
    return basket_sets

def convert_to_transaction(db):
    #This reads the files that come in the format of one line per transaction
    transactions = {}
    for i, row in db.iterrows():
        row_set = row.index[row == True].tolist()
        transactions[i] = set(row_set)
    transaction_set = pd.DataFrame(transactions.items(), columns=['index', 'itemsets'])
    return transaction_set

def convert_to_matrix(db):
    pass

def import_dataset(name):
    if name == "uci_retail":
        return import_uci_retail()
    elif name == "instacart":
        return import_instacart()
    elif name == "T40I10D100K" or name == "T10I4D100K":
        return import_other("./datasets/"+name+".dat.txt")
    else:
        return import_other("./datasets/"+name+".dat")

def encode_units(x):
    if x <= 0:
        return 0
    if x >= 1:
        return 1