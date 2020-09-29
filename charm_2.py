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
    C = {k: v for _, itemsets in C.items()
         for k,v in itemsets}
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
        x_prev = x_i
        Y = t_i

        for j, (x_j, t_j) in enumerate(P[i+1:]):
            X = x_i | x_j
            Y = t_i & t_j
            x_i_new, P_i = charm_property(x_i, t_i, x_j, t_j, X, Y, P, P_i, frequency_threshold)

            if x_i != x_i_new:
                # Replace in P
                for x, _ in P:
                    if x_i <= x:
                        x |= x_i_new

                # Replace in P_i
                for x, _ in P_i:
                    x |= x_i_new
                x_i = x_i_new

        if P_i:
            charm_extend(P_i, C, frequency_threshold)


        # Check if x_prev still in P
        if P[i][0] == x_prev and not is_subsumed(x_prev, t_i, C):
            hash_value = sum(t_i)
            if hash_value not in C:
                C[hash_value] = []
            C[hash_value].append((frozenset(x_prev), t_i))


        elif P[i][0] == X and not is_subsumed(X, Y, C):
            hash_value = sum(Y)
            if hash_value not in C:
                C[hash_value] = []
            C[hash_value].append((frozenset(X), Y))






#
# def remove_x(P, Xj):
#     for i, x in enumerate(P):
#         if x[0] == Xj:
#             del P[i]
#             return P
#     #print("Couldn't find Xj")
#     return P
#
def replaceInItems(current, target, set_a):
    #Replace Xi with X in A
    temp = []
    for i in range(len(set_a)):
        if current.issubset(set_a[i][0]):
            temp += [i]

    for i in temp:
        set_a[i][0] = set_a[i][0].difference(current)
        set_a[i][0] = set_a[i][0].union(target)
    return set_a
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
        Pi = Pi[:j+1] + [ X ] + Pi[j+1:]
        return Pi


def is_subsumed(X, Y, C):
    hash_value = sum(Y)
    if hash_value not in C:
        return False
    for itemset, transactions in C[hash_value]:
        if X <= itemset and Y == len(transactions):
            return True
    return False


