# AI-Powered Resume Maker

This is a sophisticated, AI-driven web application built with Streamlit and LangChain that empowers users to create professional, polished resumes with ease. The application leverages the power of Large Language Models (LLMs) through the Google Gemini API to automate and enhance various aspects of the resume-building process, from data entry to content generation.

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
*   **AI/LLM Orchestration**: LangChain
*   **LLM Provider**: Google Gemini API (gemini-1.5-flash)
*   **PDF Generation**: ReportLab
*   **PDF Parsing**: pypdf
*   **Web Content Loading**: BeautifulSoup4
*   **Core Language**: Python

## 📂 Project Structure

The project is organized into a modular structure for clarity and maintainability:

```
resumeMaker/
│
├── app.py                  # Main Streamlit application
├── requirements.txt        # All project dependencies
│
├── modules/                # Core logic and reusable functions
│   ├── __init__.py
│   ├── ai_utils.py         # All LangChain pipelines and AI functions
│   └── resume_generator.py # PDF generation logic
│
├── templates/              # Resume layout and formatting
│   └── template1.py        # The professional PDF template
│
├── assets/                 # Static files
│   └── fonts/              # Font files for the PDF template
│
└── output/                 # Directory for generated resumes
```

## 🚀 Getting Started

Follow these steps to get the AI Resume Maker running on your local machine.

### 1. Prerequisites

*   Python 3.9+
*   A Google Gemini API Key

### 2. Installation

Clone the repository:

```
git clone [https://github.com/your-username/resumeMaker.git](https://github.com/your-username/resumeMaker.git)
cd resumeMaker
```

Create a virtual environment:

```
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

Install the dependencies:

```
pip install -r requirements.txt
```

Set up your API Key:
You need to set your Google Gemini API key as an environment variable. The application will not work without it.

On macOS/Linux:

```
export GOOGLE_API_KEY="your_actual_api_key_goes_here"
```

On Windows (Command Prompt):

```
set GOOGLE_API_KEY="your_actual_api_key_goes_here"
```

### 3. Running the Application

Once your environment is set up, you can run the Streamlit app with a single command:

```
streamlit run app.py
```

Your web browser will automatically open with the application running.

