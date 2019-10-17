#!/usr/bin/env python3

import joblib
import pandas as pd


def predict(obj, model_ctx):
    """
    A prediction function.

    Args:
        obj (dict): a list of object (or a single object) to predict on
        model_ctx (dict): a model training context

    Returns:
        a list with predictions

    """
    print("MODEL -> {}".format(model_ctx))
    df = pd.DataFrame(obj, index=[0])  # convert to DataFrame (pandas)
    return model_ctx.predict(df).tolist()


def load_model(model_path):
    """
    Function for loading the trained model based on ENV

    Args:
        model_path (str): (necessary for predict)

    Returns:
        model (object): a loaded model

    """

    # define health as whether the model can be loaded
    model = joblib.load(model_path)

    return model
