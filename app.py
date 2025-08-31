from modules.ai_utils import categorize_skills, generate_summary, suggest_projects, analyze_github_repo, parse_resume_from_pdf
import streamlit as st
import os
from modules.resume_generator import generate_pdf

# --- Setup and session state initialization ---
st.set_page_config(page_title="AI Resume Maker", page_icon="📄", layout="centered")
if not os.path.exists('output'):
    os.makedirs('output')
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = {
        "name": "", "email": "", "phone": "",
        "linkedin": "", "github": "", "leetcode": "",
        "summary": "", "internships": [], "experience": [], "projects": [], "skills": [],
        "education": [], "achievements": [], "leadership": []
    }
if 'ai_suggestions' not in st.session_state:
    st.session_state.ai_suggestions = []

# --- Helper functions ---
def remove_item(category, index):
    if 0 <= index < len(st.session_state.resume_data[category]):
        st.session_state.resume_data[category].pop(index)

def toggle_project_selection(project_data):
    project_titles = [p.get('title') for p in st.session_state.resume_data['projects'] if isinstance(p, dict)]
    is_added = project_data.get('title') in project_titles
    if is_added:
        st.session_state.resume_data['projects'] = [p for p in st.session_state.resume_data['projects'] if not (isinstance(p, dict) and p.get('title') == project_data.get('title'))]
        st.toast(f"Removed project '{project_data.get('title')}'")
    else:
        new_project = {"title": project_data.get('title', ''), "points": project_data.get('description', []), "techStack": project_data.get('tech_stack', ''), "repo_link": ""}
        st.session_state.resume_data['projects'].append(new_project)
        st.toast(f"Added project '{new_project.get('title')}'")

# --- Sidebar and Page Setup ---
st.sidebar.title("Resume Sections")
page_options = ["Import Resume", "Personal Info", "Skills", "Summary", "Education", "Projects", "Internship Experience (Optional)", "Work Experience (Optional)", "Achievements & Leadership", "Generate Resume"]
page = st.sidebar.radio("Go to", page_options, key="page_nav")
st.title("📄 AI-Powered Resume Maker")
API_KEY_CONFIGURED = bool(os.getenv("GOOGLE_API_KEY"))

# --- Page Rendering Logic ---
if page == "Import Resume":
    st.header("🚀 Import Your Existing Resume")
    st.markdown("Upload your current resume in PDF format, and our AI will automatically extract the details and pre-fill all the sections for you.")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        if st.button("Parse and Fill Resume"):
            if not API_KEY_CONFIGURED: st.error("Please set your GOOGLE_API_KEY in the terminal to use this feature.")
            else:
                with st.spinner("AI is reading your resume... This may take a minute."):
                    pdf_bytes = uploaded_file.getvalue()
                    parsed_data = parse_resume_from_pdf(pdf_bytes)
                    if isinstance(parsed_data, dict) and "error" not in parsed_data:
                        st.session_state.resume_data = parsed_data
                        st.success("Resume successfully parsed! Navigate to other sections to see the pre-filled data.")
                    elif isinstance(parsed_data, dict) and "error" in parsed_data:
                        st.error(parsed_data["error"])
                    else:
                        st.error("An unexpected error occurred during parsing.")

elif page == "Personal Info":
    st.header("Personal Information")
    st.session_state.resume_data['name'] = st.text_input("Full Name", st.session_state.resume_data.get('name', ''))
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.resume_data['email'] = st.text_input("Email", st.session_state.resume_data.get('email', ''))
        st.session_state.resume_data['linkedin'] = st.text_input("LinkedIn URL", st.session_state.resume_data.get('linkedin', ''))
    with col2:
        st.session_state.resume_data['phone'] = st.text_input("Phone Number", st.session_state.resume_data.get('phone', ''))
        st.session_state.resume_data['github'] = st.text_input("GitHub URL", st.session_state.resume_data.get('github', ''))
    st.session_state.resume_data['leetcode'] = st.text_input("LeetCode URL", st.session_state.resume_data.get('leetcode', ''))

elif page == "Skills":
    st.header("Skills")
    raw_skills = st.text_area("Enter all your skills, separated by commas", help="e.g., Python, FastAPI, React, AWS, Docker, SQL")
    if st.button("Categorize Skills with AI ✨"):
        if not API_KEY_CONFIGURED: st.error("Please set your GOOGLE_API_KEY in the terminal.")
        elif not raw_skills: st.warning("Please enter at least one skill.")
        else:
            skills_list = [skill.strip() for skill in raw_skills.split(',')]
            with st.spinner("AI is organizing your skills..."):
                st.session_state.resume_data['skills'] = categorize_skills(skills_list)
    if st.session_state.resume_data['skills']:
        st.write("### Your Categorized Skills:")
        for category in st.session_state.resume_data['skills']:
            st.markdown(f"**{category.get('category')}:** {category.get('details')}")

