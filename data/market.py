import yfinance as yf


def get_market_series(ticker, name, start, end):
    df = yf.download(ticker, start=start, end=end)

    # Fix multi-index issue
    if hasattr(df.columns, "levels"):
        df.columns = df.columns.get_level_values(0)

    df = df[["Close"]]
    df = df.rename(columns={"Close": name})
    df = df.dropna()
    return df


def get_sp500(start, end):
    return get_market_series("^GSPC", "S&P500", start, end)


def get_btc(start, end):
    return get_market_series("BTC-USD", "BTC", start, end)