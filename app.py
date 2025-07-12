import streamlit as st
import pandas as pd
import google.generativeai as genai
import gspread
import json
from fuzzywuzzy import fuzz

st.set_page_config(page_title="SmartToolMatch", layout="wide", page_icon="🚀")

# -- Custom CSS for Modern Look --
st.markdown(
    """
    <style>
    body {font-family: 'Inter', 'Segoe UI', Arial;}
    .stApp {background: #f5f6fa;}
    .tool-card {
        background: white;
        border-radius: 18px;
        box-shadow: 1px 2px 14px #ececec;
        margin-bottom: 18px;
        padding: 18px 20px;
        transition: box-shadow 0.2s;
        border: 1px solid #f3f3f3;
    }
    .tool-card:hover {box-shadow: 2px 4px 22px #cce7ff;}
    .workflow-step {
        background: linear-gradient(90deg,#1e90ff14 0%,#e3eefd 100%);
        border-radius: 16px;
        margin-bottom: 10px;
        padding: 15px 24px;
        font-size: 21px;
        font-weight: 600;
        color: #2266bb;
        box-shadow: 1px 2px 10px #ececec;
    }
    .step-number {
        background: #1e90ff;
        color: white;
        border-radius: 50%;
        width: 32px;
        height: 32px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 12px;
        font-size: 17px;
    }
    .linkedin-cta {
        background: #eaf5ff;
        color: #1567ad;
        border-radius: 10px;
        padding: 10px;
        text-align:center;
        font-size:17px;
        margin-bottom:16px;
        font-weight: 500;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0% {box-shadow: 0 0 0 0 #85baff;}
      70% {box-shadow: 0 0 0 8px #b6e0ff88;}
      100% {box-shadow: 0 0 0 0 #eaf5ff;}
    }
    </style>
    """, unsafe_allow_html=True
)

# LOGO & TITLE
st.markdown(
    """
    <div style='text-align:center; margin-bottom:16px'>
        <img src="https://img.icons8.com/emoji/96/rocket.png" width="64">
        <h1 style='margin-bottom:0;color:#1966d2;font-size:2.7rem;font-family:Segoe UI,Arial;'>SmartToolMatch 🚀</h1>
        <div style='font-size:23px;margin-top:0;color:#222;font-weight:500;'>Your AI Workflow and Tool Discovery Assistant</div>
    </div>
    """, unsafe_allow_html=True
)

