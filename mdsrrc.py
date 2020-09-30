import itertools
import pandas as pd
import numpy as np
import datasets.import_datasets as im #TODO:only here for testing purposes 
from mlxtend.frequent_patterns import association_rules, fpgrowth


def items_and_transactions_to_sanitize(database, sensitive_transactions, transaction_sensitivity, frequency_on_rhs, num_transactions):
    sorted_rhs_items=[(item, frequency ,database.loc[database[item]==True].shape[0]/num_transactions) for item, frequency in frequency_on_rhs.items()]
    sorted_rhs_items=sorted(sorted_rhs_items, key=lambda x: (x[1], x[2]))

    #select all transations which support is0
    is0=sorted_rhs_items.pop()[0]
    is0_transactions=[]
    for transaction_id, transaction in sensitive_transactions.items():
        if is0 in transaction:
            is0_transactions.append((transaction,transaction_sensitivity[transaction],transaction_id))

    sorted_is0_transactions=sorted(is0_transactions, key= lambda x: (-1*x[1],len(x[0])))

    return is0, sorted_is0_transactions

def mdsrrc(mct, mst, database, minded_sensitive_rules):
    """
    mct (float) minimum confidence threshold 
    mst (float) minimum support threshold 
    database (dataFrame) original transactional database
    association_rules () association rules mind from the original algorithm 
    """
    num_transactions= database.shape[0]
    
    rules=list(zip(sensitive_rules["antecedents"].tolist(), set(sensitive_rules["consequents"].tolist())))
    support_and_confidence_of_rules = list(zip(sensitive_rules["support"].tolist(), sensitive_rules["confidence"].tolist()))
    item_sensitivity=dict() 
    frequency_on_rhs=dict()
    
    for lhs,rhs in rules:
        for item in lhs:
            if item in item_sensitivity:
                item_sensitivity[item]+=1
            else:
                item_sensitivity[item]=1
        for item in rhs:
            if item in item_sensitivity:
                item_sensitivity[item]+=1
            else:
                item_sensitivity[item]=1
            if item in frequency_on_rhs:
                frequency_on_rhs[item]+=1
            else:
                frequency_on_rhs[item]=1
       
    sensitive_transactions=dict()
    transaction_sensitivity=dict()
    for transaction_id, onehot in database.iterrows():
        for sensitive_item in item_sensitivity.keys():
            if onehot[[sensitive_item][0]]==True:
                transaction=frozenset(item for item in database.columns if onehot[[item][0]])
                sensitive_transactions[transaction_id]=transaction
                transaction_sensitivity[transaction]=sum([item_sensitivity[item] for item in transaction if item in item_sensitivity])
                break
    
    is0, sorted_is0_transactions = items_and_transactions_to_sanitize(database, sensitive_transactions, transaction_sensitivity,frequency_on_rhs, num_transactions)

    while rules:
        transaction, transaction_sensitivity_value, transaction_id=sorted_is0_transactions.pop(0)
        new_transaction=transaction.difference(set(is0))
        #code to support sudo line 19 
        sensitive_transactions[transaction_id]=new_transaction
        if transaction in transaction_sensitivity:
            del transaction_sensitivity[transaction]

        database[is0][transaction_id]=False
        
        for index, rule in enumerate(rules):
            lhs, rhs = rule
            if is0 in rhs:
                support, confidence = support_and_confidence_of_rules[index]
                new_support=support-1/num_transactions
                new_confidence= confidence - 1/len(np.where(np.all(database[list(lhs)], axis=1)))
                support_and_confidence_of_rules[index]=(new_support, new_confidence)
                if new_support<mst or new_confidence<mct:
                    rule.pop(index)
                    for item in lhs:
                        item_sensitivity[item]-=1
                    for item in rhs:
                        item_sensitivity[item]-=1
                        frequency_on_rhs[item]-=1
                    for transaction in sensitive_transactions.values(): 
                        transaction_sensitivity[transaction]=sum([item_sensitivity[item] for item in transaction if item in item_sensitivity])
                    is0, sorted_is0_transactions = items_and_transactions_to_sanitize(database, sensitive_transactions, transaction_sensitivity,frequency_on_rhs, num_transactions)

                    
    return database


#toy data test case
database=im.import_dataset("toydata")
print(database.head())
frequent_itemsets=fpgrowth(database, min_support=0.3, use_colnames=True) #must use colum names or else the code will break!!!
print(frequent_itemsets.head())
mined_association_rules=association_rules(frequent_itemsets, metric="confidence", min_threshold=0.8)
pd.set_option("display.max_rows", None, "display.max_columns", None)
print(mined_association_rules)

sensitive_rules=mined_association_rules[:4].copy()

