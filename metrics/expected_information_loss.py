def expected_information_loss(a: set, sigma: float):
    """
    The information loss of the sanitised model is compared to the expected information loss.
    As the stopping condition for RPS is that all sensitive frequent itemsets are hidden
    below σ min the expected information loss can not be achieved by RPS.

    Given a transactional database D and an associated sanitised database D′
    a is the frequent itemset dataframe of D
    sigma is the sanitisation threshold
    """

    denominator = a.support.sum()
    numerator = sum(abs(a.support - sigma))

    return numerator / denominator
