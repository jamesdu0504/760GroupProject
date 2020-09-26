#from arm_utilities import get_closed_itemsets
from mlxtend.frequent_patterns import fpgrowth
import pandas as pd

import datasets.import_datasets as im

def get_closed_itemsets_new(baskets, threshold):
    #An implementation of the CHARM closed frequent itemsets algorithm
    freq = fpgrowth(baskets, min_support=threshold, use_colnames=True)

    #Get a sorted list of individual frequent itemsets
    sorted_p = {}
    for _, row in freq.iterrows():
        if len(row["itemsets"]) == 1:
            if row["support"] > threshold:
                sorted_p[row["itemsets"]] = row["support"]

    #Sort
    P = [] #Frequent single items ordered by f
    for i in sorted(sorted_p.items(), key=lambda x: x[1], reverse=True):
        P += [i[0]]
    
    T = {} #Tidset indexed by P_i
    #Find transactions that each of P occur in and store as a list
    for P_i in P:
        T[P_i] = set(baskets.index[baskets[P_i]])

    #Call recursive part
    closed_itemsets = charm_extended(freq, P, threshold, dict())
    #return closed_itemsets, itemsets

def charm_extended(freq, P, min_sup, C, T):
    for i, Xi in enumerate(P):                  #For Xi x t(Xi) in P
        Pi = {}
        for Xj in P[i+1:]:                      #For Xj >= f Xi
            X = Xi.union(Xj)
            Y = T[Xj].intersection(T[Xj])       #Tidset combining these

            #Should be finding the support of X and comparing to the threshold
            if freq.loc[freq['itemsets'] == X].iloc[0]["support"] >= min_sup:
                if T[Xi] == T[Xj]:              #Property 1
                    print("Property 1")
                    P.discard(Xj)               #Remove Xj from P
                    replaceInItems(Xi,X)        #Replace Xi with X

                elif T[Xi].issubset(T[Xj]):     #Property 2
                    print("Property 2")
                    replaceInItems(Xi,X)        #Replace all Xi with X

                elif T[Xi].issuperset(T[Xj]):   #Property 3
                    print("Property 3")
                    P = P.discard(Xj)           #Remove Xj from P
                    Pi.add(X)                   #TODO: Add X x Y to [Pi] using ordering f

                elif T[Xi] != T[Xj]:            #Property 4
                    print("Property 4")
                                                #TODO: Add X x Y to [Pi] using ordering f

        if Pi != {}:
            C = charm_extended(freq, Pi, min_sup, C) #TODO: is it passing everything correctly
        del Pi                                  #TODO: what are we deleting?
        C.append((X, row['support']))
    return C

def replaceInItems(current, target, set_a):
    #TODO: replace occurances of current with target in set_a
    #Replace Xi with X in A
    for key in set_a.keySet():
        if key.contains(curr):
            temp.add(key)

    for key in temp:
        val = set_a.get(key)
        set_a.remove(key)
        key.addAll(target)
        set_a.put(key, val)


def main():
    threshold = 0.3
    data = im.import_dataset("toydata")
    get_closed_itemsets_new(data, threshold)

main()