"""
Module with convenience helper functions
"""

import pandas as pd


def sorted_list_of_unique_elements(x: list | pd.Series):
    if isinstance(x, list):
        s = pd.Series(x)
    elif isinstance(x, pd.Series):
        s = x
    else:
        raise TypeError("Input must be list or pandas.Series")
    return list(s.sort_values().unique())
