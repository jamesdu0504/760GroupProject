# Send only non-sensitive item sets
def misses_cost(a, b):
    """
    Given a transactional database D and an associated sanitised database D′

    a is the set of non-sensitive itemsets in D
    b is set of non-sensitive itemsets in D'
    """
    return (len(a) - len(b)) / len(a)
