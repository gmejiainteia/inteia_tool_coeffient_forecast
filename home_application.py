import pandas as pd
import streamlit as st

from coefficient import calculate_results
from info import calculate_info
from info import calculate_download

def web(*args, **kwargs):
    calculate_info(**dict(application='default'))

if __name__ == "__main__":
    web()