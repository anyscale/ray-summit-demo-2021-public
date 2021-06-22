from dataclasses import dataclass
import logging
import os
from typing import Iterable

import numpy as np
import pandas as pd
import xgboost as xgb
import xgboost_ray as xgbr

import sklearn
from sklearn import preprocessing
from sklearn.model_selection import train_test_split

from local_module.interfaces import Data

import ray
from ray import tune

# DMatrix = xgb.DMatrix
DMatrix = xgbr.RayDMatrix

# Silence annoying warnings.
logging.getLogger("ray.tune").setLevel("ERROR")


def create_dmatrix(data):
    values, labels = zip(*((d.x, d.label) for d in data))
    le = preprocessing.LabelEncoder()
    le.fit(labels)

    labels = le.transform(labels)
    X_train, X_test, y_train, y_test = train_test_split(
        values, labels, stratify=labels, train_size=0.9, test_size=0.1
    )

    train_set = DMatrix(np.array(X_train), np.array(y_train))
    test_set = DMatrix(np.array(X_test), np.array(y_test))
    return train_set, test_set, len(le.classes_)


def tune_model(df_ref, num_trials=5, s3_bucket=None):
    ray.wait([df_ref])
    ray_params = xgbr.RayParams(
        max_actor_restarts=1, gpus_per_actor=0, cpus_per_actor=2, num_actors=2
    )

    def tune_xgb(config, ray_params=None, train_set=None, test_set=None):
        df = ray.get(df_ref)
        data = [Data(row["value"], row["label"]) for i, row in df.iterrows()]
        train_set, test_set, num_classes = create_dmatrix(data)

        evals_result = {}
        bst = xgbr.train(
            {
                "objective": "multi:softmax",
                "eval_metric": ["mlogloss", "merror"],
                "num_class": num_classes,
            },
            train_set,
            evals_result=evals_result,
            evals=[(train_set, "train"), (test_set, "eval")],
            verbose_eval=False,
            ray_params=ray_params,
        )
        bst.save_model("tuned.xgb")

    analysis = tune.run(
        tune.with_parameters(
            tune_xgb, ray_params=ray_params
        ),
        # Use the `get_tune_resources` helper function to set the resources.
        resources_per_trial=ray_params.get_tune_resources(),
        config={
            "eta": tune.loguniform(1e-4, 1e-1),
            "subsample": tune.uniform(0.5, 1.0),
            "max_depth": tune.randint(1, 20),
        },
        verbose=1,
        log_to_file=True,
        num_samples=num_trials,
        metric="eval-merror",
        mode="min",
        fail_fast="raise",
        sync_config=tune.SyncConfig(sync_to_driver=False)
    )

    accuracy = 1.0 - analysis.best_result["eval-merror"]
    print(f"Best model parameters: {analysis.best_config}")
    print(f"Best model total accuracy: {accuracy:.4f}")
