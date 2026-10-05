import streamlit as st
from pypdf import PdfReader
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import os


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Placement & Mock Interview App",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ AI-Driven Placement & Interview Evaluation Hub")

st.markdown(
    "Scan resumes against standard applicant models, "
    "run mock test loops, and view complete analytics."
)


# ============================================================
# GROQ MODEL CONFIGURATION
# ============================================================

# Keep the model name in ONE place.
# If Groq changes models later, only change this line.
GROQ_MODEL = "openai/gpt-oss-120b"


# ============================================================
# SESSION STATE
# ============================================================

if "interview_question" not in st.session_state:
    st.session_state.interview_question = ""

if "target_role" not in st.session_state:
    st.session_state.target_role = ""


# ============================================================
# SIDEBAR CONFIGURATION
# ============================================================

st.sidebar.title("🧭 Configuration & Navigation")

user_groq_key = st.sidebar.text_input(
    "Enter Groq API Key:",
    type="password",
    help="Enter your GroqCloud API key."
)

if user_groq_key:
    os.environ["GROQ_API_KEY"] = user_groq_key


app_mode = st.sidebar.radio(
    "Go to Module:",
    [
        "ATS Screening",
        "Interactive Mock Loop"
    ]
)


if not user_groq_key:
    st.warning(
        "🔑 Please enter your Groq API Key in the left sidebar "
        "configuration panel to unlock system modules."
    )


# ============================================================
# HELPER FUNCTION — PDF READER
# ============================================================

def parse_resume_document(file_buffer):

    pdf_reader = PdfReader(file_buffer)

    extracted_raw_text = ""

    for target_page in pdf_reader.pages:

        page_text = target_page.extract_text()

        if page_text:
            extracted_raw_text += page_text + "\n"

    return extracted_raw_text


# ============================================================
# HELPER FUNCTION — CREATE GROQ MODEL
# ============================================================

def create_llm(temperature=0.2):

    return ChatGroq(
        model=GROQ_MODEL,
        api_key=user_groq_key,
        temperature=temperature
    )


# ============================================================
# MODULE 1 — ATS SCREENING
# ============================================================

if app_mode == "ATS Screening":

    st.header("📄 Automated Applicant Profile Matcher")

    st.caption(
        "Upload your resume and the target job description "
        "to evaluate your profile alignment."
    )


    col1, col2 = st.columns(2)


    with col1:

        uploaded_pdf = st.file_uploader(
            "Upload Profile Document (PDF Format Only)",
            type=["pdf"]
        )


    with col2:

        job_details = st.text_area(
            "Paste Target Job Description Requirement Matrix:",
            height=200
        )


    # --------------------------------------------------------
    # ATS ANALYSIS BUTTON
    # --------------------------------------------------------

    if st.button("🔍 Execute ATS Matrix Alignment Analysis"):

        if not user_groq_key:

            st.error(
                "❌ Action Blocked: Provide a valid Groq API Key "
                "in the sidebar first."
            )


        elif not uploaded_pdf or not job_details:

            st.error(
                "❌ Action Blocked: Upload your resume and "
                "paste the job description."
            )


        else:

            with st.spinner(
                "Parsing resume and executing AI analysis..."
            ):

                try:

                    # -----------------------------------------
                    # Extract Resume
                    # -----------------------------------------

                    resume_parsed_text = parse_resume_document(
                        uploaded_pdf
                    )


                    if not resume_parsed_text.strip():

                        st.error(
                            "❌ No readable text could be extracted "
                            "from this PDF."
                        )

                        st.stop()


                    # -----------------------------------------
                    # LLM
                    # -----------------------------------------

                    strict_llm = create_llm(
                        temperature=0.1
                    )


                    # -----------------------------------------
                    # ATS PROMPT
                    # -----------------------------------------

                    ats_prompt = ChatPromptTemplate.from_messages(
                        [

                            (
                                "system",

                                """
You are an expert technical recruiter.

Analyze the candidate's resume against the provided
job description.

Return ONLY valid JSON.

The JSON must contain exactly these keys:

"match_score":
An integer between 0 and 100.

"missing_tech_keywords":
A string containing the important technical skills,
technologies, qualifications, or keywords required
by the job description but missing from the resume.

"resume_reconstruction_advice":
A string containing concise recommendations explaining
how the candidate can improve the resume for this role.

Do not include Markdown formatting.
Do not include text outside the JSON object.
"""
                            ),

                            (
                                "human",

                                """
RESUME CONTENT:

{resume}


JOB REQUIREMENTS:

{jd}
"""
                            )

                        ]
                    )


                    # -----------------------------------------
                    # BUILD CHAIN
                    # -----------------------------------------

                    eval_chain = (
                        ats_prompt
                        | strict_llm
                        | JsonOutputParser()
                    )


                    # -----------------------------------------
                    # CALL GROQ
                    # -----------------------------------------

                    analysis_payload = eval_chain.invoke(
                        {
                            "resume": resume_parsed_text,
                            "jd": job_details
                        }
                    )


                    # -----------------------------------------
                    # DISPLAY RESULT
                    # -----------------------------------------

                    st.success(
                        "✅ Analysis Execution Complete"
                    )


                    st.metric(
                        label="Calculated ATS System Alignment Match",
                        value=f"{analysis_payload.get('match_score', 0)}%"
                    )


                    st.subheader(
                        "❌ Detected Keyword Skill Gaps"
                    )

                    st.write(
                        analysis_payload.get(
                            "missing_tech_keywords",
                            "No data returned."
                        )
                    )


                    st.subheader(
                        "💡 Strategic Profile Optimization Tips"
                    )

                    st.write(
                        analysis_payload.get(
                            "resume_reconstruction_advice",
                            "No advice returned."
                        )
                    )


                except Exception as e:

                    st.error(
                        f"⚠️ Infrastructure Engine Error: {str(e)}"
                    )


