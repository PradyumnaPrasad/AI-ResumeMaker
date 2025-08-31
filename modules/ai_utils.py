import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import pypdf
from io import BytesIO

os.environ["USER_AGENT"] = "AIResumeMaker/1.0"

# --- Pydantic Models for Resume Parsing ---
class Education(BaseModel):
    degree: str
    institution: str
    dates: str
    grade_type: Optional[str] = Field(description="The type of grade, e.g., 'CGPA' or 'Percentage'")
    grade_value: Optional[str] = Field(description="The numerical value of the grade")

class Project(BaseModel):
    title: str
    points: List[str]
    techStack: Optional[str] = ""
    repo_link: Optional[str] = ""

class Experience(BaseModel):
    role: str
    company: str
    dates: str
    responsibilities: List[str]

class ResumeData(BaseModel):
    name: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    linkedin: Optional[str] = ""
    github: Optional[str] = ""
    leetcode: Optional[str] = ""
    summary: Optional[str] = ""
    education: List[Education] = []
    projects: List[Project] = []
    internships: List[Experience] = []
    experience: List[Experience] = []
    skills: List[Dict[str, str]] = Field(description="Categorized skills, e.g., [{'category': 'Languages', 'details': 'Python, Java'}]")
    achievements: List[str] = []
    leadership: List[str] = []

# --- Pydantic Models for Other AI Features ---
class SkillCategory(BaseModel):
    category: str = Field(description="The category of the skills, e.g., 'Languages', 'Frameworks/Tools'")
    details: str = Field(description="A comma-separated string of skills in this category")

class SkillList(BaseModel):
    skills: List[SkillCategory]

class ProjectDetails(BaseModel):
    title: str = Field(description="A concise and professional title for the project.")
    description: List[str] = Field(description="A list of 2 bullet points describing the project's key features and achievements.")
    tech_stack: str = Field(description="A comma-separated string of the key technologies, languages, and frameworks used.")

class SuggestedProjects(BaseModel):
    projects: List[ProjectDetails]


# --- AI Functions ---

def parse_resume_from_pdf(pdf_bytes: bytes):
    """Extracts text from a PDF and uses an LLM to parse it into a structured resume format."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: return {"error": "GOOGLE_API_KEY not set."}

    try:
        pdf_reader = pypdf.PdfReader(BytesIO(pdf_bytes))
        resume_text = ""
        for page in pdf_reader.pages:
            resume_text += page.extract_text() or ""

        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key, temperature=0.0)
        parser = JsonOutputParser(pydantic_object=ResumeData)

        prompt = PromptTemplate(
            template="""You are an expert resume parser. Your task is to analyze the text from a resume and extract the information into a structured JSON format.
            
            Pay close attention to the requested schema. For education, explicitly identify if a grade is a 'CGPA' or 'Percentage' and separate the value.
            If a field is not present in the resume text, leave it as an empty string or empty list. For skills, categorize them.
            
            Here is an example of how to handle an education entry like "Vidyaniketan PU College, Percentage: 96.43":
            "education": [
                {{
                  "degree": "Higher Secondary",
                  "institution": "Vidyaniketan PU College",
                  "dates": "June 2021-June 2023",
                  "grade_type": "Percentage",
                  "grade_value": "96.43"
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
        return {"error": f"Failed to parse resume: {e}"}

def analyze_github_repo(url: str):
    from langchain_community.document_loaders import WebBaseLoader
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: return {"error": "GOOGLE_API_KEY not set."}
    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key, temperature=0.0)
        parser = JsonOutputParser(pydantic_object=ProjectDetails)
        prompt = PromptTemplate(template="You are an expert at analyzing GitHub README files. Based on the following document, extract the project's title, a 2 bullet point description, and its tech stack.\n{format_instructions}\nDOCUMENT:\n{document}", input_variables=["document"], partial_variables={"format_instructions": parser.get_format_instructions()})
        chain = prompt | llm | parser
        content = docs[0].page_content if docs else ""
        return chain.invoke({"document": content[:10000]})
    except Exception as e:
        return {"error": f"Failed to analyze repository: {e}"}

def suggest_projects(skills: List[Dict[str, str]]):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: return {"error": "GOOGLE_API_KEY not set."}
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key, temperature=0.7)
        parser = JsonOutputParser(pydantic_object=SuggestedProjects)
        skills_text = ", ".join([s.get('details', '') for s in skills])
        prompt = PromptTemplate(
            template="""You are a helpful assistant that suggests project ideas. Based on the user's skills, generate 2 diverse and impressive project ideas.
            **IMPORTANT**: You MUST format your response as a single JSON object adhering to the schema. Do not include any other text.
            {format_instructions}
            USER'S SKILLS: {skills}""",
            input_variables=["skills"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | llm | parser
        response = chain.invoke({"skills": skills_text})
        return response.get('projects', [])
    except Exception as e:
        return {"error": f"Failed to get AI suggestions: {e}"}

def categorize_skills(skills_list: List[str]):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: return [{"category": "Error", "details": "GOOGLE_API_KEY not set."}]
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key, temperature=0.0)
        parser = JsonOutputParser(pydantic_object=SkillList)
        prompt = PromptTemplate(template="You are an expert tech recruiter. Categorize the following skills into logical groups.\n{format_instructions}\nSKILL LIST:\n{skills}", input_variables=["skills"], partial_variables={"format_instructions": parser.get_format_instructions()})
        chain = prompt | llm | parser
        response = chain.invoke({"skills": ", ".join(skills_list)})
        return response.get('skills', [])
    except Exception as e:
        return [{"category": "Skills", "details": ", ".join(skills_list)}]

def generate_summary(skills: List[Dict[str, str]], job_description: str):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: return "Error: GOOGLE_API_KEY not set."
    skills_text = "; ".join([f"{cat.get('category', '')}: {cat.get('details', '')}" for cat in skills])
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0, google_api_key=api_key)
    prompt_text = f"Based on the following skills and job description, write a 2-3 sentence professional summary.\n\nSkills: {skills_text}\n\nJob Description: {job_description}"
    return llm.invoke(prompt_text).content

