import pandas as pd

def information_loss(a, b):
    """
    Finds the information loss between the original database D, and the sanitized one D'

    Given a transactional database D and an associated sanitised database D′
    a is the frequent itemset dataframe of D
    b is the frequent itemset dataframe of D'
    """
    merged = pd.merge(a, b, how="outer", on=["itemsets"])
    merged = merged[merged['support_x'].notna()]

    # If one has itemsets that the other doesn't, its support is 0
    merged = merged.fillna(0)

    denominator = a.support.sum()
    numerator = sum(abs(merged["support_x"] - merged["support_y"]))

    return numerator / denominator
