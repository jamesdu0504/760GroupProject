from mlxtend.frequent_patterns import fpgrowth
import pandas as pd

def get_closed_itemsets_new(baskets, threshold):
    #An implementation of the CHARM closed frequent itemsets algorithm
    freq = fpgrowth(baskets, min_support=threshold, use_colnames=True)

    #Get set of frequent individual items
    P = set()
    for _, row in freq.iterrows():
        if len(row["itemsets"]) == 1:
            if row["support"] > threshold:
                P.add(set(row["itemsets"]))

    #Call recursive part
    closed_itemsets = charm_extend(freq, P, threshold, dict())
    return closed_itemsets, itemsets

def charm_extend(freq, P, threshold):
    for Xi in P:                                #For Xi x t(Xi) in P
        Pi = set()                              #Empty set,
        for Xj in P:                            #For Xj >= f Xi
            X = Xi.union(Xj)
            Y = t(Xi).intersection(t(Xj))

            #Should be finding the support of X and comparing to the threshold
            if freq.loc[freq['itemsets'] == X].iloc[0]["support"] >= threshold:
                if t(Xi) == t(Xj):              #Property 1
                    P.discard(Xj)               #Remove Xj from P
                    #Replace Xi with X

                elif t(Xi).issubset(t(Xj)):     #Property 2
                    #Replace all Xi with X

                elif t(Xj).issuperset(t(Xj)):   #Property 3
                    P = P.discard(Xj)           #Remove Xj from P
                    #Add X x Y to [Pi] using ordering f

                elif t(Xi) != t(Xj):            #Property 4
                    #Add X x Y to [Pi] using ordering f

        if Pi != {}:
            C = charm_extend(freq, Pi, threshold, C)
        del Pi
        cl.append((X, row['support']))
    return C