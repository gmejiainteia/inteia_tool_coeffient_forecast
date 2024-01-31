
import pandas as pd
import streamlit as st

from forecast import calculate_template
from forecast import calculate_results
from info import calculate_info
from info import calculate_download

def results(*args, **kwargs):
    df=kwargs.get('df').copy()
    date_hour_column=kwargs.get('date_hour_column')
    value_column=kwargs.get('value_column')

    columns=[date_hour_column, value_column]
    df=df[columns]
    
    df.rename(columns={'date_hour_column': 'date_hour', 'value_column': 'value'}, inplace=True)

    result = calculate_results(**dict(df=df))

    fig_elements=result.get('fig_elements')
    df_elements=result.get('df_elements')

    st.header('figures', divider='rainbow')
    fig_expander = st.expander("figures", expanded=True)
    fig_result_tabs = fig_expander.tabs([element.get('name') for element in fig_elements])

    for i in range(len(fig_elements)):
        fig_result_tabs[i].success(fig_elements[i].get('name'))
        fig_result_tabs[i].plotly_chart(fig_elements[i].get('fig'), use_container_width=True)


    st.header('data', divider='rainbow')
    df_expander = st.expander("data", expanded=True)
    df_result_tabs = df_expander.tabs([element.get('name') for element in df_elements])
    for i in range(len(df_elements)):
        df_result_tabs[i].success(df_elements[i].get('name'))
        df_result_tabs[i].dataframe(df_elements[i].get('df'), use_container_width=True)


def application(*args, **kwargs):

    upload=None
    st.header('UPLOAD', divider='rainbow')
    upload_expander = st.expander("upload data", expanded=True)
    uploaded_file = upload_expander.file_uploader("Upload Excel", type=["xls", "xlsx"])
    
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)

        upload_expander.dataframe(df, use_container_width=True)
        upload=True

    if upload is not None:
        st.header('form', divider='rainbow')
        calculate_form=st.form("calculate_form")

        columns = df.columns
        date_hour_column = calculate_form.selectbox("date hour column", columns, index=0)
        value_column = calculate_form.selectbox("value column", columns, index=1)

        calculate_submitted = calculate_form.form_submit_button("calculate", use_container_width=True)
    
        if calculate_submitted:
            results(**dict(df=df, date_hour_column=date_hour_column, value_column=value_column))


def web(*args, **kwargs):
    calculate_info(**dict(application='forecast_application'))
    calculate_download(**dict(template_name='template_forecast'))
    application()

if __name__ == "__main__":
    web()