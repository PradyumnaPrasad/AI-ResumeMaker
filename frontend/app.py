import streamlit as st
import os
import requests
from modules.resume_generator import generate_pdf

# --- CONFIGURATION ---
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="AI Resume Maker", page_icon="📄", layout="centered")

# --- SESSION STATE INITIALIZATION ---
def initialize_session_state():
    if 'token' not in st.session_state: st.session_state.token = None
    if 'resume_data' not in st.session_state: st.session_state.resume_data = {}
    if 'page' not in st.session_state: st.session_state.page = "Import Resume"
    if 'ai_suggestions' not in st.session_state: st.session_state.ai_suggestions = []

initialize_session_state()

# --- API CLIENT FUNCTIONS ---
def api_request(method, endpoint, json_data=None, files=None):
    headers = {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}
    try:
        response = None
        if method.lower() == 'post': response = requests.post(f"{BACKEND_URL}{endpoint}", headers=headers, json=json_data, files=files)
        elif method.lower() == 'put': response = requests.put(f"{BACKEND_URL}{endpoint}", headers=headers, json=json_data)
        elif method.lower() == 'get': response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        if e.response is not None:
             st.error(f"API Error ({e.response.status_code}): {e.response.json().get('detail', 'An error occurred.')}")
        else:
            st.error(f"API request failed: {e}")
        return None

def fetch_resume_data():
    response = api_request('get', '/resume/')
    if response and response.status_code == 200:
        st.session_state.resume_data = response.json()
        for key in ['education', 'projects', 'internships', 'experience', 'skills', 'achievements', 'leadership']:
            if key not in st.session_state.resume_data or st.session_state.resume_data[key] is None:
                st.session_state.resume_data[key] = []
        if 'section_order' not in st.session_state.resume_data or not st.session_state.resume_data['section_order']:
            st.session_state.resume_data['section_order'] = ["Summary", "Education", "Projects", "Skills", "Internship Experience", "Work Experience", "Achievements", "Activities & Leadership"]

def save_resume_data():
    if st.session_state.token:
        response = api_request('put', '/resume/', json_data=st.session_state.resume_data)
        if response and response.status_code == 200:
            st.toast("Progress Saved!", icon="✅")

# --- UI HELPER FUNCTIONS ---
def remove_item(category, index):
    if 0 <= index < len(st.session_state.resume_data[category]):
        st.session_state.resume_data[category].pop(index)
        st.toast("Item removed!", icon="🗑️")

def toggle_project_selection(project_data):
    project_titles = [p.get('title') for p in st.session_state.resume_data.get('projects', []) if isinstance(p, dict)]
    is_added = project_data.get('title') in project_titles
    if is_added:
        st.session_state.resume_data['projects'] = [p for p in st.session_state.resume_data['projects'] if not (isinstance(p, dict) and p.get('title') == project_data.get('title'))]
    else:
        new_project = {"title": project_data.get('title', ''), "points": project_data.get('description', []), "techStack": project_data.get('tech_stack', ''), "repo_link": ""}
        st.session_state.resume_data.setdefault('projects', []).append(new_project)

# --- UI COMPONENTS ---

def show_login_signup_ui():
    st.markdown("<style>.stApp { background-color: #000000; }</style>", unsafe_allow_html=True)
    st.title("Welcome to the AI Resume Maker")
    st.info("Log in or create an account to build and save your resume.")
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        with st.container(border=True):
            login_tab, signup_tab = st.tabs(["Login", "Sign Up"])
            with login_tab:
                with st.form("login_form"):
                    email = st.text_input("Email", placeholder="you@example.com")
                    password = st.text_input("Password", type="password", placeholder="••••••••")
                    if st.form_submit_button("Login", use_container_width=True, type="primary"):
                        response = requests.post(f"{BACKEND_URL}/token/", data={"username": email, "password": password})
                        if response and response.status_code == 200:
                            st.session_state.token = response.json()['access_token']
                            fetch_resume_data()
                            st.rerun()
                        else: st.error("Invalid email or password.")
            with signup_tab:
                with st.form("signup_form"):
                    email = st.text_input("Email", placeholder="you@example.com")
                    password = st.text_input("Create Password", type="password", placeholder="••••••••")
                    if st.form_submit_button("Sign Up", use_container_width=True):
                        response = requests.post(f"{BACKEND_URL}/signup/", json={"email": email, "password": password})
                        if response and response.status_code == 200: st.success("Account created! Please log in.")
                        else: st.error(f"Failed to create account: {response.json().get('detail')}")

