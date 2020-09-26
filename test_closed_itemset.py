#from arm_utilities import get_closed_itemsets
from mlxtend.frequent_patterns import fpgrowth
import pandas as pd

import datasets.import_datasets as im
from arm_utilities import get_closed_itemsets

def get_closed_itemsets_new(baskets, threshold):
    #An implementation of the CHARM closed frequent itemsets algorithm
    freq = fpgrowth(baskets, min_support=threshold, use_colnames=True)

    #Get a sorted list of individual frequent itemsets
    sorted_p = {}
    for _, row in freq.iterrows():
        if len(row["itemsets"]) == 1:
            sorted_p[row["itemsets"]] = row["support"]

    #Sort
    P = [] #Frequent single items ordered by f
    for i in sorted(sorted_p.items(), key=lambda x: x[1]):
        item = list(i[0])
        P += [[set(item), set(baskets.index[baskets[item[0]] == True].tolist())]]
    
    C = dict()
    #Call recursive part
    closed_itemsets = charm_extended(freq, P, threshold, C)
    return closed_itemsets, freq

def charm_extended(freq, P, min_sup, C):
    for i, Xi in enumerate(P):                      #For Xi x t(Xi) in P
        Pi = []
        X = Xi[0]
        for Xj in P[i+1:]:                          #For Xj >= f Xi
            print("\n", Xi, Xj)
            X = Xi[0].union(Xj[0])
            Y = Xi[1].intersection(Xj[1])           #Tidset combining these

            #Should be finding the support of X and comparing to the threshold
            try:
                frequency = freq.loc[freq['itemsets'] == X].iloc[0]["support"]
            except:
                frequency = 0
            if frequency >= min_sup:
                if Xi[1] == Xj[1]:                  #Property 1
                    print("Property 1")
                    print(P, Xj)
                    P = remove_x(P, Xj)             #Remove Xj from P
                    print(P, Xj)
                    P = replaceInItems(Xi, X, P)    #Replace Xi with X

                elif Xi[1].issubset(Xj[1]):         #Property 2
                    print("Property 2")
                    P = replaceInItems(Xi, X, P)    #Replace all Xi with X

                elif Xi[1].issuperset(Xj[1]):       #Property 3
                    print("Property 3")
                    P = remove_x(P, Xj)             #Remove Xj from P
                    Pi = add_item(X, Y, Pi)

                elif Xi[1] != Xj[1]:                #Property 4
                    print("Property 4")
                    Pi = add_item(X, Y, Pi)

        if Pi != {}:
            C = charm_extended(freq, Pi, min_sup, C)                        #TODO: is it passing everything correctly
        del Pi                                                              #TODO: what are we deleting?
        try:
            C[frozenset(X)] = freq.loc[freq['itemsets'] == X].iloc[0]["support"]
        except:
            print("Index error", X)
    return C

def remove_x(P, Xj):
    for i, x in enumerate(P):
        if x[0] == Xj:
            del P[i]
            return P
    print("Couldn't find Xj")
    return P

def replaceInItems(current, target, set_a):
    #Replace Xi with X in A
    for i, key in enumerate(set_a):
        if current[0] == current[0].intersection(key[0]):
            set_a[i][0] = set_a[i][0].difference(current[0])
            set_a[i][0] = set_a[i][0].union(target)
    return set_a

def binary_search(l, freq):
    low = 0
    high = len(l)-1
    while low <= high: 
        mid = (low+high)//2
        if len(l[mid]) > freq: 
            high = mid-1
        elif len(l[mid]) < freq: 
            low = mid+1
        else: 
            return mid
    return -1

def add_item(X, Y, Pi):
    #Pi = [Frequency, Union of items, Tidset]
    #Added in sorted order to each new class
    if len(Pi) == 0:
        Pi = [ [X, Y] ]
        return Pi
    else:
        j = binary_search(Pi, len(Y)) 
        Pi = Pi[:j] + [ [X, Y] ] + Pi[j+1:] 
        return Pi 

def main():
    threshold = 0.3
    data = im.import_dataset("toydata")
    print(get_closed_itemsets_new(data, threshold)[0])
    print(get_closed_itemsets(data, threshold)[0])

main()