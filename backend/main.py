from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict
import json

from . import database, schemas, auth, ai_utils

database.Base.metadata.create_all(bind=database.engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/signup", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    """Endpoint to create a new user account."""
    db_user = auth.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return auth.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    """Endpoint for user login. Returns a JWT access token."""
    user = auth.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect Email or Password")
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/resume/", response_model=schemas.ResumeData)
def get_resume_data(current_user: schemas.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    """Protected endpoint to retrieve a user's resume data."""
    db_resume = db.query(database.Resume).filter(database.Resume.owner_id == current_user.id).first()
    if not db_resume or not db_resume.resume_data:
        return schemas.ResumeData()
    
    # The resume_data is stored as a JSON string, so we need to parse it
    if isinstance(db_resume.resume_data, str):
        return json.loads(db_resume.resume_data)
    return db_resume.resume_data

@app.put("/resume/", response_model=schemas.ResumeData)
def update_resume_data(resume_data: schemas.ResumeData, current_user: schemas.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    """Protected endpoint to update a user's resume data."""
    db_resume = db.query(database.Resume).filter(database.Resume.owner_id == current_user.id).first()
    if not db_resume:
        db_resume = database.Resume(owner_id=current_user.id)
        db.add(db_resume)
    
    db_resume.resume_data = resume_data.dict()
    db.commit()
    db.refresh(db_resume)
    return db_resume.resume_data

@app.post("/ai/parse-resume/", response_model=schemas.ResumeData)
async def parse_resume(file: UploadFile = File(...), current_user: schemas.User = Depends(auth.get_current_user)):
    """Endpoint to parse an uploaded PDF resume."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")
    pdf_bytes = await file.read()
    parsed_data = ai_utils.parse_resume_from_pdf(pdf_bytes)
    if isinstance(parsed_data, dict) and "error" in parsed_data:
        raise HTTPException(status_code=500, detail=parsed_data["error"])
    return parsed_data

@app.post("/ai/generate-summary/", response_model=Dict[str, str])
def generate_summary_endpoint(request_data: schemas.SummaryRequest, current_user: schemas.User = Depends(auth.get_current_user)):
    """Endpoint to generate an AI summary for the resume."""
    summary = ai_utils.generate_summary_from_skills_and_role(
        skills=request_data.skills,
        job_description=request_data.job_description
    )
    if "error" in summary:
        raise HTTPException(status_code=500, detail=summary)
    return {"summary": summary}

@app.post("/ai/suggest-projects/")
def suggest_projects_endpoint(skills_data: schemas.SkillList, current_user: schemas.User = Depends(auth.get_current_user)):
    """Endpoint to get AI project suggestions based on skills."""
    suggestions = ai_utils.suggest_projects(skills_data.skills)
    if isinstance(suggestions, dict) and "error" in suggestions:
        raise HTTPException(status_code=500, detail=suggestions["error"])
    return suggestions

@app.post("/ai/categorize-skills/")
def categorize_skills_endpoint(skills: List[str], current_user: schemas.User = Depends(auth.get_current_user)):
    """Endpoint to categorize a list of skills."""
    categorized = ai_utils.categorize_skills(skills)
    if isinstance(categorized, dict) and "error" in categorized:
        raise HTTPException(status_code=500, detail=categorized["error"])
    return categorized

@app.post("/ai/analyze-github/")
def analyze_github_endpoint(url_data: Dict[str, str], current_user: schemas.User = Depends(auth.get_current_user)):
    """Endpoint to analyze a GitHub repository."""
    url = url_data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    analysis = ai_utils.analyze_github_repo(url)
    if isinstance(analysis, dict) and "error" in analysis:
        raise HTTPException(status_code=500, detail=analysis["error"])
    return analysis

