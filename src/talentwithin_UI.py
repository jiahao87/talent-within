import streamlit as st
import base64
from streamlit_option_menu import option_menu
from streamlit_extras.app_logo import add_logo
from streamlit_extras.stylable_container import stylable_container
from annotated_text import annotated_text
import pandas as pd
import random
import requests


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

        if fl_upload is not None:
            upload_jd_endpoint = "http://localhost:8080/integrationservice/jd-upload"
            files = [("file", (fl_upload.name, fl_upload.getvalue(), 'application/pdf'))]
            response_jd_upload = requests.request("POST", upload_jd_endpoint, files=files)
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
            jd_submit_endpoint = "http://localhost:8080/integrationservice/jd-submit"
            # response_jd_submit = requests.request("POST", jd_submit_endpoint, data=jd_extracted_json)
            response_jd_submit = requests.post(jd_submit_endpoint, json=jd_extracted_json)
            print(jd_extracted_json)
            if response_jd_submit.ok:
                st.info('JD Submitted Successfully. Please proceed to Talent Marketplace to view results.', icon="ℹ️")


if selected == "Talent Marketplace":
    st.title(f"Welcome to :blue[{selected}]")
    st.divider()
    st.subheader('Select your internal candidates')
    st.write('Job Description')
    jd_list_endpoint = "http://localhost:8080/integrationservice/jd-list"
    response_jd_json = requests.get(jd_list_endpoint).json()
    options = [str(jd['id']) + " " + str(jd['jobTitle']) for jd in response_jd_json]
    hiring_manager_dict = {}
    for i, jd_dict in enumerate(response_jd_json):
        hiring_manager_dict[str(jd_dict['id']) + " " + jd_dict['jobTitle']] = jd_dict['hiringManager']
    drp_jobtitle = st.selectbox("Job Title",options,0,)
    output_hiring_mgr = st.text_input("Hiring Manager", hiring_manager_dict[drp_jobtitle], disabled=True) #Data to be fed from backend based on job title selected

    col1, col2 = st.columns([3,2])

    with col1:
        st.subheader('Internal profile recommendation')
        st.write('Shortlist the candidate for hiring manager review')

        if "df" not in st.session_state:
            talent_results_endpoint = "http://localhost:8080/integrationservice/talent-results"
            response_talent_results = requests.get(talent_results_endpoint, params={"job-id": drp_jobtitle.split(" ")[0]}).json()
            talent_results_df = pd.DataFrame(response_talent_results)
            talent_results_df['name'] = talent_results_df['firstName'] + talent_results_df['lastName']
            st.session_state.df = talent_results_df
            # st.session_state.df = pd.DataFrame(
            #     {
            #         "employee_id": response_talent_results['Serial Number'],
            #         "name": [str(m) + str(n) for m,n in zip(response_talent_results['First Name'], response_talent_results['Last Name'])],
            #         "location": response_talent_results['Country'],
            #         "title" : response_talent_results['Global Corporate Title'],
            #         "percentage": response_talent_results['score'],
            #     }
            # )

        event = st.dataframe(
            st.session_state.df[["serialNum", "name", "location", "corporateTitle", "score"]],
            column_config={
                "serialNum": "Employee ID",
                "name": "Candidate Name",
                "location": "Location",
                "corporateTitle": "Corp Title",
                "score": "Score",
            },
            hide_index=True,
            key="data",
            on_select="rerun",
            selection_mode=["multi-row", "multi-column"],
            width=500
        )
        
        selected_row = event.selection.rows
        candidate_id  = st.session_state.df.iloc[selected_row]["serialNum"]
    
    with col2:
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
            
            st.write(st.session_state.df.iloc[selected_row]["name"].values)
            st.divider()
            print("ksa type : ", type(st.session_state.df.iloc[selected_row]["ksa"]))
            print("ksa list : ", st.session_state.df.iloc[selected_row]["ksa"])
            st.multiselect("",
                           st.session_state.df.iloc[selected_row]["ksa"].to_list(),
                           st.session_state.df.iloc[selected_row]["ksa"].to_list(), 
                           disabled=True)
            st.markdown("#")
            st.write("Send shortlisted candidate to manager")
            st.button("Submit", type="primary")
