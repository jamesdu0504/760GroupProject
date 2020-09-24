import itertools
import pandas as pd
import datasets.import_datasets as im #TODO:only here for testing purposes 
from mlxtend.frequent_patterns import association_rules, fpgrowth

def dsrrc(mct, mst, database, sensitive_rules):
    """
    mct (float) minimum confidence threshold 
    mst (float) minimum support threshold 
    database (dataFrame) original transactional database
    sensitive_rules (dataframe as per:http://rasbt.github.io/mlxtend/user_guide/frequent_patterns/association_rules/#example-1-generating-association-rules-from-frequent-itemsets) the set of sensitive rules
    WARNING: this algorithm assumes for sensitive rules the consequent and antecedent is each one item
    """
    #TODO: check for the sake of uniform timing that association rules are generated in or outside of algorithms in the same way accross all algorithms 
    
    number_of_transactions=len(database.index)
    antecedents=sensitive_rules["antecedents"].tolist()
    consequents=sensitive_rules["consequents"].tolist()

    clusters=dict()
    cluster_sensitivity=dict()

    item_sensitivity=dict()         #should of only been per cluster.
    rule_sensitivity=dict()
    
    sensitive_transactions=dict()
    transactions_sensitivity=dict()

    #generate clusters
    for antecedent, consequent in zip(antecedents,consequents):         
        if consequent in clusters:
            clusters[consequent].append(antecedent)
        else:
            clusters[consequent]=[antecedent]
    
    #calculate item sensitivity per cluster
    for cluster, antecedents in clusters.items():
        sensitivities={}
        sensitivities[cluster]=len(antecedents)
        for item in antecedents:
            if item in sensitivities:
                sensitivities[item]+=1
            else:
                sensitivities[item]=1
        item_sensitivity[cluster]=sensitivities

    #calculate rule sensitivity per cluster
    for cluster, antecedents in clusters.items():
        sensitivities=item_sensitivity[cluster]
        c=sensitivities[cluster]
        for antecedent in antecedents:
            rule=(cluster,antecedent)
            a=sensitivities[antecedent]
            rule_sensitivity[rule]=c+a
    
    #cluster sensitivity
    for cluster, antecedents in clusters.items():
        sensitivity=0
        for antecedent in antecedents:
            sensitivity+=rule_sensitivity[(cluster, antecedent)]
        cluster_sensitivity[cluster]=sensitivity
    
#toy data test case
# database=im.import_dataset("toydata")
# frequent_itemsets=fpgrowth(database, min_support=0.3, use_colnames=True) #must use colum names or else the code will break!!!
# mined_association_rules=association_rules(frequent_itemsets, metric="confidence", min_threshold=0.8)
# pd.set_option("display.max_rows", None, "display.max_columns", None)
# print(mined_association_rules)
# sensitive_rules=mined_association_rules[:4].copy()
# new_database=dsrrc(0.5, 0.3, database,sensitive_rules)
# new_frequent_itemsets=fpgrowth(new_database, min_support=0.3, use_colnames=True) #must use colum names or else the code will break!!!
# new_mined_association_rules=association_rules(new_frequent_itemsets, metric="confidence", min_threshold=0.8)
# print(new_mined_association_rules)