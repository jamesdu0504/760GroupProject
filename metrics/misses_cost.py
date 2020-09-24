# Send only non-sensitive item sets
def misses_cost(a, b):
    return (len(a) - len(b)) / len(a)
