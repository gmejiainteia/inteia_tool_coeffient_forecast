import streamlit as st

import os
import json
import markdown

from PIL import Image

def calculate_info(*args, **kwargs):
    application=kwargs.get('application')

    file_path = os.path.join('data',f'{application}.json')
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    page_icon=data.get('page_icon')
    page_title=data.get('page_title')
    application_name=data.get('application_name')
    title=data.get('title')
    enterprise=data.get('enterprise')
    version=data.get('version')

    st.set_page_config(layout='wide', page_icon=page_icon, page_title=page_title, initial_sidebar_state="expanded")
    file_path=os.path.join('img','LOGO.png')
    logo_image = Image.open(file_path)
    st.sidebar.image(logo_image, use_column_width=True)

    st.sidebar.caption(f"enterprise: {enterprise}")
    st.sidebar.caption(f"aplicacion: {application_name}")
    st.sidebar.caption(f"version: {version}")

    st.title(title)

    file_path = os.path.join('data',f'{application}.md')
    with open(file_path, "r", encoding="utf-8") as file:
        data = file.read()

    st.header(f'DOCUMENTATION {application_name}', divider='rainbow')
    documentation_expander = st.expander("documentation", expanded=False)
    documentation_expander.markdown(markdown.markdown(data), unsafe_allow_html=True)


def calculate_download(*args,**kwargs):
    template_name=kwargs.get('template_name')

    file_path=os.path.join('data',f'{template_name}.xlsx')
    with open(file_path, "rb") as template_file:
        template = template_file.read()

    st.header('DOWNLOAD', divider='rainbow')
    template_expander = st.expander("template", expanded=True)
    template_expander.download_button(label="Download Template", data=template, file_name=f"{template_name}.xlsx", mime='application/octet-stream', use_container_width=True)

if __name__ == '__main__':
    calculate_download(**dict(template_name='template_forecast'))