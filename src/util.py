import pandas as pd


def handle_tcg_csv(filename, unwanted_cols=None, rename_cols=None):
    if unwanted_cols is None:
        unwanted_cols=['Name']
    if rename_cols is None:
        rename_cols={'Simple Name': 'Name',
                     'Quantity': 'Count'}
    df = pd.read_csv(filename)
    handled_df = df.drop(unwanted_cols, axis=1).rename(index=str,
                                                       columns=rename_cols)
    return handled_df
