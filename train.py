import os
import texthero as hero
import dask
import dask.dataframe as dd

import ray
from ray.util.dask import ray_dask_get

from local_module import (
    load_data_from_file,
    clean_content,
    tune_model
)

dask.config.set(scheduler=ray_dask_get)

@ray.remote
def load_and_preprocess(path: str) -> dd.DataFrame:
    try:
        df = load_data_from_file(path, npartitions=10)
    except Exception as e:
        print(f"!!! Error !!! {e}")
        ray.util.pdb.set_trace()
    df = clean_content(df)
    df["tfidf"] = hero.tfidf(df["full_content"])
    df["value"] = hero.pca(df["tfidf"], n_components=50)
    print("Summary of data labels:")
    print(df.label.value_counts())
    return df


def main(num_trials: int = 1):
    ray.client().connect()

    # Load data, preprocess, put into shared memory.
    data_path = "training_data.pkl"
    preprocessed_ref = load_and_preprocess.remote(data_path)

    # Train the model `num_trials` times to find the best one.
    tune_model(
        preprocessed_ref,
        num_trials=num_trials,
        s3_bucket="intent-classifier"
    )


if __name__ == "__main__":
    import typer
    typer.run(main)
