import numpy as np
import pandas as pd
from sklearn import metrics
import os
import tarfile


def prepare_dataframe(dataset_path, label_column):
    df = load_data(dataset_path)

    # Since the data and target values are in the same file, let's split them into separate dataframes
    return split_by_column(df, label_column)


def create_metrics(predictions, labels, dataset):
    # Generating metrices (precision, recall, f1 score,...)
    metrics_matrix = metrics.classification_report(flatten_one_element_df_array(labels), predictions)

    # Generating TP(true positive) and TN(true negative) prediction for accuracy calculation
    true_prediction = predictions == flatten_one_element_df_array(labels)

    # Saving metrices
    counts = np.unique(true_prediction, return_counts=True)[1]

    # If all the prediction are correct then we have only count for True,
    # if there are some wrong predictions the count for correct is in the second element
    accuracy = (counts[0] if len(counts) == 1 else counts[1]) / float(len(labels))

    return {
        f"accuracy_{dataset}": accuracy,
        f"metrics_{dataset}": metrics_matrix
    }


def split_by_column(df, column):
    return df.iloc[:, :column], df.iloc[:, column:]


def load_data(path):
    tars = [f for f in os.listdir(path) if f.endswith('.tar.gz')]
    for tar in tars:
        tar_file = tarfile.open(os.path.join(path, tar), 'r:gz')
        tar_file.extractall(path)
        tar_file.close()

    fids = [f for f in os.listdir(path) if f.endswith('.csv')]

    dfs = []
    for fid in fids:
        temp_df = pd.read_csv(os.path.join(path, fid), index_col=False, header=None, engine='python')
        dfs.append(temp_df)
    return pd.concat(dfs, axis=0, ignore_index=True)


def flatten_one_element_df_array(array):
    return np.array([el[0] for el in array.values])
