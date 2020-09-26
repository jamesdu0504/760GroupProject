def side_effects_factor(a: set, b: set, c: set):
    """
    Side effect factor is similar to misses cost and is used to quantify the number of non-sensitive rules
    which are removed by the sanitation process.

    Given a transactional database D and an associated sanitised database D′
    a is the set of itemsets in D
    b is the set of itemsets in D'
    c is the set of sensitive itemsets in D
    """
    numerator = len(a) - (len(b) + len(c))
    denominator = len(a) - len(c)
    return numerator / denominator