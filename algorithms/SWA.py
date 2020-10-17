import random

def association_rules_from_itemsets():
    #Need to convert into collection of possible rules we want to hide
    # sensitiveItemset (set) the sensitive itemset which is a subset of itemset and must be removed
    pass
    return sensitive_rules

def SWA(database, sensitive_rules, window_size):
    #Lets assume sensitive rules is a pair <rule, disclosure threshold> (Each restrictive rule has one)
    transactions_rules = dict() #T
    database_copy = database.copy()
    victim = {}

    #Step 1
    for index in range(window_size, database.shape[0], window_size): #TODO: fix
        for i, t in database.iterrows():
            #Sort the items of each transaction in ascending order so we can use binary search
            sensitive = False
            transaction = sorted(list(t["itemset"]))
            frequency = dict()

            #if it has all items of at least one restrictive rule
            #We store a list of transactions for the restrictive rules with frequency
            for rule in sensitive_rules.keys():
                if rule.issubset(t["itemset"]):
                    transactions_rules[rule] = transactions_rules.get(rule,[]) + [i]

                    #for item in rule we add to the frequency?
                    for item in rule:
                        frequency[item] = frequency.get(item,0) + 1
                    sensitive = True

            #Step 2:
            if sensitive:
                for rule in sensitive_rules.keys():
                    itemv = max(rule, lambda x: frequency[x])
                    # itemv = -1
                    # for itemk in rule:
                    #     if frequency.get(itemv,0) <= frequency[itemk]:
                    #         itemv = itemk

                    if frequency.get(itemv,0) > 1: 
                        victim[rule] = itemv
                    else:
                        victim[rule] = random.choice(rule) #may need to change to list

        num_trans = dict() 
        for rule in sensitive_rules.keys(): #Step 3
            num_trans[rule] = len(transactions_rules) * (1-sensitive_rules[rule]) #|T[rri]| = number of sensitive transactions for rri in K

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

                #TODO: need to do this
                # if sensitive_rules[rule] == 0:
                #     do a look ahead(rule, victimrri, t, sensitive_rules)

        return database_copy
