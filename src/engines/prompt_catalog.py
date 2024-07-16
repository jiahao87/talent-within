
system_prompt_jd_extraction = """You are an experienced recruiter. Read the job description below and fill in the following json.
{
    "job_id": "<fill in job ID that is usually located beside the Job title and in numbers only>"
    "job_title": "<fill in job title>",
    "corporate_title": "<fill in one of values - Analyst, Associate, Vice President, Executive Director or Managing Director. Default Analyst.>",
    "job_description": "<fill in summarized job description based on function overview and job responsibilities>",
    "education": "<fill in education requirement>",
    "years_of_experience": "<fill in minimum years of experience required in integers only>",
    "technical_skill": [<fill in list of all technical skills, professional knowledge and certification required>],
    "non_technical_skill": [<fill in list of all soft skills required>],
    "domain_knowledge": [<fill in list of all domain knowledge required>],
    "language": [<fill in list of languages required, if any. English is default.>]
    }
"""

user_prompt_jd_extraction = """Extract details from this Job Description:
{jd}"""

system_prompt_cv_extraction = """You are an experienced recruiter. Read the candidate's resume below and fill in the following json.
{
    "education": "<fill in highest education attained>",
    "job_history": [{{"job_title": "<fill in job title1>", "company": "<fill in company1>", "job_period": "<fill in date range of job>", "job_description": "<fill in job_description1>"}}, {{<fill in for more jobs if any>}}],
    "certification": [<fill in list of all certification obtained>],
    "language": [<fill in list of proficient languages, if any>]
    }
"""

user_prompt_cv_extraction = """Extract details from this Resume:
{cv}
"""

system_prompt_cv_experience = """You are an experienced recruiter. Read the candidate's job history below. Calculate the candidate's total number years of experience. Ignore internships and teaching/research roles. 
Check whether the company is Nomura. If not, assume "Present" is {last_hire_date}, else present is {now}. Provide final answer in the format {{"years_of_experience": }}.Think step by step.
"""

user_prompt_cv_experience = """Job history:
{{
      "job_title": "Analyst",
      "company": "Nomura",
      "job_period": "{last_hire_date} - Present"
      }}
{job_history}
"""

# prompt_cv_experience = """You are an experienced recruiter. Read the job description and the candidate's job history below. Calculate the candidate's total number of relevant years of experience. 
# Assume "Present" is {now}. Provide final answer in the format {{"years_of_experience": }}.Think step by step.
# Job Description:
# {jd_data}

# Resume:
# {job_history}
# """