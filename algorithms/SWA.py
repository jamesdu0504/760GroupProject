import random

def association_rules_from_itemsets():
    #Need to convert into collection of possible rules we want to hide
    # sensitiveItemset (set) the sensitive itemset which is a subset of itemset and must be removed
    pass
    return sensitive_rules

def SWA(database, sensitive_rules, window_size):
    #Lets assume sensitive rules is a pair <rule, disclosure threshold> (Each restrictive rule has one)
    transactions = dict()
    transactions_rules = dict()
    database_copy = database.copy()

    #Step 1
    for i, t in database.iterrows():
        #Sort the items of each transaction in ascending order so we can use binary search
        sensitive = False
        transaction = sorted(list(t["itemset"]))
        transactions[i] = transaction
        frequency = dict()

        #if it has all items of at least one restrictive rule
        #We store a list of transactions for the restrictive rules with frequency
        for rule in sensitive_rules.keys():
            if rule.issubset(t["itemset"]):
                transactions_rules[rule] = transactions_rules.get(rule,[]) + [i]

                #for item in rule we add to the frequency? TODO: is this right or is it for all sensitive items in both?
                for item in list(rule):
                    frequency[item] = frequency.get(item,0) + 1
                sensitive = True

        #Step 2: Sort in descending order
        if sensitive:
            freq = {k: v for k, v in sorted(frequency.items(), reversed=True, key=lambda item: item[1])}
            for rule in sensitive_rules.keys():
                rule_items = list(rule)
                itemv = 0
                for itemk in rule_items:
                    if freq.get(itemv,0) <= freq[itemk]:
                        itemv = itemk

                if freq.get(itemv,0) > 1: 
                    victimrri = itemv
                else:
                    victimrri = random.choice(rule_items)

    num_trans = dict() 
    for rule in sensitive_rules.keys(): #Step 3
        num_trans[rule] = len(transactions_rules) * (1-sensitive_rules[rule]) #|T[rri]| = number of sensitive transactions for rri in K

    #Step 4: sort transactions(T[rule]) in ascending order of size
    for rule in sensitive_rules.keys(): 
        sorted_num_trans = {k: v for k, v in sorted(num_trans.items(), key=lambda item: item[1])}

    #Step 5: 
    for rule in sensitive_rules.keys(): 
        #Select transactions to sanitize
        transToSanitize = transactions_rules[rule][:num_trans[rule]]

        for i in transToSanitize:
            #Sanitize transaction
            itemsets = database_copy.at[i, "itemsets"].remove(rule)
            database_copy.at[i, "itemsets"] = itemsets

            #TODO: need to do this
            # if sensitive_rules[rule] == 0:
            #     do a look ahead(rule, victimrri, t, sensitive_rules)

    return database_copy
