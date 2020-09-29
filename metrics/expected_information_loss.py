def expected_information_loss(a: set, b: set, sigma: float):
    """
    The information loss of the sanitised model is compared to the expected information loss.
    As the stopping condition for RPS is that all sensitive frequent itemsets are hidden
    below σ min the expected information loss can not be achieved by RPS.

    Given a transactional database D and an associated sanitised database D′
    a is the frequent itemset dataframe of D
    sigma is the sanitisation threshold
    """

    denominator = a.support.sum()
    #Subtract sigma only from frequencies containing a sensitive itemset
    a.loc[a["itemsets"].isin(b["itemsets"]), "support"] = a["support"] - sigma
    numerator = sum(abs(a["support"]))

    return numerator / denominator
