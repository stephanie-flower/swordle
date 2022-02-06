import pandas as pd


def get_words(path: str) -> pd.DataFrame:
    return pd.read_csv(path)
