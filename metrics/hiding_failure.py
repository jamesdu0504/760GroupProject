def hiding_failure(a, b):
    """
    Hiding Failure quantifies the amount of sensitive information remaining in the dataset.
    It is defined as the percentage of sensitive itemsets that remain in the sanitised database relative
    to how many existed in the original database. Ideally, hiding failure should be zero,
    meaning no sensitive itemsets are remaining in the dataset.

    Given a transactional database D and an associated sanitised database D′
    a is the set of sensitive itemsets in D
    b is set of sensitive itemsets in D'
    """
    return len(a) / len(b)
