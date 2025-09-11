from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Optional

# --- Resume Data Schemas ---
# These define the structure for a user's resume data. They are the "source of truth"
# for what gets saved to and retrieved from the database.

class Education(BaseModel):
    degree: str
    institution: str
    dates: str
    grade_type: Optional[str]
    grade_value: Optional[str]

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

class SkillCategory(BaseModel):
    category: str = Field(description="The category of the skills, e.g., 'Languages', 'Frameworks/Tools'")
    details: str = Field(description="A comma-separated string of skills in this category")

class ResumeData(BaseModel):
    name: Optional[str] = ""
    email: Optional[EmailStr] = ""
    phone: Optional[str] = ""
    linkedin: Optional[str] = ""
    github: Optional[str] = ""
    leetcode: Optional[str] = ""
    summary: Optional[str] = ""
    education: List[Education] = []
    projects: List[Project] = []
    internships: List[Experience] = []
    experience: List[Experience] = []
    skills: List[SkillCategory] = []
    achievements: List[str] = []
    leadership: List[str] = []
    section_order: List[str] = []

    class Config:
        # Use 'from_attributes' for Pydantic V2 compatibility instead of 'orm_mode'
        from_attributes = True

# --- User Authentication Schemas ---
# These define the data needed for creating users and handling login tokens.

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# --- AI-related schemas that are used in API request bodies ---
# This is required by the /ai/suggest-projects/ endpoint in main.py
class SkillList(BaseModel):
    skills: List[Dict[str, str]]

class SummaryRequest(BaseModel):
    skills: List[SkillCategory]
    job_description: str

