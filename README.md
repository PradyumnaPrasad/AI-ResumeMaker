# AI-Powered Resume Maker

This is a sophisticated, AI-driven web application built with Streamlit and FastAPI that empowers users to create professional, polished resumes with ease. The application leverages the power of Large Language Models (LLMs) through the Google Gemini API to automate and enhance various aspects of the resume-building process, from data entry to content generation.

## ✨ Key Features

This project is more than just a form-filler; it's a suite of intelligent tools designed to streamline resume creation:

*   **Dynamic Resume Building**: A clean, multi-page Streamlit interface allows users to input their personal information, education, projects, experience, skills, and more.
*   **Professional PDF Generation**: The application generates a clean, single-page PDF resume using a professional and aesthetically pleasing template, ensuring a high-quality final product.
*   **🤖 AI Resume Parser**: Users can upload an existing resume in PDF format. The AI will read the document, parse the content, and automatically pre-fill all the relevant sections of the application, saving a significant amount of time.
*   **🤖 AI GitHub Analyzer**: By simply pasting a URL to a GitHub repository, the AI will analyze the README.md file to automatically extract the project's title, a concise description, and its technology stack, and add it directly to the resume.
*   **🤖 AI Project Suggester**: For users looking for inspiration, the AI can generate tailored project ideas based on their listed skills. These suggestions can be added to the resume with a single click.
*   **🤖 AI Skill Categorizer**: Users can input a comma-separated list of their skills, and the AI will intelligently group them into professional categories like "Languages," "Frameworks/Tools," "AI/ML," etc.
*   **🤖 AI Summary Writer**: The application can generate a compelling, professional summary based on the user's skills and experience, tailored to a specific job description if provided.

## 🛠️ Tech Stack

*   **Frontend**: Streamlit
*   **Backend**: FastAPI
*   **AI/LLM Orchestration**: LangChain
*   **LLM Provider**: Google Gemini API (gemini-1.5-flash)
*   **PDF Generation**: ReportLab
*   **PDF Parsing**: pypdf
*   **Web Content Loading**: BeautifulSoup4
*   **Database**: SQLite
*   **Core Language**: Python

## 📂 Project Structure

The project is organized into a modular structure for clarity and maintainability:

```
resumeMaker/
│
├── backend/                # FastAPI backend application
│   ├── main.py             # Main FastAPI application
│   ├── database.py         # Database configuration and models
│   ├── auth.py             # Authentication logic
│   ├── schemas.py          # Pydantic models for data validation
│   └── ai_utils.py         # All LangChain pipelines and AI functions
│
├── frontend/               # Streamlit frontend application
│   ├── app.py              # Main Streamlit application
│   ├── modules/            # Core logic and reusable functions
│   │   ├── resume_generator.py # PDF generation logic
│   │   └── ...
│   ├── templates/          # Resume layout and formatting
│   │   └── template1.py    # The professional PDF template
│   └── assets/             # Static files (fonts, etc.)
│
├── requirements.txt        # All project dependencies
├── .gitignore              # Git ignore file
└── README.md               # Project README file
```

## 🚀 Getting Started

Follow these steps to get the AI Resume Maker running on your local machine.

### 1. Prerequisites

*   Python 3.9+
*   A Google Gemini API Key

### 2. Installation

Clone the repository:

```bash
git clone https://github.com/your-username/resumeMaker.git # Replace with your repo URL
cd resumeMaker
```

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Set up your API Key:
You need to set your Google Gemini API key as an environment variable. The application will not work without it.

On macOS/Linux:

```bash
export GOOGLE_API_KEY="your_actual_api_key_goes_here"
```

On Windows (Command Prompt):

```cmd
set GOOGLE_API_KEY="your_actual_api_key_goes_here"
```

### 3. Running the Application Locally

First, start the backend:

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then, in a new terminal, start the frontend:

```bash
cd frontend
streamlit run app.py
```

Your web browser will automatically open with the Streamlit application running.