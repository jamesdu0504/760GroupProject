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

    number_of_transactions=len(database.index)
    antecedents=sensitive_rules["antecedents"].tolist()
    consequents=sensitive_rules["consequents"].tolist()

    item_sensitivity=dict()
    rule_sensitivity=dict()
    clusters=dict()
    cluster_sensitivity=dict()
    sensitive_transactions=dict()
    transactions_sensitivity=dict()

    for antecedent, consequent in zip(antecedents,consequents):         
        if consequent in clusters:
            clusters[consequent].append(antecedent)
        else:
            clusters[consequent]=[antecedent]

        for item in itertools.chain(antecedent,consequent):
            if item in item_sensitivity:
                item_sensitivity[frozenset(item)]+=1
            else:
                item_sensitivity[frozenset(item)]=1
            
    for consequent, antecedents in clusters.items():
        consequent_sensitivity=item_sensitivity[consequent]
        sensitivity_of_cluster=consequent_sensitivity
        for antecedent in antecedents:
            antecedent_sensitivity=item_sensitivity[antecedent]
            rule_sensitivity[(antecedent, consequent)]=antecedent_sensitivity+consequent_sensitivity
            sensitivity_of_cluster+=antecedent_sensitivity
        cluster_sensitivity[consequent]=sensitivity_of_cluster

    for transaction_id, onehot in database.iterrows():
        for sensitive_item in item_sensitivity.keys():
            if onehot[list(sensitive_item)[0]]==True:
                sensitive_transactions[transaction_id]=set(item for item in item_sensitivity.keys() if onehot[list(item)[0]])
                break

    for transaction_id in sensitive_transactions.keys():
        transactions_sensitivity[transaction_id]=sum([item_sensitivity[item] for item in sensitive_transactions[transaction_id]])

    transactions_sensitivity=sorted(transactions_sensitivity.items(), key=lambda x: x[1], reverse=True) #A heap may be more effiecent
    cluster_sensitivity=sorted(cluster_sensitivity.items(), key=lambda x: x[1], reverse=True)     

    for cluster, sensitivity in cluster_sensitivity:
        cluster_items=set(i for i in itertools.chain([cluster]+clusters[cluster]))  #set of frozen sets
        
        all_rules_in_cluster_hidden=True
        for antecedent in clusters[cluster]:
            rule=sensitive_rules.loc[(sensitive_rules["antecedents"]==antecedent) & (sensitive_rules["consequents"]==cluster)]    
            if rule["support"].item()>mst and rule["confidence"].item()>mct:
                all_rules_in_cluster_hidden=False
                break
        if all_rules_in_cluster_hidden:
            continue
        for index, (transaction_id, sensitivity) in enumerate(transactions_sensitivity):
            intersection=cluster_items.intersection(sensitive_transactions[transaction_id])
            if intersection != set():
                database.loc[transaction_id, str(list(cluster)[0])] = False
                new_transaction=sensitive_transactions[transaction_id].difference(cluster)
                transactions_sensitivity[index]=(new_transaction, transactions_sensitivity[index][1]-item_sensitivity[cluster])
                sensitive_transactions[transaction_id]=new_transaction
                all_rules_in_cluster_hidden=True
                for antecedent in clusters[cluster]:
                    rule=sensitive_rules.loc[(sensitive_rules["antecedents"]==antecedent) & (sensitive_rules["consequents"]==cluster)]
                    sensitive_rules.loc[rule.index, ["support"]]-=1/number_of_transactions
                    sensitive_rules.loc[rule.index,["confidence"]]-=1/sensitive_rules.loc[sensitive_rules["antecedents"]==antecedent].count()
                    if rule["support"].item()>mst and rule["confidence"].item()>mct:
                        all_rules_in_cluster_hidden=False
                if all_rules_in_cluster_hidden:
                    break
        transactions_sensitivity=sorted(transactions_sensitivity, key=lambda x: x[1], reverse=True)

    return database


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