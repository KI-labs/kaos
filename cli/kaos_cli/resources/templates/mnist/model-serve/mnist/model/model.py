#!/usr/bin/env python3
from __future__ import print_function

import joblib
from skimage.transform import resize
from PIL import Image
import numpy as np
from io import BytesIO
from skimage.filters import threshold_otsu
import pandas as pd


def predict(obj, ctx):
    """
    A prediction function.

    Args:
        obj (bytearray): a list of object (or a single object) to predict on
        ctx (dict): a model training context

    Returns:
        a list with predictions

    """
    binary_image = Image.open(BytesIO(obj)).convert('L')
    img = resize(np.array(binary_image), (28, 28), preserve_range=True)
    threshold = threshold_otsu(img)
    img_colors_inverted = list(map(lambda el: 0 if el > threshold else int(255 - el), img.flatten()))
    img_transformed = ctx['scaler'].transform([img_colors_inverted])
    df = pd.DataFrame(img_transformed)  # convert to DataFrame (pandas)
    return ctx['model'].predict(df).tolist()


def load_ctx(model_path):
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
