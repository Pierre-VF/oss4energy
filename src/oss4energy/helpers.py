"""
Module with convenience helper functions
"""

import pandas as pd


def sorted_list_of_unique_elements(x: list):
    return list(pd.Series(x).sort_values().unique())
