#from arm_utilities import get_closed_itemsets
from mlxtend.frequent_patterns import fpgrowth
import pandas as pd

import datasets.import_datasets as im
from arm_utilities import get_closed_itemsets

def get_closed_itemsets_new(baskets, min_sup):
    #An implementation of the CHARM closed frequent itemsets algorithm
    freq = fpgrowth(baskets, min_support=min_sup, use_colnames=True)

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
    frequency = min_sup * len(baskets)
    skip_set = []
    C = dict()
    #Call recursive part
    closed_itemsets, _ = charm_extended(frequency, P, C, skip_set)
    return closed_itemsets, freq

def charm_extended(freq, P, C, skip_set):
    for idi in range(len(P)):
        Xi = P[idi]
        print("Xi:", Xi[0])
        if Xi[0] in skip_set: 
            continue
        x_prev = Xi
        Pi = []
        for idj in range(idi+1, len(P)):
            Xj = P[idj]
            print("-Xi Xj:", Xi[0], Xj[0])
            if Xj in skip_set:
                continue
            X = Xi[0].union(Xj[0])
            Y = Xi[1].intersection(Xj[1])

            if len(Y) >= freq:
                if Xi[1] == Xj[1]:                      #Property 1
                    print("Property 1")
                    skip_set += [Xj]
                    temp = [Xi[0].union(Xj[0]), Xi[1].intersection(Xj[1])]
                    Pi = replaceInItems(Xi[0].copy(), temp[0], Pi)    #Replace works
                    P = replaceInItems(Xi[0].copy(), temp[0], P)     #Replace Xi with X
                    Xi = temp

                elif Xi[1].issubset(Xj[1]):             #Property 2
                    print("Property 2")
                    temp = [Xi[0].union(Xj[0]), Xi[1].intersection(Xj[1])]
                    Pi = replaceInItems(Xi[0].copy(), temp[0], Pi)      #Replace works
                    P = replaceInItems(Xi[0].copy(), temp[0], P)       #Replace Xi with X
                    Xi = temp

                elif Xi[1].issuperset(Xj[1]):           #Property 3
                    print("Property 3")
                    skip_set += [Xj]
                    Pi = add_item([X, Y], Pi)   #Add works
            
                elif Xi[1] != Xj[1]:                    #Property 4
                    print("Property 4")
                    Pi = add_item([X, Y], Pi)   #Add works

        if Pi != []:
            print("\nRecursive:", Pi)
            C, skip_set = charm_extended(freq, Pi, C, skip_set)

        if x_prev[0] != [] and x_prev[1] != [] and not is_subsumed(C, x_prev[1]):
            print("Adding 1:", x_prev)
            C[frozenset(x_prev[0])] = Y
        if Xi[0] != [] and Xi != x_prev and Xi[1] != [] and not is_subsumed(C, Xi[1]):
            print("Adding 2:", Xi)
            C[frozenset(Xi[0])] = Y

    return C, skip_set

def remove_x(P, Xj):
    for i, x in enumerate(P):
        if x[0] == Xj:
            del P[i]
            return P
    print("Couldn't find Xj")
    return P

def replaceInItems(current, target, set_a):
    #Replace Xi with X in A
    for i in range(len(set_a)):
        if current.issubset(set_a[i][0]):
            set_a[i][0] = set_a[i][0].difference(current)
            set_a[i][0] = set_a[i][0].union(target)
    return set_a

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

def add_item(X, Pi):
    #Pi = [Frequency, Union of items, Tidset]
    #Added in sorted order to each new class
    if len(Pi) == 0:
        Pi = [ X ]
        return Pi
    else:
        j = binary_search(Pi, len(X[1]), 0, len(Pi)) + 1
        Pi = Pi[:j] + [ X ] + Pi[j+1:] 
        return Pi 

def is_subsumed(C, Y):
    for _, value in C.items():
        if value == Y:
            return True
    return False

def main():
    threshold = 0.3
    data = im.import_dataset("toydata")
    

    CI_n = get_closed_itemsets_new(data, threshold)[0]
    CI_o = get_closed_itemsets(data, threshold)[0]

    same = []
    have = []
    missing = []
    for CI in CI_o:
        if CI in CI_n:
            same += [CI]
        else:
            missing += [CI]

    for CI in CI_n:
        if not CI in CI_o:
            have += [CI]
    
    print("Similar closed:", same)
    print("Need to remove:", have)
    print("Need to add to:", missing)

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