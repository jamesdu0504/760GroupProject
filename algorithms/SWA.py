
def association_rules_from_itemsets():
    #Need to convert into collection of possible rules we want to hide
    # sensitiveItemset (set) the sensitive itemset which is a subset of itemset and must be removed
    return sensitive_rules

def SWA(transaction, sensitive_rules, window_size):
    #Lets assume sensitive rules is a pair <rule, disclosure threshold> (Each restrictive rule has one)

    for t in transaction.iterrows(): #Step 1
        #Sort the items of each transaction in ascending order so we can use binary search
        #if it has all items of at least one restrictive rule
        #We store a list of transactions for the restrictive rules with frequency
        sensitive = False
        sort the items in t in ascending order
        for rule in sensitive_rules.keys():
            if there exists rule such that forall j item_j is in sensitive_rules.keys():
                T[rule] = T[rule] union t
                freq(item)=freq(item)+1
                sensitive = True

        #Sort in descending order
        if sensitive: #Step 2
            sort vector(freq) in descending order
            for rule in sensitive_rules.keys():
                select itemv such that itemv in rule and forall itemk in rule, freq(itemv) >= item[itemk]
                if freq[itemv] > 1: 
                    victimrri = itemv
                else:
                    victimrri <- randomly selected itemk such that itemk is in rule

    for rule in sensitive_rules.keys(): #Step 3
        Numtrans_rri = |T(rule)| * (1-sensitive_rules[rule]) #|T[rri]| = number of sensitive transactions for rri in K

    for rule in sensitive_rules.keys(): #Step 4
        sort transactions(T[rule]) #in ascending order of size

    for rule in sensitive_rules.keys(): #Step 5
        transToSanitize = select first NumTrans_rri from T[rule]
        in D sanitized for each transaction t in transToSanitize:
            t = (t-victim_rri)
            if sensitive_rules[rule] == 0:
                do a look ahead(rule, victimrri, t, sensitive_rules)
