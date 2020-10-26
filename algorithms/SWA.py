import random
import pandas as pd

from mlxtend.frequent_patterns import fpgrowth

import sys
sys.path.insert(0, '..')
import datasets.import_datasets as im
from charm_algorithm import get_closed_itemsets_Charm as get_closed_itemsets
from support_distribution_graph import dual_support_graph_distribution
from arm_utilities import itemsets_from_closed_itemsets



def SWA(database, sensitive_rules, window_size):
    #Lets assume sensitive rules is a pair <rule, disclosure threshold> (Each restrictive rule has one)
    database_copy = database.copy()
    victim = {} #Victim Item Transaction

    #Step 1
    for index in range(0, database.shape[0], window_size): #Loop through window
        transactions_rules = dict() #T

        for i in range(index, min(index+window_size, database.shape[0])): #Loop through transactions in splice
            t = database.loc[i]

            #Sort the items of each transaction in ascending order so we can use binary search
            sensitive_rules_present = []
            transaction = sorted(list(t["itemset"]))
            frequency = dict()

            #if it has all items of at least one restrictive rule
            #We store a list of transactions for the restrictive rules with frequency
            for rule in sensitive_rules.keys():
                if rule.issubset(transaction):
                    transactions_rules[rule] = transactions_rules.get(rule,[]) + [i]

                    #for item in rule we add to the frequency?
                    for item in rule:
                        frequency[item] = frequency.get(item,0) + 1
                    
                    sensitive_rules_present += [rule]

            #Step 2:
            if sensitive_rules_present:
                for rule in sensitive_rules_present:
                    itemv = max(rule, lambda x: frequency[x])
                    if frequency.get(itemv,0) > 1: 
                        victim[rule] = itemv
                    else:
                        victim[rule] = random.choice(rule) #may need to change to list

        #Step 3:
        num_trans = dict() 
        for rule in sensitive_rules.keys(): #Step 3
            num_trans[rule] = len(transactions_rules[rule]) * (1-sensitive_rules[rule]) #|T[rri]| = number of sensitive transactions for rri in K

        #Step 4: sort transactions(T[rule]) in ascending order of size
        for rule in sensitive_rules.keys(): 
            transactions_rules[rule] = [k for k in sorted(transactions_rules[rule].items(), reversed=True, key=lambda item: len(item[1]))]

        #Step 5: 
        for rule in sensitive_rules.keys(): 
            #Select transactions to sanitize
            transToSanitize = transactions_rules[rule][:num_trans[rule]]

            for i in transToSanitize:
                #Sanitize transaction
                database_copy.at[i, "itemsets"] = database_copy.at[i, "itemsets"].remove(victim[rule])

    return database_copy

data = im.import_dataset("toydata")

sensitiveItemsets = {frozenset(["4"]): 0.3, frozenset(["1", "2"]): 0.3}

SWA(data, sensitiveItemsets, 10)