def show_main_app_ui():
    page_options = ["Import Resume", "Personal Info", "Skills", "Summary", "Education", "Projects", "Internship Experience (Optional)", "Work Experience (Optional)", "Achievements & Leadership", "Generate Resume"]
    st.sidebar.title("Resume Sections")
    st.session_state.page = st.sidebar.radio("Go to", page_options, key="page_nav", index=page_options.index(st.session_state.page))
    st.sidebar.markdown("---")
    if st.sidebar.button("Save Progress", type="primary"): save_resume_data()
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.resume_data = {}
        st.rerun()
    st.title("📄 AI-Powered Resume Maker")
    st.info("Fill only the sections you require. Empty sections will be hidden automatically.")
    render_page(st.session_state.page)
    current_page_index = page_options.index(st.session_state.page)
    col1, _, col3 = st.columns([1, 3, 1])
    with col1:
        if current_page_index > 0:
            if st.button("Previous"):
                save_resume_data()
                st.session_state.page = page_options[current_page_index - 1]
                st.rerun()
    with col3:
        if current_page_index < len(page_options) - 1:
            if st.button("Next", type="primary"):
                save_resume_data()
                st.session_state.page = page_options[current_page_index + 1]
                st.rerun()

def render_page(page):
    page_map = {p: globals()[f"render_{p.lower().replace(' ', '_').replace('&', 'and').replace('(optional)','').strip()}_page"] for p in ["Import Resume", "Personal Info", "Skills", "Summary", "Education", "Projects", "Achievements & Leadership", "Generate Resume"]}
    page_map["Internship Experience (Optional)"] = lambda: render_experience_page("Internship")
    page_map["Work Experience (Optional)"] = lambda: render_experience_page("Work")
    with st.container(border=True):
        page_map[page]()

# --- DEDICATED PAGE RENDERING FUNCTIONS ---
def render_import_resume_page():
    st.header("🚀 Import Your Existing Resume")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file and st.button("Parse and Fill Resume"):
        with st.spinner("AI is reading your resume..."):
            files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            response = api_request('post', '/ai/parse-resume/', files=files)
            if response and response.status_code == 200:
                st.session_state.resume_data = response.json()
                for key in ['education', 'projects', 'internships', 'experience', 'skills', 'achievements', 'leadership']:
                    if key not in st.session_state.resume_data or st.session_state.resume_data[key] is None:
                        st.session_state.resume_data[key] = []
        st.success("Resume successfully parsed!"); st.balloons()
        st.rerun()

def render_personal_info_page():
    st.header("Personal Information")
    data = st.session_state.resume_data
    data['name'] = st.text_input("Full Name", data.get('name', ''))
    c1, c2 = st.columns(2); data['email'] = c1.text_input("Email", data.get('email', '')); data['phone'] = c2.text_input("Phone Number", data.get('phone', ''))
    c3, c4 = st.columns(2); data['linkedin'] = c3.text_input("LinkedIn URL", data.get('linkedin', '')); data['github'] = c4.text_input("GitHub URL", data.get('github', ''))
    data['leetcode'] = st.text_input("LeetCode URL", data.get('leetcode', ''))

def render_skills_page():
    st.header("Skills")
    raw_skills_input = ", ".join([s.get('details', '') for s in st.session_state.resume_data.get('skills', [])])
    raw_skills = st.text_area("Enter all your skills, separated by commas", value=raw_skills_input)
    if st.button("Categorize Skills with AI ✨"):
        if not raw_skills: st.warning("Please enter at least one skill.")
        else:
            with st.spinner("AI is organizing..."):
                response = api_request('post', '/ai/categorize-skills/', json_data=raw_skills.split(','))
                if response and response.status_code == 200:
                    st.session_state.resume_data['skills'] = response.json()
                    st.toast("Skills categorized!"); st.rerun()
    if st.session_state.resume_data.get('skills'):
        st.write("### Categorized Skills:")
        for cat in st.session_state.resume_data['skills']: st.markdown(f"**{cat.get('category')}:** {cat.get('details')}")

