import pandas as pd
import streamlit as st


from coefficient import calculate_results
from info import calculate_info
from info import calculate_download

def results(*args, **kwargs):
    df=kwargs.get('df').copy()
    ignore_columns=kwargs.get('ignore_multiselect_columns')
    target_columns=kwargs.get('target_selectbox_columns')

    result=calculate_results(**dict(df=df, ignore_columns=ignore_columns, target_columns=target_columns))
    
    df_elements=result.get('df_elements')

    fig_number_elements=result.get('fig_number_elements')
    fig_categorical_elements=result.get('fig_categorical_elements')
    fig_date_elements=result.get('fig_date_elements')

    record_elements=result.get('record_elements')

    st.header('data', divider='rainbow')
    df_expander = st.expander("data", expanded=True)
    df_result_tabs = df_expander.tabs([element.get('name') for element in df_elements])
    for i in range(len(df_elements)):
        df_result_tabs[i].success(df_elements[i].get('name'))
        df_result_tabs[i].dataframe(df_elements[i].get('df'), use_container_width=True)


    st.header('figures', divider='rainbow')
    fig_expander = st.expander("figures", expanded=True)
    fig_result_tabs = fig_expander.tabs(['number figures', 'categorical figures', 'date figures'])

    for fig_element in fig_number_elements:
        fig_result_tabs[0].success(fig_element.get('name'))
        fig_result_tabs[0].plotly_chart(fig_element.get('fig'), use_container_width=True)

    for fig_element in fig_categorical_elements:
        fig_result_tabs[1].success(fig_element.get('name'))
        fig_result_tabs[1].plotly_chart(fig_element.get('fig'), use_container_width=True)

    for fig_element in fig_date_elements:
        fig_result_tabs[2].success(fig_element.get('name'))
        fig_result_tabs[2].plotly_chart(fig_element.get('fig'), use_container_width=True)

    st.header('record', divider='rainbow')
    df_expander = st.expander("record", expanded=True)
    record_result_tabs = df_expander.tabs([element.get('name') for element in record_elements])
    for i in range(len(record_elements)):
        record_result_tabs[i].success(record_elements[i].get('name'))
        record_result_tabs[i].write(record_elements[i].get('record'), use_container_width=True)


def application(*args, **kwargs):

    upload=None
    st.header('upload', divider='rainbow')
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
        ignore_multiselect_columns = calculate_form.multiselect("ignore_columns", columns)
        target_selectbox_columns = [calculate_form.selectbox("target_column", columns, index=len(columns)-1)]

        calculate_submitted = calculate_form.form_submit_button("calculate", use_container_width=True)
    
        if calculate_submitted:
            results(**dict(df=df, ignore_multiselect_columns=ignore_multiselect_columns, target_selectbox_columns=target_selectbox_columns))


def web(*args, **kwargs):
    calculate_info(**dict(application='coefficient_application'))
    calculate_download(**dict(template_name='template_coeficient'))
    application()

if __name__ == "__main__":
    web()