def artifactual_patterns(a: set, b: set):
    """
    Measures the proportion of itemsets minded from the sanitised
    database which did not occur in the original database.

    Given a transactional database D and an associated sanitised database D′
    a is the set of itemsets in D
    b is the set of itemsets in D'
    """
    return (len(b) - len(a.intersection(b))) / len(b)
