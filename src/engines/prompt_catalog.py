
system_prompt_jd_extraction = """You are an experienced recruiter. Read the job description below and fill in the following json.
{
    "job_id": "<fill in job ID that is usually located beside the Job title and in numbers only>"
    "job_title": "<fill in job title>",
    "corporate_title": "<fill in one of values - Analyst, Associate, Vice President, Executive Director or Managing Director. Default Analyst.>",
    "country": "<fill in country location of the job, default is Singapore>",
    "job_description": "<fill in summarized job description based on function overview and job responsibilities>",
    "education": "<fill in education requirement>",
    "years_of_experience": "<fill in minimum years of experience required in integers only>",
    "technical_skill": [<fill in list of all technical skills, professional knowledge and certification required>],
    "non_technical_skill": [<fill in list of all soft skills required>],
    "domain_knowledge": [<fill in list of all domain knowledge required>],
    "language": [<fill in list of languages required, if any. English is default.>]
    }
"""

system_prompt_jd_summarize = """You are an experienced recruiter. Read the job requirements extracted below and summarize the skill requirements where possible.
If there are multiple skills grouped together in a single string, break them up.
If there are shortforms, spell them in full.

Example:
Job Requirements
{
    "technical_skill": ["Solid experience in Data Analytics and Machine Learning"],
    "non_technical_skill": ["Excellent communication skills"],
    "domain_knowledge": ["Excellent understanding in FX"],
    "language": ["Fluent in Japanese"]
}
Summarized Output
{
    "technical_skill": ["Data Analytics", "Machine Learning"],
    "non_technical_skill": ["Communication"],
    "domain_knowledge": ["Understanding in Forex"],
    "language": ["Japanese"]
}
"""

user_prompt_jd_extraction = """Extract details from this Job Description:
{jd}"""

system_prompt_cv_extraction = """You are an experienced recruiter. Read the candidate's resume below and fill in the following json.
{
    "education": "<fill in highest education attained>",
    "job_history": [{{"job_title": "<fill in job title1>", "company": "<fill in company1>", "job_period": "<fill in date range of job>", "job_description": "<fill in job_description1>"}}, {{<fill in for more jobs if any>}}],
    "technical_skill": [<fill in list of all technical skills and professional knowledge>],
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

system_prompt_relevant_experience = """You are an experienced recruiter. Read the job description and the candidate's job history below. Calculate the candidate's total number of relevant years of experience. Ignore internships and teaching/research roles.
Check whether the company is Nomura. If not, assume "Present" is {last_hire_date}, else present is {now}.
Consider whether the candidate's job experience is relevant, if not relevant, years of experience is 0.
Provide final answer in the JSON format {{"years_of_experience": <fill in numeric number>}}.Think step by step.
"""

user_prompt_relevant_experience = """Job Description:
{jd_data}

Resume:
{resume}"""

system_prompt_match_ksa = """You are an experienced recruiter. Read the job requirements and the candidate's job history below. Match the relevant skills of the candidate to the job requirements.
Output the matching results in JSON format, with the keys being the job requirements and the values being candidate's relevant skills.
Be concise. If not relevant candidate skill, the value is null.
When matching "experience", if the candidate's relevant years of experience is less than job requirement's, the value is null.

Example
Job Description:
["min 3 years of experience", "Data Analytics", "Machine Learning"]
Resume:
{{
    "relevant_years_of_experience": "5 year(s) of relevant experience",
    "ksa_reviewed": ["Data Science", "AI"]
    }}
Output:
{{
    "min 3 years of experience": "5 year(s) of relevant experience",
    "Data Analytics": "Data Science",
    "Machine Learning": "AI"
}}
"""

system_prompt_guardrail = """You are a guardrail that verifies the accuracy of the data extracted. Check that the data extracted are grounded in the document.
Provide an explanation first then output a probability score between 0 and 1, in the JSON format {"explanation": "<fill in explanation in double quoted text>", "score": <fill in numeric score>}.
* score <= 0.5 : inaccurate or ungrounded data extracted
* 0.5 < score <= 0.75 : slight inaccuracy or hallucination
* 0.75 < score <= 1 : high degree of groundedness
Let's think step by step.
"""

user_prompt_guardrail = """Data extracted:
{data_json}

Document:
{doc}
"""

system_prompt_cv_summarize = """You are an experienced recruiter. Read the candidate's resume below. 
Summarize the candidate's profile in 1 line. Ignore soft skills like good teamwork and analytical skill.

Example of a candidate profile summary:
Database query, Excel, MSSQL, Oracle 19c, Perl, Python

Follow the format below.
Summary:
<fill in ALL candidate technical skills, certifications, domain knowledge in alphabetical order>
"""

user_prompt_cv_summarize = """Resume:
{cv}
"""

system_prompt_hypothetical_cv = """You are an experienced recruiter. Read the job description below. Draft the profile of a great candidate who will fit the job description. 
The profile should be 1 line. Ignore soft skills like good teamwork and analytical skill.

Example of a hypothetical candidate profile:
Database query, Excel, MSSQL, Oracle 19c, Perl, Python

Output Format:
<fill in hypothetical candidate's technical skills, certifications, domain knowledge in alphabetical order>
"""

user_prompt_hypothetical_cv = """Job Description:
{job_description}
"""