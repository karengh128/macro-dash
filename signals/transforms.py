def yoy_change(series):
    return series.pct_change(12) * 100


def qoq_annualized(series):
    return ((series / series.shift(1)) ** 4 - 1) * 100