# SIDEBAR
with st.sidebar:
    st.image("https://media.licdn.com/dms/image/D5603AQHOUycbDkGsvQ/profile-displayphoto-shrink_400_400/0/1706542228345?e=1722470400&v=beta&t=twshjtbBkJG3xIzR6o8BIB8NPjR91FSBUpvCuKQch2E", width=108)
    st.markdown(
        """
        <div class="linkedin-cta">
            <a href='https://www.linkedin.com/in/vijaykumarbalusa/' target='_blank' style='text-decoration:none;'>
            👉 Connect with the creator on <b>LinkedIn</b>!<br>
            <span style='font-size:15px;'>Let's network and talk AI projects!</span>
            </a>
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown("---")
    st.markdown("""
    <span style='font-size:19px;font-weight:500;color:#1966d2;'>How does it work?</span>
    <ul style='font-size:15px;margin-left:-14px;'>
        <li>Describe your goal (e.g. "Create a marketing campaign")</li>
        <li>Get actionable workflow steps</li>
        <li>Discover best-matched AI tools for every step</li>
    </ul>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.info("💡 Try: 'Edit podcast audio', 'Design a presentation', 'Summarize research papers', 'Automate data scraping'")

# GOOGLE SHEETS & GEMINI SETUP
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    gemini_model = genai.GenerativeModel("gemini-1.5-pro")
    service_account_info = json.loads(st.secrets["GSPREAD_SERVICE_ACCOUNT"])
    gc = gspread.service_account_from_dict(service_account_info)
    SHEET_URL = "https://docs.google.com/spreadsheets/d/13KVDHGDG7xITg7gLor1LphhSHJEI-_LGmy3NDUVDNi8/edit?usp=sharing"  
    worksheet = gc.open_by_url(SHEET_URL).sheet1
    tools_data = worksheet.get_all_records()
    tools_df = pd.DataFrame(tools_data)
except Exception as e:
    st.error(f"Error loading AI tools: {e}")
    st.stop()

# USER INPUTS
user_goal = st.text_input(
    "What do you want to achieve?",
    placeholder="e.g., Automate blog writing, Create a video, Generate marketing images..."
)
tool_type_filter = st.selectbox("Filter by Tool Type:", options=["All"] + sorted(tools_df["Type"].dropna().unique()))
search_tool_name = st.text_input("Search tools by name (optional):")

# WORKFLOW
if user_goal:
    with st.spinner("AI is crafting your workflow..."):
        prompt = f"Break down the following user goal into 3-6 actionable workflow steps. Goal: {user_goal}"
        try:
            response = gemini_model.generate_content(prompt)
            steps = [s.strip().lstrip("1234567890. ").capitalize()
                     for s in response.text.split("\n") if s.strip()]
            if not steps:
                raise ValueError("Gemini response is empty. Try rephrasing your goal.")
        except Exception as e:
            st.error(f"Gemini API error: {e}")
            st.stop()

    st.markdown("### 📝 <span style='color:#1966d2;font-size:1.2em;'>Your Personalized Workflow & AI Tools</span>", unsafe_allow_html=True)

    for i, step in enumerate(steps, 1):
        st.markdown(f"""
        <div class="workflow-step">
            <span class="step-number">{i}</span> {step}
        </div>
        """, unsafe_allow_html=True)

        def match_tools(step, tools_df):
            first_word = step.split()[0].lower() if step.split() else ""
            if first_word:
                try:
                    matches = tools_df[tools_df["Category"].str.lower().str.contains(first_word, na=False, regex=False)]
                except Exception:
                    matches = pd.DataFrame()
            else:
                matches = pd.DataFrame()
            if matches.empty:
                threshold = 60
                tools_df["fuzz_ratio"] = tools_df["Category"].apply(
                    lambda x: fuzz.partial_ratio(x.lower(), step.lower()) if pd.notna(x) else 0
                )
                matches = tools_df[tools_df["fuzz_ratio"] >= threshold]
            return matches

        matched_tools = match_tools(step, tools_df)
        universal_tools = tools_df[tools_df["Type"].str.lower() == "universal"]

        if tool_type_filter != "All":
            matched_tools = matched_tools[matched_tools["Type"] == tool_type_filter]
            universal_tools = universal_tools[universal_tools["Type"] == tool_type_filter]
        if search_tool_name:
            matched_tools = matched_tools[matched_tools["Tool Name"].str.lower().str.contains(search_tool_name.lower(), na=False)]
            universal_tools = universal_tools[universal_tools["Tool Name"].str.lower().str.contains(search_tool_name.lower(), na=False)]

        tools_to_show = pd.concat([matched_tools, universal_tools]).drop_duplicates("Tool Name")

        if not tools_to_show.empty:
            for _, row in tools_to_show.iterrows():
                logo_url = ""
                if row["Tool Name"].lower() == "chatgpt":
                    logo_url = "https://cdn.openai.com/chatgpt/favicon-32x32.png"
                elif row["Tool Name"].lower() == "gemini":
                    logo_url = "https://www.gstatic.com/lamda/images/gemini-icon-64.png"
                elif row["Tool Name"].lower() == "claude":
                    logo_url = "https://avatars.githubusercontent.com/u/103022833?s=280&v=4"
                elif row["Tool Name"].lower() == "midjourney":
                    logo_url = "https://cdn.worldvectorlogo.com/logos/midjourney.svg"
                elif row["Tool Name"].lower() == "notion ai":
                    logo_url = "https://cdn.icon-icons.com/icons2/3914/PNG/512/notion_logo_icon_249965.png"
                # ...add more as you like!

                st.markdown(
                    f"""
                    <div class='tool-card'>
                        {'<img src="'+logo_url+'" width="28" style="vertical-align:middle;margin-right:7px;">' if logo_url else ''}
                        <b><a href="{row['Link']}" target="_blank">{row['Tool Name']}</a></b>
                        <br><span style="color:#2668bb;font-size:15px;"><i>Type:</i> {row['Type']} &nbsp;|&nbsp; <i>Category:</i> {row['Category']}</span>
                        <br>{row['Description']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.warning("No tools found for this step. Try adjusting filter or search.")

else:
    st.info("Enter your goal above to get started!")

st.markdown("""
---
<center>
    <span style='font-size:15px;color:#555;'>
        © 2025 SmartToolMatch • Built with ❤️ by <a href="https://www.linkedin.com/in/vijaykumarbalusa/" target="_blank">Vijay Kumar Balusa</a><br>
        Powered by Gemini, Google Sheets, and Streamlit
    </span>
</center>
""", unsafe_allow_html=True)
