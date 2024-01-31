from st_pages import Page
from st_pages import show_pages
from st_pages import add_page_title 

import streamlit as st

add_page_title(Page("home_application.py", "home", "🚀"))


show_pages(
    [   
        Page("coefficient_application.py", "coeffient", "🚀"),
        Page("forecast_application.py", "forecast", "🚀"),
    ]
)