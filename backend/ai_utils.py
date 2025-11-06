import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from typing import List, Dict
import pypdf
from io import BytesIO
import time
import json
from pydantic import BaseModel, Field
from .schemas import ResumeData, Project, Education, Experience, SkillCategory

os.environ["USER_AGENT"] = "AIResumeMaker/1.0"

class SkillListInternal(BaseModel):
    skills: List[SkillCategory]

class ProjectDetails(BaseModel):
    title: str = Field(description="A concise and professional title for the project.")
    description: List[str] = Field(description="A list of 2 bullet points describing the project's key features and achievements.")
    tech_stack: str = Field(description="A comma-separated string of the key technologies, languages, and frameworks used.")

class SuggestedProjects(BaseModel):
    projects: List[ProjectDetails]

def _invoke_with_retry(chain, params):
    max_retries = 3
    delay = 2
    for attempt in range(max_retries):
        try:
            return chain.invoke(params)
        except Exception as e:
            if "Quota exceeded" in str(e) or "429" in str(e):
                if attempt < max_retries - 1:
                    print(f"Rate limit exceeded. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2
                else:
                    return {"error": "API quota limit reached. Please try again in a few minutes."}
            else:
                print(f"An unexpected error occurred: {e}")
                return {"error": f"An unexpected error occurred: {e}"}
    return {"error": "Failed after multiple retries."}

def _parse_skills(resume_text: str, api_key: str) -> List[Dict[str, str]]:
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key, temperature=0.0)
        parser = JsonOutputParser(pydantic_object=SkillListInternal)
        template = """Extract the skills from the resume text and categorize them into logical groups.
{format_instructions}
RESUME TEXT:
{resume_text}
"""
        prompt = PromptTemplate(template=template, input_variables=["resume_text"], partial_variables={"format_instructions": parser.get_format_instructions()})
        chain = prompt | llm | parser
        response = _invoke_with_retry(chain, {"resume_text": resume_text})
        if isinstance(response, dict) and "error" in response:
            return []
        return response.get('skills', [])
    except Exception as e:
        print(f"Error in _parse_skills: {e}")
        return []

def parse_resume_from_pdf(pdf_bytes: bytes):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: return {"error": "GOOGLE_API_KEY not set."}
    try:
        pdf_reader = pypdf.PdfReader(BytesIO(pdf_bytes))
        resume_text = "".join([page.extract_text() or "" for page in pdf_reader.pages])
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key, temperature=0.0)
        main_parser = JsonOutputParser(pydantic_object=ResumeData)
        main_prompt_template = """You are an expert resume parser. Analyze the resume text and extract the information into a structured JSON object.
Pay close attention to all sections EXCEPT for skills.
{format_instructions}
RESUME TEXT:
{resume_text}
"""
        main_prompt = PromptTemplate(template=main_prompt_template, input_variables=["resume_text"], partial_variables={"format_instructions": main_parser.get_format_instructions()})
        main_chain = main_prompt | llm | main_parser
        parsed_data = _invoke_with_retry(main_chain, {"resume_text": resume_text})

        if isinstance(parsed_data, dict) and "error" in parsed_data:
            return parsed_data
        # Separately parse skills
        parsed_skills = _parse_skills(resume_text, api_key)
        parsed_data['skills'] = parsed_skills

        # Ensure all schema fields correct type and present
        for field, field_type in ResumeData.__annotations__.items():
            if field not in parsed_data:
                if str(field_type).startswith("typing.List"):
                    parsed_data[field] = []
                else:
                    parsed_data[field] = ""
            # Fix leetcode field (should never be list)
            if field == "leetcode" and not isinstance(parsed_data[field], str):
                parsed_data[field] = ""

        return parsed_data
    except Exception as e:
        print(f"Error in parse_resume_from_pdf: {e}")
        return {"error": f"Failed to parse resume: {e}"}

def analyze_github_repo(url: str):
    from langchain_community.document_loaders import WebBaseLoader
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: return {"error": "GOOGLE_API_KEY not set."}
    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key, temperature=0.0)
        parser = JsonOutputParser(pydantic_object=ProjectDetails)
        prompt = PromptTemplate(
            template="""Analyze the GitHub README file. Extract the project title, a 2-bullet point description, and its tech stack.
**IMPORTANT**: You MUST return ONLY a JSON object.
{format_instructions}
DOCUMENT:
{document}
""",
            input_variables=["document"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        chain = prompt | llm | parser
        content = docs[0].page_content if docs else ""
        return _invoke_with_retry(chain, {"document": content[:10000]})
    except Exception as e:
        return {"error": f"Failed to analyze repository: {e}"}

def suggest_projects(skills: List[SkillCategory]):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: return {"error": "GOOGLE_API_KEY not set."}
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key, temperature=0.7)
        parser = JsonOutputParser(pydantic_object=SuggestedProjects)
        skills_text = ", ".join([f"{s['category']}: {s['details']}" for s in skills])
        prompt = PromptTemplate(template="Suggest 2 project ideas based on the user's skills. Return ONLY a JSON object.\n{format_instructions}\nUSER'S SKILLS: {skills}", input_variables=["skills"], partial_variables={"format_instructions": parser.get_format_instructions()})
        chain = prompt | llm | parser
        response = _invoke_with_retry(chain, {"skills": skills_text})
        if isinstance(response, dict) and "error" in response:
            return response
        return response.get('projects', [])
    except Exception as e:
        return {"error": f"Failed to get AI suggestions: {e}"}

def categorize_skills(skills_list: List[str]):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: return [{"category": "Error", "details": "GOOGLE_API_KEY not set."}]
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key, temperature=0.0)
        parser = JsonOutputParser(pydantic_object=SkillListInternal)
        prompt = PromptTemplate(template="Categorize these skills into logical groups (e.g., Languages:python,java, Frontend:react, html, css,stremalit, Backend:node.js,express.js,fastapi, AI/ML:langchain,RAG , scikit-learn,tensorflow ,Developer tools like git,github, cs fundamentals like OS,DBMS, CN,machine learning,DL,DSA). Return ONLY JSON.\n{format_instructions}\nSKILLS:\n{skills}", input_variables=["skills"], partial_variables={"format_instructions": parser.get_format_instructions()})
        chain = prompt | llm | parser
        response = _invoke_with_retry(chain, {"skills": ", ".join(skills_list)})
        if isinstance(response, dict) and "error" in response:
            return [{"category": "Error", "details": response['error']}]
        return response.get('skills', [])
    except Exception as e:
        return [{"category": "Skills", "details": ", ".join(skills_list)}]

def generate_summary_from_skills_and_role(skills: List[SkillCategory], job_description: str):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "Error: GOOGLE_API_KEY not set."
    try:
        skills_text = "; ".join([f"{cat.category}: {cat.details}" for cat in skills])
        
        prompt_text = (
            "Write a 2-3 sentence professional summary based on these skills and the target job role.\n"
            "Skills: {skills_text}\n"
            "Job Role: {job_description}"
        )
        
        prompt = PromptTemplate.from_template(prompt_text)
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0, google_api_key=api_key)
        chain = prompt | llm
        response = _invoke_with_retry(chain, {"skills_text": skills_text, "job_description": job_description})
        
        if hasattr(response, 'content'):
            return response.content
        return str(response)
    except Exception as e:
        return f"Error generating summary: {e}"