def render_summary_page():
    st.header("Professional Summary")
    st.session_state.resume_data['summary'] = st.text_area("Your Summary", st.session_state.resume_data.get('summary', ''), height=200)
    st.subheader("✨ AI Assistant")
    job_desc = st.text_area("Optional: Paste a target job description")
    if st.button("Generate Summary with AI"):
        if not st.session_state.resume_data.get('skills'): st.warning("Please add skills first.")
        else:
            with st.spinner("AI is crafting your summary..."):
                payload = {"skills": st.session_state.resume_data['skills'], "job_description": job_desc}
                response = api_request('post', '/ai/generate-summary/', json_data=payload)
                if response and response.status_code == 200:
                    st.session_state.resume_data['summary'] = response.json().get('summary')
                    st.toast("Summary generated!"); st.rerun()

def render_education_page():
    st.header("Education")
    for i, edu in enumerate(st.session_state.resume_data.get('education', [])):
        with st.container(border=True):
            st.write(f"**{edu.get('degree')}** from {edu.get('institution')}")
            st.button("Remove", key=f"remove_edu_{i}", on_click=remove_item, args=('education', i))
    with st.form("new_edu_form", clear_on_submit=True):
        st.subheader("Add New Education")
        degree, inst = st.text_input("Degree / Course"), st.text_input("Institution")
        dates = st.text_input("Dates of Study")
        c1,c2 = st.columns([1,2]); grade_type = c1.selectbox("Grade Type", ["CGPA", "Percentage"]); grade_val = c2.text_input("Value")
        if st.form_submit_button("Add Education"):
            st.session_state.resume_data.setdefault('education',[]).append({"degree":degree, "institution":inst, "dates":dates, "grade_type":grade_type, "grade_value":grade_val})
            st.toast("Education added!"); st.rerun()

def render_projects_page():
    st.header("Projects")
    st.subheader("🤖 AI GitHub Repo Analyzer")
    repo_url = st.text_input("Paste a GitHub repository URL to auto-add")
    if st.button("Analyze and Add Repository"):
        if not repo_url: st.warning("Please enter a URL.")
        else:
            with st.spinner("AI is analyzing..."):
                resp = api_request('post', '/ai/analyze-github/', json_data={"url": repo_url})
                if resp and resp.status_code == 200:
                    details = resp.json()
                    new_proj = {"title": details.get('title',''), "points": details.get('description',[]), "techStack": details.get('tech_stack',''), "repo_link": repo_url}
                    st.session_state.resume_data.setdefault('projects',[]).append(new_proj)
                    st.success(f"Added '{new_proj.get('title')}'!")
    st.divider()
    st.subheader("Your Added Projects")
    for i, p in enumerate(st.session_state.resume_data.get('projects', [])):
        with st.container(border=True): st.write(f"**{p.get('title')}**"); st.button("Remove", key=f"rem_proj_{i}", on_click=remove_item, args=('projects', i))
    with st.form("new_project_form", clear_on_submit=True):
        st.subheader("Add a Project Manually")
        title, points = st.text_input("Project Title"), st.text_area("Key points")
        tech, link = st.text_input("Technologies (Tech Stack)"), st.text_input("Repository Link")
        if st.form_submit_button("Add Manual Project"):
            st.session_state.resume_data.setdefault('projects',[]).append({"title":title, "points":[p.strip() for p in points.split('\n') if p], "techStack":tech, "repo_link":link})
            st.toast("Project added!"); st.rerun()
    st.divider()
    st.header("💡 AI Project Idea Generator")
    if st.button("Suggest Projects"):
        if not st.session_state.resume_data.get('skills'): st.warning("Please add skills first.")
        else:
            with st.spinner("AI is brainstorming..."):
                resp = api_request('post', '/ai/suggest-projects/', json_data={"skills": st.session_state.resume_data['skills']})
                if resp and resp.status_code == 200: st.session_state.ai_suggestions = resp.json(); st.toast("Suggestions loaded!")
    if st.session_state.ai_suggestions:
        st.write("### AI Ideas (select to add/remove):")
        for i, proj in enumerate(st.session_state.ai_suggestions):
            with st.container(border=True):
                if isinstance(proj, dict):
                    is_added = any(isinstance(p, dict) and p.get('title') == proj.get('title') for p in st.session_state.resume_data['projects'])
                    st.checkbox(proj.get('title',''), value=is_added, key=f"sel_proj_{i}", on_change=toggle_project_selection, args=(proj,))
                    st.write("\n".join([f"- {p}" for p in proj.get('description',[])])); st.write(f"**Tech:** {proj.get('tech_stack')}")

