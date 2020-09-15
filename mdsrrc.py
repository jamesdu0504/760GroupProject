import sys

sys.path.append("..")
import pandas as pd
import datasets.import_datasets as im #TODO:only here for testing purposes 
from mlxtend.frequent_patterns import fpgrowth


def mdsrrc(mct, mst, database, association_rules, sensitive_rules):
    """
    mct (float) minimum confidence threshold 
    mst (float) minimum support threshold 
    database (dataFrame) original transactional database
    association_rules () association rules mind from the original algorithm 
    """
    #TODO: check for the sake of uniform timing that association rules are generated in or outside of algorithms in the same way accross all algorithms 
    return

df=im.import_dataset("toydata")
print(df.head())