elif page == "Summary":
    st.header("Professional Summary")
    st.session_state.resume_data['summary'] = st.text_area("Your Summary", value=st.session_state.resume_data.get('summary', ''), height=200)
    st.subheader("✨ AI Assistant")
    job_desc_input = st.text_area("Optional: Paste a target job description for a tailored summary")
    if st.button("Generate Summary with AI"):
        if not API_KEY_CONFIGURED: st.error("Please set your GOOGLE_API_KEY in the terminal.")
        elif not st.session_state.resume_data['skills']: st.warning("Please add some skills in the 'Skills' section first.")
        else:
            with st.spinner("AI is crafting your summary..."):
                st.session_state.resume_data['summary'] = generate_summary(st.session_state.resume_data['skills'], job_desc_input)
                st.rerun()

elif page == "Education":
    st.header("Education")
    st.info("Add your most recent education first (e.g., University), then prior education (e.g., High School).")
    for i, edu in enumerate(st.session_state.resume_data['education']):
        with st.container(border=True):
            st.write(f"**{edu.get('degree')}** from {edu.get('institution')}")
            st.button("Remove", key=f"remove_edu_{i}", on_click=remove_item, args=('education', i))
    with st.form("new_edu_form", clear_on_submit=True):
        st.subheader("Add New Education Entry")
        edu_degree = st.text_input("Degree / Course (e.g., Bachelor of Engineering in CSE)")
        edu_institution = st.text_input("Institution / School (e.g., Siddaganga Institute of Technology)")
        edu_dates = st.text_input("Dates of Study (e.g., August 2023 - Present)")
        col1, col2 = st.columns([1, 2])
        with col1:
            grade_type = st.selectbox("Grade Type", ["CGPA", "Percentage"])
        with col2:
            grade_value = st.text_input("Value", help="e.g., 9.14 or 96.1")
        if st.form_submit_button("Add Education"):
            st.session_state.resume_data['education'].append({"degree": edu_degree, "institution": edu_institution, "dates": edu_dates, "grade_type": grade_type, "grade_value": grade_value})
            st.rerun()

elif page == "Projects":
    st.header("Projects")
    st.markdown("Add projects manually or use our AI assistants to auto-populate them.")
    st.subheader("🤖 AI GitHub Repo Analyzer")
    repo_url = st.text_input("Paste a GitHub repository URL to automatically add it to your resume")
    if st.button("Analyze and Add Repository"):
        if not API_KEY_CONFIGURED: st.error("Please set your GOOGLE_API_KEY in the terminal to use this feature.")
        elif not repo_url: st.warning("Please enter a GitHub URL.")
        else:
            with st.spinner("AI is analyzing the repository..."):
                details = analyze_github_repo(repo_url)
                if "error" in details: st.error(details["error"])
                else:
                    new_project = {"title": details.get('title', ''), "points": details.get('description', []), "techStack": details.get('tech_stack', ''), "repo_link": repo_url}
                    st.session_state.resume_data['projects'].append(new_project)
                    st.success(f"Successfully analyzed and added '{new_project.get('title')}' to your resume!")
    st.divider()
    st.subheader("Your Added Projects")
    if not st.session_state.resume_data['projects']: st.info("Your projects will appear here once you add them.")
    for i, project in enumerate(st.session_state.resume_data['projects']):
        if isinstance(project, dict):
            with st.container(border=True):
                st.write(f"**{project.get('title', 'Untitled Project')}**")
                st.button("Remove", key=f"remove_proj_{i}", on_click=remove_item, args=('projects', i))
    with st.form("new_project_form", clear_on_submit=True):
        st.subheader("Add a Project Manually")
        proj_title = st.text_input("Project Title")
        proj_points = st.text_area("Key points (one per line)", height=100)
        proj_tech = st.text_input("Technologies Used")
        proj_link = st.text_input("Repository Link")
        if st.form_submit_button("Add Manual Project"):
            if proj_title:
                st.session_state.resume_data['projects'].append({"title": proj_title, "points": [p.strip() for p in proj_points.split('\n') if p.strip()], "techStack": proj_tech, "repo_link": proj_link})
                st.rerun()
    st.divider()
    st.header("💡 AI Project Idea Generator")
    if st.button("Suggest Projects Based on My Skills"):
        if not API_KEY_CONFIGURED: st.error("Please set your GOOGLE_API_KEY in the terminal.")
        elif not st.session_state.resume_data['skills']: st.warning("Please add skills in the 'Skills' section first.")
        else:
            with st.spinner("AI is brainstorming project ideas..."):
                suggestions = suggest_projects(st.session_state.resume_data['skills'])
                if isinstance(suggestions, dict) and "error" in suggestions:
                    st.error(suggestions['error'])
                elif isinstance(suggestions, list):
                    st.session_state.ai_suggestions = suggestions
                else:
                    st.session_state.ai_suggestions = []
                    st.error("AI returned an unexpected format. Please try again.")
                    st.warning("Raw AI Output:"); st.code(str(suggestions))
    if st.session_state.ai_suggestions:
        st.write("### Here are some ideas (select to add/remove):")
        for i, proj in enumerate(st.session_state.ai_suggestions):
            with st.container(border=True):
                if isinstance(proj, dict):
                    is_added = any(isinstance(p, dict) and p.get('title') == proj.get('title') for p in st.session_state.resume_data['projects'])
                    st.checkbox(proj.get('title', f'Project {i+1}'), value=is_added, key=f"select_proj_{i}", on_change=toggle_project_selection, args=(proj,))
                    st.write("\n".join([f"- {p}" for p in proj.get('description', [])]))
                    st.write(f"**Tech:** {proj.get('tech_stack')}")
                else: st.write(str(proj))