new_database=mdsrrc(0.5, 0.3, database,sensitive_rules)
new_frequent_itemsets=fpgrowth(new_database, min_support=0.3, use_colnames=True) #must use colum names or else the code will break!!!
new_mined_association_rules=association_rules(new_frequent_itemsets, metric="confidence", min_threshold=0.8)
print(new_mined_association_rules)


# def mdsrrc(mct, mst, database, association_rules, sensitive_rules):
#     """
#     mct (float) minimum confidence threshold 
#     mst (float) minimum support threshold 
#     database (dataFrame) original transactional database
#     association_rules () association rules mind from the original algorithm 
#     """
#     #TODO: check for the sake of uniform timing that association rules are generated in or outside of algorithms in the same way accross all algorithms 
#     number_of_transactions=len(database.index)
#     antecedents=sensitive_rules["antecedents"].tolist()
#     consequents=sensitive_rules["consequents"].tolist()

#     item_sensitivity=dict()
#     rule_sensitivity=dict()
#     clusters=dict()
#     cluster_sensitivity=dict()
#     sensitive_transactions=dict()
#     transactions_sensitivity=dict()

#     for antecedent, consequent in zip(antecedents,consequents):         
#         if consequent in clusters:
#             clusters[consequent].append(antecedent)
#         else:
#             clusters[consequent]=[antecedent]

#         for item in itertools.chain(antecedent,consequent):
#             if item in item_sensitivity:
#                 item_sensitivity[frozenset(item)]+=1
#             else:
#                 item_sensitivity[frozenset(item)]=1
            
#     for consequent, antecedents in clusters.items():
#         consequent_sensitivity=item_sensitivity[consequent]
#         sensitivity_of_cluster=consequent_sensitivity
#         for antecedent in antecedents:
#             antecedent_sensitivity=item_sensitivity[antecedent]
#             rule_sensitivity[(antecedent, consequent)]=antecedent_sensitivity+consequent_sensitivity
#             sensitivity_of_cluster+=antecedent_sensitivity
#         cluster_sensitivity[consequent]=sensitivity_of_cluster

#     for transaction_id, onehot in database.iterrows():
#         for sensitive_item in item_sensitivity.keys():
#             if onehot[list(sensitive_item)[0]]==True:
#                 sensitive_transactions[transaction_id]=set(item for item in item_sensitivity.keys() if onehot[list(item)[0]])
#                 break

#     for transaction_id in sensitive_transactions.keys():
#         transactions_sensitivity[transaction_id]=sum([item_sensitivity[item] for item in sensitive_transactions[transaction_id]])

#     transactions_sensitivity=sorted(transactions_sensitivity.items(), key=lambda x: x[1], reverse=True) #A heap may be more effiecent
#     cluster_sensitivity=sorted(cluster_sensitivity.items(), key=lambda x: x[1], reverse=True)     

#     for cluster, sensitivity in cluster_sensitivity:
#         cluster_items=set(i for i in itertools.chain([cluster]+clusters[cluster]))  #set of frozen sets
        
#         all_rules_in_cluster_hidden=True
#         for antecedent in clusters[cluster]:
#             rule=sensitive_rules.loc[(sensitive_rules["antecedents"]==antecedent) & (sensitive_rules["consequents"]==cluster)]    
#             if rule["support"].item()>mst and rule["confidence"].item()>mct:
#                 all_rules_in_cluster_hidden=False
#                 break
#         if all_rules_in_cluster_hidden:
#             continue
#         for index, (transaction_id, sensitivity) in enumerate(transactions_sensitivity):
#             intersection=cluster_items.intersection(sensitive_transactions[transaction_id])
#             if intersection != set():
#                 database.loc[transaction_id, str(list(cluster)[0])] = False
#                 new_transaction=sensitive_transactions[transaction_id].difference(cluster)
#                 transactions_sensitivity[index]=(new_transaction, transactions_sensitivity[index][1]-item_sensitivity[cluster])
#                 sensitive_transactions[transaction_id]=new_transaction
#                 all_rules_in_cluster_hidden=True
#                 for antecedent in clusters[cluster]:
#                     rule=sensitive_rules.loc[(sensitive_rules["antecedents"]==antecedent) & (sensitive_rules["consequents"]==cluster)]
#                     sensitive_rules.loc[rule.index, ["support"]]-=1/number_of_transactions
#                     sensitive_rules.loc[rule.index,["confidence"]]-=1/sensitive_rules.loc[sensitive_rules["antecedents"]==antecedent].count()
#                     if rule["support"].item()>mst and rule["confidence"].item()>mct:
#                         all_rules_in_cluster_hidden=False
#                 if all_rules_in_cluster_hidden:
#                     break
#         transactions_sensitivity=sorted(transactions_sensitivity, key=lambda x: x[1], reverse=True)

#     return database
