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

    print(P)
    
    C = dict()
    #Call recursive part
    closed_itemsets = charm_extended(freq, P, threshold, C)
    return closed_itemsets, freq

def charm_extended(freq, P, min_sup, C):
    for i, Xi in enumerate(P):                      #For Xi x t(Xi) in P
        print("\nXi", Xi)
        Pi = []
        X = P[i][0]
        for Xj in P[i+1:]:                          #For Xj >= f Xi
            X = P[i][0]
            print("\nXj", Xj)
            X = Xi[0].union(Xj[0])
            Y = Xi[1].intersection(Xj[1])           #Tidset combining these
            print("Combined:", X, Y)

            #Should be finding the support of X and comparing to the threshold
            try:
                frequency = freq.loc[freq['itemsets'] == X].iloc[0]["support"]
            except:
                frequency = 0
            if frequency >= min_sup:
                if Xi[1] == Xj[1]:                  #Property 1
                    print("Property 1")
                    P = remove_x(P, Xj)             #Remove Xj from P
                    print("Deleting:", Xj)
                    P = replaceInItems(Xi, X, P)    #Replace Xi with X
                    Pi = replaceInItems(Xi, X, Pi)
                    Xi[0] = X

                elif Xi[1].issubset(Xj[1]):         #Property 2
                    print("Property 2")
                    P = replaceInItems(Xi, X, P)    #Replace all Xi with X
                    Pi = replaceInItems(Xi, X, Pi)
                    print(Pi)
                    Xi[0] = X

                elif Xi[1].issuperset(Xj[1]):       #Property 3
                    print("Property 3")
                    P = remove_x(P, Xj)             #Remove Xj from P
                    print("Deleting:", Xj)
                    Pi = add_item(X, Y, Pi)
                    print("Pi", Pi, X)

                elif Xi[1] != Xj[1]:                #Property 4
                    print("Property 4")
                    Pi = add_item(X, Y, Pi)
                    print("Pi", Pi, X)

        if Pi != []:
            print("Recursive:", Pi)
            C = charm_extended(freq, Pi, min_sup, C)                        #TODO: is it passing everything correctly
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

# def binary_search(l, freq):
#     low = 0
#     high = len(l)-1
#     while low < high: 
#         mid = (low+high)//2
#         print(mid, len(l[mid][1]))
#         if l[mid][2] > freq: 
#             high = mid-1
#         elif l[mid][2] < freq: 
#             low = mid+1
#         else: 
#             return mid
#     return -1

def binary_search(arr, key, start, end):
   #key
   if end - start <= 1:
      if key < len(arr[start][1]):
         return start - 1
      else:
         return start

   mid = (start + end)//2
   if len(arr[mid][1]) < key:
      return binary_search(arr, key, mid, end)
   elif len(arr[mid][1]) > key:
      return binary_search(arr, key, start, mid)
   else:
      return mid

def add_item(X, Y, Pi):
    #Pi = [Frequency, Union of items, Tidset]
    #Added in sorted order to each new class
    if len(Pi) == 0:
        Pi = [ [X, Y] ]
        return Pi
    else:
        #j = binary_search(Pi, len(Y)) 
        j = binary_search(Pi, len(Y), 0, len(Pi)) + 1
        Pi = Pi[:j] + [ [X, Y] ] + Pi[j+1:] 
        return Pi 

def main():
    threshold = 0.3
    data = im.import_dataset("toydata")
    

    print(get_closed_itemsets_new(data, threshold)[0])
    print(get_closed_itemsets(data, threshold)[0])

main()


"""
Should have:
{frozenset({'2'}): 1.0, 
frozenset({'2', '5'}): 0.9, 
frozenset({'2', '1', '5'}): 0.8, 
frozenset({'2', '3'}): 0.6, 
frozenset({'2', '4'}): 0.7, 
frozenset({'2', '1', '5', '4'}): 0.6, 
frozenset({'2', '3', '5'}): 0.5, 
frozenset({'2', '3', '1', '5'}): 0.4, 
frozenset({'2', '3', '4'}): 0.3}

Have:
frozenset({'2', '5', '4'}): 0.6, 
frozenset({'1', '2'}): 0.8, 

frozenset({'3', '2'}): 0.6, 
frozenset({'2', '4'}): 0.7, 
frozenset({'5', '1', '2', '4'}): 0.6,
frozenset({'2', '3', '5'}): 0.5, 
{frozenset({'5', '1', '3', '2'}): 0.4, 
frozenset({'2', '5'}): 0.9, 
frozenset({'2'}): 1.0}
"""