elif page == "Internship Experience (Optional)":
    st.header("Internship Experience")
    st.info("This section is optional and can be left blank.")
    for i, intern in enumerate(st.session_state.resume_data['internships']):
        with st.container(border=True):
            st.write(f"**{intern.get('role')}** at {intern.get('company')}")
            st.button("Remove", key=f"remove_intern_{i}", on_click=remove_item, args=('internships', i))
    with st.form("new_intern_form", clear_on_submit=True):
        st.subheader("Add New Internship")
        intern_role = st.text_input("Role / Title (e.g., Software Engineering Intern)")
        intern_company = st.text_input("Company")
        intern_dates = st.text_input("Dates (e.g., May 2024 - Aug 2024)")
        intern_points = st.text_area("Key projects or responsibilities (one per line)")
        if st.form_submit_button("Add Internship"):
            st.session_state.resume_data['internships'].append({"role": intern_role, "company": intern_company, "dates": intern_dates, "responsibilities": [p.strip() for p in intern_points.split('\n') if p.strip()]})
            st.rerun()

elif page == "Work Experience (Optional)":
    st.header("Work Experience")
    st.info("This section is optional and can be left blank.")
    for i, job in enumerate(st.session_state.resume_data['experience']):
        with st.container(border=True):
            st.write(f"**{job.get('role')}** at {job.get('company')}")
            st.button("Remove", key=f"remove_exp_{i}", on_click=remove_item, args=('experience', i))
    with st.form("new_exp_form", clear_on_submit=True):
        st.subheader("Add New Experience")
        exp_role = st.text_input("Role / Title")
        exp_company = st.text_input("Company")
        exp_dates = st.text_input("Dates (e.g., Jan 2024 - Present)")
        exp_points = st.text_area("Key responsibilities (one per line)")
        if st.form_submit_button("Add Experience"):
            st.session_state.resume_data['experience'].append({"role": exp_role, "company": exp_company, "dates": exp_dates, "responsibilities": [p.strip() for p in exp_points.split('\n') if p.strip()]})
            st.rerun()

elif page == "Achievements & Leadership":
    st.header("Achievements")
    for i, ach in enumerate(st.session_state.resume_data['achievements']):
        st.text(f"• {ach}")
        st.button("Remove", key=f"remove_ach_{i}", on_click=remove_item, args=('achievements', i))
    with st.form("new_ach_form", clear_on_submit=True):
        ach_text = st.text_input("Add a new achievement")
        if st.form_submit_button("Add Achievement"):
            st.session_state.resume_data['achievements'].append(ach_text)
            st.rerun()
    st.divider()
    st.header("Leadership & Activities")
    for i, act in enumerate(st.session_state.resume_data['leadership']):
        st.text(f"• {act}")
        st.button("Remove", key=f"remove_act_{i}", on_click=remove_item, args=('leadership', i))
    with st.form("new_act_form", clear_on_submit=True):
        act_text = st.text_input("Add a new activity or leadership role")
        if st.form_submit_button("Add Activity"):
            st.session_state.resume_data['leadership'].append(act_text)
            st.rerun()

elif page == "Generate Resume":
    st.header("Finalize and Download")
    if not st.session_state.resume_data.get('achievements') and not st.session_state.resume_data.get('leadership'):
        st.info("💡 Your resume has empty space. Consider adding Achievements or Leadership roles to make it stand out!")
    if len(st.session_state.resume_data.get('projects', [])) < 2:
        st.warning("Recruiters love to see projects. Consider adding at least one more strong example to showcase your skills.")
    st.markdown("Your resume is ready! Click the button below to generate the PDF.")
    if st.button("Generate Resume PDF 🚀"):
        with st.spinner("Building your resume..."):
            final_resume_data = st.session_state.resume_data
            pdf_path = generate_pdf(final_resume_data)
            st.success("Your resume has been generated!")
            with open(pdf_path, "rb") as pdf_file:
                PDFbyte = pdf_file.read()
            st.download_button(label="Download Resume as PDF", data=PDFbyte, file_name=f"{final_resume_data.get('name', 'resume').replace(' ', '_')}_Resume.pdf", mime="application/octet-stream")

