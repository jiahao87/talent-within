import streamlit as st
import base64
from streamlit_option_menu import option_menu
from streamlit_extras.app_logo import add_logo
from streamlit_extras.stylable_container import stylable_container
from annotated_text import annotated_text
import pandas as pd
import random
import requests
import ast
from pathlib import Path
from pandas.api.types import (
        is_categorical_dtype,
        is_datetime64_any_dtype,
        is_numeric_dtype,
        is_object_dtype,
    )
import os

from utils.load_config import load_config


config = load_config()

st.set_page_config(layout="wide")

add_logo("../assets/images/logo_transparent.png", height=100)

page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    background-image : url("https://unsplash.com/photos/a-white-desk-with-a-laptop-and-a-pair-of-glasses-Ahbw0cGz8Nk")
    background-size : cover
    background-color: rgba(0,0,0,0)
}

.st-emotion-cache-5drf04 {
    height: 5rem;
    max-width: 15rem;
    margin: 0rem 0rem 0rem 0rem;
    z-index: 999990;
}

[data-testid="stSidebarHeader"] {
    justify-content: center;
}



</style>
"""
st.markdown(page_bg_img,unsafe_allow_html=True)

tabs_font_css = """
<style>
div[class*="stTextArea"] label {
  font-size: 26px;
  color: red;
}

div[class*="stTextInput"] label {
  font-size: 26px;
  font-weight: 600;
}

div[class*="stNumberInput"] label {
  font-size: 26px;
  color: green;
}
.reportview-container .main .block-container {{
    padding-left: 1rem;
}}

