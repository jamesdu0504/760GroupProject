from mlxtend.frequent_patterns import fpgrowth
import pandas as pd

def charm(database, min_sup):
    frequent_itemsets = fpgrowth(database, min_support=min_sup, use_colnames=True)

    sorted_p = {}
    for _, row in frequent_itemsets.iterrows():
        if len(row["itemsets"]) == 1:
            sorted_p[row["itemsets"]] = row["support"]

    P = []  # Frequent single items ordered by f
    for i in sorted(sorted_p.items(), key=lambda x: x[1]):
        item = list(i[0])
        P += [(set(item), set(database.index[database[item[0]] == True].tolist()))]


    frequency_threshold = min_sup * len(database)
    C = dict()

    charm_extend(P, C, frequency_threshold)
    return C


def charm_property(x_i, t_i, x_j, t_j, X, Y, P, P_i, frequency_threshold):
    if len(Y) >= frequency_threshold:
        if t_i == t_j:
            # Property 1
            P.remove((x_j, t_j))
            return (x_i | x_j), P_i

        elif t_i < t_j:
            # Property 2
            return (x_i | x_j), P_i

        elif t_i > t_j:
            # Property 3
            P.remove((x_j, t_j))
            return x_i, add_item((X,Y), P_i)

        elif t_i != t_j:
            # Property 4
            return x_i, add_item((X,Y), P_i)

        else:
            print('Error: No property satisfied.')
            assert 1 == 2
    else:
        return x_i, P_i


def charm_extend(P, C, frequency_threshold):
    for i, (x_i, t_i) in enumerate(P):
        P_i, X = set(), x_i

        for j, (x_j, t_j) in enumerate(P[i+1:]):
            X = x_i | x_j
            Y = t_i & t_j
            x_i_new, P_i = charm_property(x_i, t_i, x_j, t_j, X, Y, P, P_i, frequency_threshold)

            if x_i != x_i_new:
                for x, _ in P_i:
                    x -= x_i
                    x |= x_i_new
                x_i = x_i_new

        if P_i:
            charm_extend(P_i, C, frequency_threshold)
        del P_i

        for itemset, transactions in C.items():
            if x_i <= itemset and len(t_i) == len(transactions):
                break
        else:
            C[frozenset(x_i)] = t_i



# def get_closed_itemsets_new(baskets, min_sup):
#     #An implementation of the CHARM closed frequent itemsets algorithm
#     freq = fpgrowth(baskets, min_support=min_sup, use_colnames=True)
#
#     #Get a sorted list of individual frequent itemsets
#     sorted_p = {}
#     for _, row in freq.iterrows():
#         if len(row["itemsets"]) == 1:
#             sorted_p[row["itemsets"]] = row["support"]
#
#     #Sort
#     P = [] #Frequent single items ordered by f
#     for i in sorted(sorted_p.items(), key=lambda x: x[1]):
#         item = list(i[0])
#         P += [[set(item), set(baskets.index[baskets[item[0]] == True].tolist())]]
#
#     frequency = min_sup * len(baskets)
#     skip_set = []
#     C = dict()
#     #Call recursive part
#     closed_itemsets, _ = charm_extended(frequency, P, C, skip_set)
#
#     length = len(baskets)
#     for key in closed_itemsets.keys():
#         closed_itemsets[key] = len(closed_itemsets[key])/length
#
#     return closed_itemsets, freq
#
# def charm_property(Xi, Xj, Y, min_sup, P, Pi, skip_set):
#     if len(Y[1]) >= min_sup:
#         temp = [Xi[0].union(Xj[0]), Xi[1].intersection(Xj[1])]
#         if Xi[1] == Xj[1]:                      #Property 1
#             #print("Property 1")
#             skip_set += [Xj]
#             Pi = replaceInItems(Xi[0].copy(), temp[0], Pi)
#             P = replaceInItems(Xi[0].copy(), temp[0], P)     #Replace Xi with X
#             return temp, Pi, P, skip_set
#
#         elif Xi[1].issubset(Xj[1]):             #Property 2
#             #print("Property 2")
#             Pi = replaceInItems(Xi[0].copy(), temp[0], Pi)
#             P = replaceInItems(Xi[0].copy(), temp[0], P)       #Replace Xi with X
#             return temp, Pi, P, skip_set
#
#         elif Xi[1].issuperset(Xj[1]):           #Property 3
#             #print("Property 3")
#             skip_set += [Xj]
#             Pi = add_item(temp, Pi)
#
#         elif Xi[1] != Xj[1]:                    #Property 4
#             #print("Property 4")
#             Pi = add_item(temp, Pi)
#
#     return Xi, Pi, P, skip_set
#
# def charm_extended(min_sup, P, C, skip_set):
#     #Combines charm_extended and charm_property
#     # - Freq: minimum support count
#     # - P: set of itemsets to loop through
#     # - C: dictionary of closed itemsets
#     # - skip_set: list of removed items
#
#     for idi in range(len(P)):
#         Xi = P[idi]
#         if Xi[0] in skip_set:
#             continue
#         x_prev = Xi
#         X = []
#         Pi = []
#         for idj in range(idi+1, len(P)):
#             Xj = P[idj]
#             if Xj in skip_set:
#                 continue
#             X = [Xi[0].union(Xj[0]), Xi[1].intersection(Xj[1])]
#             Xi, Pi, P, skip_set = charm_property(Xi, Xj, X, min_sup, P, Pi, skip_set)
#
#         if Pi != []:
#             #print("\nRecursive:", Pi)
#             C, skip_set = charm_extended(min_sup, Pi, C, skip_set)
#
#         if x_prev[0] != [] and x_prev[1] != [] and not is_subsumed(C, x_prev[1]):
#             #print("Adding 1:", x_prev)
#             C[frozenset(x_prev[0])] = x_prev[1]
#
#         if X != [] and X[0] != x_prev and X[1] != [] and not is_subsumed(C, X[1]):
#             #print("Adding 2:", Xi)
#             C[frozenset(X[0])] = X[1]
#
#     return C, skip_set
#
# def remove_x(P, Xj):
#     for i, x in enumerate(P):
#         if x[0] == Xj:
#             del P[i]
#             return P
#     #print("Couldn't find Xj")
#     return P
#
# def replaceInItems(current, target, set_a):
#     #Replace Xi with X in A
#     temp = []
#     for i in range(len(set_a)):
#         if current.issubset(set_a[i][0]):
#             temp += [i]
#
#     for i in temp:
#         set_a[i][0] = set_a[i][0].difference(current)
#         set_a[i][0] = set_a[i][0].union(target)
#     return set_a
#
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
#
# def is_subsumed(C, Y):
#     for _, value in C.items():
#         if value == Y:
#             return True
#     return False