def render_experience_page(exp_type):
    key = "internships" if exp_type == "Internship" else "experience"
    st.header(f"{exp_type} Experience")
    for i, item in enumerate(st.session_state.resume_data.get(key, [])):
        with st.container(border=True): st.write(f"**{item.get('role')}** at {item.get('company')}"); st.button("Remove", key=f"rem_{key}_{i}", on_click=remove_item, args=(key, i))
    with st.form(f"new_{key}_form", clear_on_submit=True):
        st.subheader(f"Add New {exp_type}")
        role, company = st.text_input("Role / Title"), st.text_input("Company")
        dates, points = st.text_input("Dates"), st.text_area("Responsibilities (one per line)")
        if st.form_submit_button(f"Add {exp_type}"):
            st.session_state.resume_data.setdefault(key,[]).append({"role":role, "company":company, "dates":dates, "responsibilities":[p.strip() for p in points.split('\n') if p]})
            st.toast(f"{exp_type} added!"); st.rerun()

def render_achievements_and_leadership_page():
    st.header("Achievements")
    for i, ach in enumerate(st.session_state.resume_data.get('achievements', [])):
        st.text(f"• {ach}"); st.button("Remove", key=f"rem_ach_{i}", on_click=remove_item, args=('achievements', i))
    with st.form("new_ach_form", clear_on_submit=True):
        ach_text = st.text_input("Add new achievement")
        if st.form_submit_button("Add Achievement"): st.session_state.resume_data.setdefault('achievements',[]).append(ach_text); st.toast("Achievement added!"); st.rerun()
    st.divider()
    st.header("Leadership & Activities")
    for i, act in enumerate(st.session_state.resume_data.get('leadership', [])):
        st.text(f"• {act}"); st.button("Remove", key=f"rem_act_{i}", on_click=remove_item, args=('leadership', i))
    with st.form("new_act_form", clear_on_submit=True):
        act_text = st.text_input("Add new activity")
        if st.form_submit_button("Add Activity"): st.session_state.resume_data.setdefault('leadership',[]).append(act_text); st.toast("Activity added!"); st.rerun()

def render_generate_resume_page():
    st.header("Finalize and Download")
    st.subheader("Arrange Sections")
    all_sections = ["Summary", "Education", "Projects", "Skills", "Internship Experience", "Work Experience", "Achievements", "Activities & Leadership"]
    key_map = {s: s.lower().replace(" ", "_").replace("&", "and") for s in all_sections}
    available = [s for s in all_sections if st.session_state.resume_data.get(key_map[s], [])]
    current_order = [s for s in st.session_state.resume_data.get('section_order', available) if s in available]
    for s in available:
        if s not in current_order: current_order.append(s)
    ordered_sections = st.multiselect("Set section order:", options=all_sections, default=current_order, label_visibility="collapsed")
    st.session_state.resume_data['section_order'] = ordered_sections
    st.divider()
    if st.button("Generate Resume PDF 🚀", use_container_width=True, type="primary"):
        with st.spinner("Building your resume..."):
            pdf_path = generate_pdf(st.session_state.resume_data)
            with open(pdf_path, "rb") as pdf_file: PDFbyte = pdf_file.read()
            st.download_button(label="Download Resume as PDF", data=PDFbyte, file_name=f"{st.session_state.resume_data.get('name','resume').replace(' ','_')}_Resume.pdf", mime="application/octet-stream", use_container_width=True)

# --- MAIN APPLICATION LOGIC ---
if st.session_state.token is None:
    show_login_signup_ui()
else:
    show_main_app_ui()