</style>
"""

st.write(tabs_font_css, unsafe_allow_html=True)

st.logo("../assets/images/logo_transparent.png")

with st.sidebar:
    selected = option_menu(
        menu_title = "Menu",
        options = ["HR Module","Talent Marketplace"],
        default_index=0,
    )

d={}

if selected == "HR Module":
    st.title('Welcome to :blue[HR Module]')
    st.markdown("**HR Management Portal is designed to support your search of internal candidates and promote internal mobility**")
    st.image('../assets/images/process.png',width=1100)
    st.divider()
    st.markdown(" <style> div[class^='st-emotion-cache-13ln4jf ea3mdgi5'] { padding-left: 0rem; } </style> ", unsafe_allow_html=True)
    st.subheader("HR Input")
    col1, col2 = st.columns([3,2])

    with col1:
        st.markdown("######")
        st.write('Please upload JD')
        fl_upload = st.file_uploader("Upload File", type="pdf", label_visibility="collapsed")

        job_id_predefined = None
        job_title_predefined = None
        location_predefined = None

        @st.cache_resource
        def save_uploaded_file(file, filepath):
            with open(filepath, mode='wb') as w:
                w.write(file.getvalue())

        @st.cache_data
        def call_jd_extraction_endpoint(filepath):
            upload_jd_endpoint = "http://localhost:8502/extract-jd"
            response_jd_upload = requests.post(upload_jd_endpoint, json={"filepath": filepath})
            return response_jd_upload

        if fl_upload is not None:
            file_path = os.path.join(config["data"]["jd_folder"], fl_upload.name)
            save_uploaded_file(fl_upload, file_path)

            response_jd_upload = call_jd_extraction_endpoint(file_path)
            jd_extracted_json = response_jd_upload.json()
            job_id_predefined = jd_extracted_json['job_id']
            job_title_predefined = jd_extracted_json['job_title']
            location_predefined = jd_extracted_json['country']

            st.markdown("######")
            st.write('Please review/input the details below and submit for internal transfer')

            def text_field(label, input_type="text", label_visibility="hidden", **input_params):
                c1, c2 = st.columns([2,4])

                with c1:
                    st.markdown("######")
                    st.write(label)
        
                input_params.setdefault("key", label)

                with c2:
                    if input_type=="text":
                        return c2.text_input(label, label_visibility=label_visibility, **input_params)
                    else:
                        return c2.selectbox(label, label_visibility=label_visibility, **input_params)


            job_id = text_field("Job ID", value=job_id_predefined)
            job_title = text_field("Job Title", value=job_title_predefined)
            corp_title = text_field("Corporate Title", 
                                    input_type="dropdown",
                                    options= ["Analyst", "Associate", "Vice President", "Executive Director", "Managing Director"])
            h_mgr = text_field("Hiring Manager")
            loc = text_field("Location", value=location_predefined)
        

    with col2:
        if fl_upload is not None:
            st.markdown("#### Knowledge, Skills & Abilities (KSA)")
            with st.container(height=650):
                if fl_upload is not None:
                    # jd_extracted_json = {}
                    # jd_extracted_json['ksa'] = ["min 3 years of experience", "Database querying", "Oracle 19c", "MSSQL", "UNIX", "Windows", "Financial products", "FX", "Money Market", "Equity", "Derivatives", "Front-to-back operational workflows", "Different technologies", "Avaloq Certification"]
                    options = st.multiselect("Please select and edit the KSA if necessary",
                                            jd_extracted_json['ksa'],
                                            jd_extracted_json['ksa'])

    if fl_upload is not None:
        st.markdown("######")
        if st.button("Submit",type="primary"):
            jd_extracted_json['ksa_reviewed'] = options
            jd_extracted_json['job_id'] = job_id
            jd_extracted_json['job_title'] = job_title
            jd_extracted_json['corporate_title'] = corp_title
            jd_extracted_json['country'] = loc
            jd_extracted_json['hiring_manager'] = h_mgr
            if not h_mgr:
                st.warning("Please fill in hiring manager's name", icon="⚠️")
            else:
                jd_submit_endpoint = "http://localhost:8502/submit-jd"
                response_jd_submit = requests.post(jd_submit_endpoint, json=jd_extracted_json)

                talent_matching_endpoint = "http://localhost:8502/talent-matching"
                response_talent_matching = requests.post(talent_matching_endpoint, json=jd_extracted_json)
                print(jd_extracted_json)
                if response_talent_matching.ok:
                    st.info('JD Submitted Successfully. Please proceed to Talent Marketplace to view results.', icon="ℹ️")


if selected == "Talent Marketplace":
    st.title(f"Welcome to :blue[{selected}]")
    st.divider()
    st.subheader('Select your internal candidates')
    st.write('Job Description')
    jd_list_endpoint = "http://localhost:8502/list-jd"
    response_jd_json = requests.get(jd_list_endpoint).json()
    # response_jd_json = [{"job_id": "123", "job_title": "testing", "hiring_manager":"abc"}]
    options = [str(jd['job_id']) + " " + str(jd['job_title']) for jd in response_jd_json]
    hiring_manager_dict = {}
    for i, jd_dict in enumerate(response_jd_json):
        hiring_manager_dict[str(jd_dict['job_id']) + " " + jd_dict['job_title']] = jd_dict['hiring_manager']
    drp_jobtitle = st.selectbox("Job Title",options,0,)
    output_hiring_mgr = st.text_input("Hiring Manager", hiring_manager_dict[drp_jobtitle]) #Data to be fed from backend based on job title selected

    def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds a UI on top of a dataframe to let viewers filter columns
        Args:
            df (pd.DataFrame): Original dataframe
        Returns:
            pd.DataFrame: Filtered dataframe
        """
        modify = st.checkbox("Add filters")
        if not modify:
            return df
        df = df.copy()
        # Try to convert datetimes into a standard format (datetime, no timezone)
        for col in df.columns:
            if is_object_dtype(df[col]):
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass
            if is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.tz_localize(None)
        modification_container = st.container()
        with modification_container:
            to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
            for column in to_filter_columns:
                left, right = st.columns((1, 20))
                # Treat columns with < 10 unique values as categorical
                if is_categorical_dtype(df[column]) or df[column].nunique() < 2:
                    user_cat_input = right.multiselect(
                        f"Values for {column}",
                        df[column].unique(),
                        default=list(df[column].unique()),
                    )
                    df = df[df[column].isin(user_cat_input)]
                elif is_numeric_dtype(df[column]):
                    _min = float(df[column].min())
                    _max = float(df[column].max())
                    step = (_max - _min) / 100
                    user_num_input = right.slider(
                        f"Values for {column}",
                        min_value=_min,
                        max_value=_max,
                        value=(_min, _max),
                        step=step,
                    )
                    df = df[df[column].between(*user_num_input)]
                elif is_datetime64_any_dtype(df[column]):
                    user_date_input = right.date_input(
                        f"Values for {column}",
                        value=(
                            df[column].min(),
                            df[column].max(),
                        ),
                    )
                    if len(user_date_input) == 2:
                        user_date_input = tuple(map(pd.to_datetime, user_date_input))
                        start_date, end_date = user_date_input
                        df = df.loc[df[column].between(start_date, end_date)]
                else:
                    user_text_input = right.text_input(
                        f"Substring or regex in {column}",
                    )
                    if user_text_input:
                        df = df[df[column].astype(str).str.contains(user_text_input)]
        return df
    
    col1, col2 = st.columns([3,2])

    with col1:
        st.subheader('Internal profile recommendation')
        st.write('Shortlist the candidate for hiring manager review')

        st.session_state.df = []
        talent_results_endpoint = "http://localhost:8502/talent-results"
        response_talent_results = requests.get(talent_results_endpoint, params={"id": drp_jobtitle.split(" ")[0]}).json()
        # response_talent_results = [{"firstName": "hello", "lastName": "world", "serialNum":"321", "location": "SG", "corporateTitle":"analyst", "score":0.8999, "ksa": "['python', '3 years of experience', 'NLP']"},
        #                            {"firstName": "world", "lastName": "hello", "serialNum":"321", "location": "SG", "corporateTitle":"analyst", "score":0.7999, "ksa": "['perl', '5 years of experience', 'NLP']"}]
        talent_results_df = pd.DataFrame(response_talent_results)
        if len(talent_results_df)>0:
            talent_results_df.sort_values(by="score", ascending=False, inplace=True)
            talent_results_df['Score %'] = (pd.to_numeric(talent_results_df['score']) * 100).astype(int)
            talent_results_df['Candidate Name'] = talent_results_df['First Name'] + " " + talent_results_df['Last Name']
            talent_results_df.rename(columns={'Serial Number':"Employee ID", "Global Corporate Title": "Corp Title", "Country": "Location"}, inplace=True)
            st.session_state.df = talent_results_df

            event = st.dataframe(
                filter_dataframe(st.session_state.df[["Employee ID", "Candidate Name", "Location", "Corp Title", "Score %"]]),
                column_config={
                    "Employee ID": "Employee ID",
                    "Candidate Name": "Candidate Name",
                    "Location": "Location",
                    "Corp Title": "Corp Title",
                    "Score %": "Score %",
                },
                hide_index=True,
                key="data",
                on_select="rerun",
                selection_mode=["single-row"],
                use_container_width=True
            )
            
            selected_row = event.selection.rows
        else:
            selected_row = None

        if not selected_row and len(st.session_state.df)>0:
            selected_row = [0]
    
    with col2:
        if selected_row:

            st.markdown(
                        """
                    <style>
                    [data-testid="baseButton-primary"] {
                        height: auto;
                        width: 400px;
                        padding-top: 10px !important;
                        padding-bottom: 10px !important;
                    }
                    </style>
                    """,
                        unsafe_allow_html=True,
            )
            with stylable_container(
                key="container_with_border",
                css_styles="""
                    {
                        border: 1px solid rgba(49, 51, 63, 0.2);
                        border-radius: 0.5rem;
                        padding: calc(1em - 1px);
                        background-color: #d4d4d4;
                        height: 240px
                    }
                    """,
            ):
                st.subheader(":red[Candidate KSA]")
                st.markdown(f"### {st.session_state.df.iloc[selected_row]['Candidate Name'].values[0]}")

                candidate_info_endpoint = "http://localhost:8502/candidate-info"
                response_candidate_cv = requests.get(candidate_info_endpoint, params={"id": st.session_state.df.iloc[selected_row]['Employee ID'].values[0]})
                file = response_candidate_cv.content
                # file = ""
                st.download_button("Download CV", file, file_name=st.session_state.df.iloc[selected_row]['Candidate Name'].values[0]+".pdf", mime="application/pdf")
                st.divider()
                container_col1, container_col2 = st.columns([15, 1])
                container_col1.multiselect("",
                            ast.literal_eval(st.session_state.df.iloc[selected_row]["ksa"].values[0]),
                            ast.literal_eval(st.session_state.df.iloc[selected_row]["ksa"].values[0]))
                st.markdown("#")
                st.write("Send shortlisted candidate to manager")
                st.button("Submit", type="primary")
