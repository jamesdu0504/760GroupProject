def IL(d1, d2):
    """Finds the information loss between the original database (d1), and the sanitized one (d2)"""

    denominator = d1.support.sum()
    numerator = abs(d1.support - d2.support).sum()
    print(numerator)
    print(denominator)
    return numerator/denominator


def IL_expected(d, sigma_min):
    """Finds the expected information loss given a transactional database and a minimum hiding threshold"""

    denominator = d.support.sum()
    numerator = abs(d.support - sigma_min).sum()
    return numerator/denominator
