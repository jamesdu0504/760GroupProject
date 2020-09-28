def misses_cost(a: set, b: set):
    """
    Misses cost measures the proportion of non-sensitive itemsets hidden by the sanitisation process;
    this indicates the number of itemsets which are consistent across the original and sanitised database.

    Given a transactional database D and an associated sanitised database D′
    a is the set of non-sensitive frequent itemsets in D
    b is the set of non-sensitive frequent itemsets in D'
    """
    return (len(a) - len(b)) / len(a)