# ============================================================
# MODULE 2 — INTERACTIVE MOCK INTERVIEW
# ============================================================

elif app_mode == "Interactive Mock Loop":

    st.header(
        "🤖 Adaptive Domain Technical Interview Core"
    )

    st.caption(
        "Select your target role and type your answer "
        "to receive AI-based grading."
    )


    # --------------------------------------------------------
    # ROLE INPUT
    # --------------------------------------------------------

    role_input = st.text_input(

        "Enter Target Professional Sub-Domain:",

        value=st.session_state.target_role,

        placeholder=(
            "e.g., Backend Developer, "
            "Data Analyst Intern, "
            "Software Developer"
        )
    )


    # --------------------------------------------------------
    # GENERATE INTERVIEW QUESTION
    # --------------------------------------------------------

    if st.button(
        "🎲 Generate Technical Interview Prompt"
    ):

        if not user_groq_key:

            st.error(
                "❌ Action Blocked: Provide a valid "
                "Groq API Key first."
            )


        elif not role_input.strip():

            st.error(
                "❌ Missing Field: Please enter "
                "a target role first."
            )


        else:

            st.session_state.target_role = (
                role_input.strip()
            )


            with st.spinner(
                "Generating interview question..."
            ):

                try:

                    # -----------------------------------------
                    # LLM
                    # -----------------------------------------

                    creative_llm = create_llm(
                        temperature=0.7
                    )


                    # -----------------------------------------
                    # QUESTION PROMPT
                    # -----------------------------------------

                    q_prompt = (
                        ChatPromptTemplate.from_messages(
                            [

                                (
                                    "system",

                                    """
You are an expert technical interviewer
specializing in {role} interviews.

Generate ONE challenging and highly relevant
technical, conceptual, coding, system-design,
or situational interview question appropriate
for a candidate applying for a {role} position.

The question should test practical understanding,
not just memorization.

Do not provide the answer.

Do not include greetings.

Do not include introductory text.

Output ONLY the interview question.
"""
                                ),

                                (
                                    "human",

                                    "Generate the interview question now."
                                )

                            ]
                        )
                    )


                    # -----------------------------------------
                    # CHAIN
                    # -----------------------------------------

                    question_chain = (
                        q_prompt
                        | creative_llm
                    )


                    # -----------------------------------------
                    # GENERATE QUESTION
                    # -----------------------------------------

                    question_result = (
                        question_chain.invoke(
                            {
                                "role":
                                st.session_state.target_role
                            }
                        )
                    )


                    st.session_state.interview_question = (
                        question_result.content
                    )


                except Exception as e:

                    st.error(
                        f"⚠️ Infrastructure Engine Error: {str(e)}"
                    )


    # ========================================================
    # DISPLAY INTERVIEW QUESTION
    # ========================================================

    if st.session_state.interview_question:

        st.info(

            f"""
### ❓ Question Context for {st.session_state.target_role}

{st.session_state.interview_question}
"""
        )


        candidate_response = st.text_area(

            "Type your comprehensive solution response below:",

            height=180
        )


        # ----------------------------------------------------
        # SUBMIT ANSWER
        # ----------------------------------------------------

        if st.button(
            "📊 Submit Response for Evaluation Grading"
        ):

            if not user_groq_key:

                st.error(
                    "❌ Action Blocked: Provide a valid "
                    "Groq API Key first."
                )


            elif not candidate_response.strip():

                st.error(
                    "❌ Missing Answer Text: Please enter "
                    "your response before submitting."
                )


            else:

                with st.spinner(
                    "Analyzing your response..."
                ):

                    try:

                        # -------------------------------------
                        # GRADING LLM
                        # -------------------------------------

                        grading_llm = create_llm(
                            temperature=0.2
                        )


                        # -------------------------------------
                        # GRADING PROMPT
                        # -------------------------------------

                        eval_prompt = (
                            ChatPromptTemplate.from_messages(
                                [

                                    (
                                        "system",

                                        """
You are a strict technical interviewer
evaluating a candidate's interview response.

Evaluate technical correctness,
conceptual understanding,
logical reasoning,
completeness,
and communication.

Return ONLY valid JSON.

The JSON must contain exactly:

"score":
An integer between 0 and 100.

"technical_strengths":
A string explaining the concepts
the candidate explained correctly.

"logical_flaws":
A string explaining incorrect concepts,
missing details, logical problems,
bugs, or important edge cases.

"reference_response":
A strong model answer that demonstrates
what an excellent candidate should say.

Do not output Markdown outside the JSON.
"""
                                    ),

                                    (
                                        "human",

                                        """
TARGET ROLE:

{role}


INTERVIEW QUESTION:

{question}


CANDIDATE ANSWER:

{answer}
"""
                                    )

                                ]
                            )
                        )


                        # -------------------------------------
                        # GRADING CHAIN
                        # -------------------------------------

                        grading_chain = (
                            eval_prompt
                            | grading_llm
                            | JsonOutputParser()
                        )


                        # -------------------------------------
                        # CALL MODEL
                        # -------------------------------------

                        grading_output = (
                            grading_chain.invoke(
                                {

                                    "question":
                                    st.session_state.interview_question,

                                    "answer":
                                    candidate_response,

                                    "role":
                                    st.session_state.target_role

                                }
                            )
                        )


                        # -------------------------------------
                        # DISPLAY GRADING
                        # -------------------------------------

                        st.success(
                            "🏁 Grading Process Complete"
                        )


                        st.metric(

                            "Performance Grade",

                            f"{grading_output.get('score', 0)}/100"
                        )


                        st.subheader(
                            "🎯 Identified Analytical Strengths"
                        )

                        st.write(
                            grading_output.get(
                                "technical_strengths",
                                "No strengths returned."
                            )
                        )


                        st.subheader(
                            "⚠️ Logical Flaws & Conceptual Gaps"
                        )

                        st.write(
                            grading_output.get(
                                "logical_flaws",
                                "No flaws returned."
                            )
                        )


                        st.subheader(
                            "📚 High-Performance Reference Model Answer"
                        )

                        st.write(
                            grading_output.get(
                                "reference_response",
                                "No reference response returned."
                            )
                        )


                    except Exception as e:

                        st.error(
                            f"⚠️ Processing Error: {str(e)}"
                        )