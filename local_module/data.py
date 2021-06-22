import pickle

import dask.dataframe as dd

import pandas as pd

def clean_content(df: pd.DataFrame) -> pd.DataFrame:
    import texthero as hero
    df["title"] = df["title"].pipe(hero.clean)
    df["content"] = df["content"].pipe(hero.clean)
    df["full_content"] = df["title"] + " " + df["content"]
    return df.drop(columns=["title", "content"])

def load_data_from_file(path: str, npartitions: int = 20) -> dd.DataFrame:
    with open(path, "rb") as f:
        data = list(pickle.load(f))
    return dd.from_pandas(pd.DataFrame([vars(schema) for schema in data]), npartitions=npartitions)
