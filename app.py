import streamlit as st
import pandas as pd
import google.generativeai as genai
import gspread
import json

st.set_page_config(page_title="SmartToolMatch", layout="wide", page_icon=":rocket:")

# --- Logo at the top (replace link with your own if desired!) ---
st.markdown(
    """
    <div style='text-align:center; margin-bottom:14px'>
        <img src="https://cdn-icons-png.flaticon.com/512/3468/3468379.png" width="68" style="margin-bottom:-7px;">
        <h1 style='margin-bottom:0;color:#1266c2;font-size:2.1rem;font-family:Segoe UI,Arial;'>SmartToolMatch</h1>
        <div style='font-size:18px;margin-top:0;color:#333;font-weight:500;'>Your AI App Discovery & Guidance Engine</div>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Sidebar ---
with st.sidebar:
    st.image("https://avatars.githubusercontent.com/u/103022833?s=280&v=4", width=90)
    st.markdown(
        "<b>Built by</b> [Vijay Kumar Balusa](https://www.linkedin.com/in/vijaykumarbalusa/)<br>_Connect with me on LinkedIn!_",
        unsafe_allow_html=True
    )
    st.markdown("---")
    st.markdown(
        """
        <div style="font-size:15px;padding-bottom:2px;"><b>About SmartToolMatch</b></div>
        <div style="color:#333;font-size:14px;">
        <ul style="margin-left:-14px;">
        <li><b>Instantly find the best AI apps</b> for any goal</li>
        <li>See both a “one-click” top app <b>and</b> a full workflow for your use case</li>
        <li>Recommendations are always up-to-date from a curated database</li>
        <li>Powered by Google Gemini, Streamlit, and Google Sheets</li>
        <li><b>Built for:</b> creators, students, jobseekers, and anyone curious about the best new AI tools</li>
        </ul>
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown("---")
    st.info("💡 Try: 'Plan a trip', 'Generate marketing images', 'Automate my resume', etc.")

# --- Sheets & Gemini Setup ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
gemini_model = genai.GenerativeModel("gemini-1.5-pro")
try:
    service_account_info = json.loads(st.secrets["GSPREAD_SERVICE_ACCOUNT"])
    gc = gspread.service_account_from_dict(service_account_info)
    SHEET_URL = "https://docs.google.com/spreadsheets/d/13KVDHGDG7xITg7gLor1LphhSHJEI-_LGmy3NDUVDNi8"
    worksheet = gc.open_by_url(SHEET_URL).sheet1
    tools_data = worksheet.get_all_records()
    tools_df = pd.DataFrame(tools_data)
except Exception as e:
    st.error(f"Google Sheets connection failed: {e}")
    st.stop()

# --- UI: Input ---
st.markdown("### What do you want to achieve?")
user_goal = st.text_input("Describe your task or goal (e.g., Plan a trip, Generate a resume, Create a presentation)")

if user_goal:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🔎 Best App Recommendation")
        with st.spinner("Gemini is picking the top apps for you..."):
            tools_string = "\n".join([
                f"{r['Tool Name']} ({r['Type']}) - {r['Description']}" for _, r in tools_df.iterrows()
            ])
            prompt = (
                f"A user wants to: {user_goal}.\n"
                f"Available tools:\n{tools_string}\n\n"
                "1. Briefly explain what this task is.\n"
                "2. Suggest (if possible): up to one best FREE, one best PAID, and one best UNIVERSAL tool (from the list) "
                "that can do the task directly. If not available for a type, say so.\n"
                "3. For each, give: Name (with link), brief description, and what makes it good for this goal.\n"
                "4. End with a unique Gemini Quick Tip for this task.\n"
                "Reply in markdown, with clear bullet points and links."
            )
            try:
                response1 = gemini_model.generate_content(prompt)
                answer1 = response1.text.strip()
            except Exception as e:
                answer1 = f"Gemini API error: {e}"
        st.markdown(answer1)

    with col2:
        st.markdown("#### 🤖 Step-by-Step AI Guide")
        with st.spinner("Gemini is creating your workflow..."):
            prompt2 = (
                f"A user wants to: {user_goal}.\n"
                f"Available tools:\n{tools_string}\n\n"
                "Create a 4-7 step actionable workflow for this goal. For each step, recommend the best single AI tool from the list (name, link, description). "
                "If no perfect tool, suggest the closest or a universal AI (ChatGPT, Gemini, Claude, etc.). "
                "Finish with a practical tip for success at the end. Use markdown and keep it very readable."
            )
            try:
                response2 = gemini_model.generate_content(prompt2)
                answer2 = response2.text.strip()
            except Exception as e:
                answer2 = f"Gemini API error: {e}"
        st.markdown(answer2)

    st.success("Compare a direct top app and a step-by-step workflow—choose what fits your style best!")

else:
    st.info("Enter your goal above to see both instant app recommendations and step-by-step guidance!")

st.markdown("---")
st.caption("© 2025 SmartToolMatch • Built with ❤️ by [Vijay Kumar Balusa](https://www.linkedin.com/in/vijaykumarbalusa/) • Powered by Gemini & Google Sheets")
