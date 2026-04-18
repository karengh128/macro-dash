import pandas_datareader.data as web


def get_fred_series(series_id, name, start, end):
    df = web.DataReader(series_id, "fred", start, end)
    df = df.rename(columns={series_id: name})
    df = df.dropna()
    return df


def get_core_pce(start, end):
    return get_fred_series("PCEPILFE", "Core PCE", start, end)


def get_cpi(start, end):
    return get_fred_series("CPIAUCSL", "CPI", start, end)


def get_unemployment(start, end):
    return get_fred_series("UNRATE", "Unemployment", start, end)


def get_gdp(start, end):
    return get_fred_series("GDP", "GDP", start, end)


def get_fed_rate(start, end):
    return get_fred_series("FEDFUNDS", "Fed Rate", start, end)


def get_m2(start, end):
    return get_fred_series("M2SL", "M2", start, end)