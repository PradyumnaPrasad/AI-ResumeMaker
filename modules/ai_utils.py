import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import pypdf
from io import BytesIO
import streamlit as st
import time

os.environ["USER_AGENT"] = "AIResumeMaker/1.0"

# --- (Pydantic Models) ---
class Education(BaseModel):
    degree: str
    institution: str
    dates: str
    grade_type: Optional[str] = Field(description="The type of grade, e.g., 'CGPA' or 'Percentage'")
    grade_value: Optional[str] = Field(description="The numerical value of the grade")
class Project(BaseModel):
    title: str; points: List[str]; techStack: Optional[str] = ""; repo_link: Optional[str] = ""
class Experience(BaseModel):
    role: str; company: str; dates: str; responsibilities: List[str]
class ResumeData(BaseModel):
    name: Optional[str] = ""; email: Optional[str] = ""; phone: Optional[str] = ""; linkedin: Optional[str] = ""; github: Optional[str] = ""; leetcode: Optional[str] = ""; summary: Optional[str] = ""; education: List[Education] = []; projects: List[Project] = []; internships: List[Experience] = []; experience: List[Experience] = []; skills: List[Dict[str, str]] = Field(description="Categorized skills, e.g., [{'category': 'Languages', 'details': 'Python, Java'}]"); achievements: List[str] = []; leadership: List[str] = []
class SkillCategory(BaseModel):
    category: str = Field(description="The category of the skills, e.g., 'Languages', 'Frameworks/Tools'"); details: str = Field(description="A comma-separated string of skills in this category")
class SkillList(BaseModel):
    skills: List[SkillCategory]
class ProjectDetails(BaseModel):
    title: str = Field(description="A concise and professional title for the project."); description: List[str] = Field(description="A list of 2 bullet points describing the project's key features and achievements."); tech_stack: str = Field(description="A comma-separated string of the key technologies, languages, and frameworks used.")
class SuggestedProjects(BaseModel):
    projects: List[ProjectDetails]


# --- AI Functions with Caching and Rate Limit Handling ---

@st.cache_data(ttl="24h")
def parse_resume_from_pdf(pdf_bytes: bytes):
    """Extracts text from a PDF and uses an LLM to parse it, with retry logic for rate limits."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: return {"error": "GOOGLE_API_KEY not set."}

    max_retries = 3
    delay = 2

    for attempt in range(max_retries):
        try:
            pdf_reader = pypdf.PdfReader(BytesIO(pdf_bytes))
            resume_text = "".join([page.extract_text() or "" for page in pdf_reader.pages])
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key, temperature=0.0)
            parser = JsonOutputParser(pydantic_object=ResumeData)
            
         
            prompt = PromptTemplate(
                template="""You are an expert resume parser. Your task is to analyze the text from a resume and extract the information into a structured JSON format.
                
                Pay close attention to the requested schema. If a field is not present, leave it as an empty string or list.
                
                Here is an example of how to handle an education entry like "Vidyaniketan PU College, Percentage: 96.43":
                "education": [
                    {{
                      "degree": "Higher Secondary", "institution": "Vidyaniketan PU College", "dates": "June 2021-June 2023",
                      "grade_type": "Percentage", "grade_value": "96.43"
                    }}
                ]

                Here is an example of how to handle a skills section like "Languages: Python, Java | AI/ML: LangChain, RAG":
                "skills": [
                    {{
                        "category": "Languages",
                        "details": "Python, Java"
                    }},
                    {{
                        "category": "AI/ML",
                        "details": "LangChain, RAG"
                    }}
                ]

                **IMPORTANT**: You MUST format your response as a single JSON object that strictly adheres to the schema. Do not include any other text.

                {format_instructions}
                
                RESUME TEXT:
                {resume_text}
                """,
                input_variables=["resume_text"],
                partial_variables={"format_instructions": parser.get_format_instructions()},
            )

            chain = prompt | llm | parser
            response = chain.invoke({"resume_text": resume_text})
            return response

        except Exception as e:
            if "Quota exceeded" in str(e) or "429" in str(e):
                if attempt < max_retries - 1:
                    print(f"Rate limit exceeded. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2
                else:
                    return {"error": "API quota limit reached. Please try again in a few minutes."}
            else:
                return {"error": f"Failed to parse resume: {e}"}
    
    return {"error": "Failed to parse resume after multiple retries."}


# --- (Other functions remain the same) ---
@st.cache_data(ttl="24h")
def analyze_github_repo(url: str):
    from langchain_community.document_loaders import WebBaseLoader
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: return {"error": "GOOGLE_API_KEY not set."}
    try:
        # ... (function logic is correct)
        loader = WebBaseLoader(url)
        docs = loader.load()
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key, temperature=0.0)
        parser = JsonOutputParser(pydantic_object=ProjectDetails)
        prompt = PromptTemplate(template="You are an expert at analyzing GitHub README files... (prompt remains the same)", input_variables=["document"], partial_variables={"format_instructions": parser.get_format_instructions()})
        chain = prompt | llm | parser
        content = docs[0].page_content if docs else ""
        return chain.invoke({"document": content[:10000]})
    except Exception as e:
        return {"error": f"Failed to analyze repository: {e}"}

@st.cache_data(ttl="24h")
def suggest_projects(skills: List[Dict[str, str]]):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: return {"error": "GOOGLE_API_KEY not set."}
    try:
        # ... (function logic is correct)
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key, temperature=0.7)
        parser = JsonOutputParser(pydantic_object=SuggestedProjects)
        skills_text = ", ".join([s.get('details', '') for s in skills])
        prompt = PromptTemplate(template="You are a helpful assistant that suggests project ideas... (prompt remains the same)", input_variables=["skills"], partial_variables={"format_instructions": parser.get_format_instructions()})
        chain = prompt | llm | parser
        response = chain.invoke({"skills": skills_text})
        return response.get('projects', [])
    except Exception as e:
        return {"error": f"Failed to get AI suggestions: {e}"}

@st.cache_data(ttl="24h")
def categorize_skills(skills_list: List[str]):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: return [{"category": "Error", "details": "GOOGLE_API_KEY not set."}]
    try:
        # ... (function logic is correct)
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key, temperature=0.0)
        parser = JsonOutputParser(pydantic_object=SkillList)
        prompt = PromptTemplate(template="You are an expert tech recruiter... (prompt remains the same)", input_variables=["skills"], partial_variables={"format_instructions": parser.get_format_instructions()})
        chain = prompt | llm | parser
        response = chain.invoke({"skills": ", ".join(skills_list)})
        return response.get('skills', [])
    except Exception as e:
        return [{"category": "Skills", "details": ", ".join(skills_list)}]

@st.cache_data(ttl="24h")
def generate_summary(skills: List[Dict[str, str]], job_description: str):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: return "Error: GOOGLE_API_KEY not set."
    try:
        # ... (function logic is correct)
        skills_text = "; ".join([f"{cat.get('category', '')}: {cat.get('details', '')}" for cat in skills])
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0, google_api_key=api_key)
        prompt_text = f"Based on the following skills and job description... (prompt remains the same)"
        return llm.invoke(prompt_text).content
    except Exception as e:
        return f"Error generating summary: {e}"

