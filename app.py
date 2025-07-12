import streamlit as st
import pandas as pd
import google.generativeai as genai
import gspread
import json
from fuzzywuzzy import fuzz

st.set_page_config(page_title="SmartToolMatch", layout="wide")
st.markdown(
    """
    <div style='text-align:center; margin-bottom:6px'>
        <span style="font-size:2.7rem;">🚀</span>
        <h1 style='margin-bottom:0;color:#1266c2;font-size:2.2rem;font-family:Segoe UI,Arial;'>
            SmartToolMatch
        </h1>
        <div style='font-size:18px;margin-top:0;color:#333;font-weight:500;'>Your AI Workflow & Tool Discovery Assistant</div>
    </div>
    """, unsafe_allow_html=True
)

# --- Sidebar with profile & LinkedIn ---
with st.sidebar:
    st.image("https://avatars.githubusercontent.com/u/103022833?s=280&v=4", width=100)
    st.markdown(
        """
        <div style="font-size:17px;font-weight:600;">
        Built by <a href='https://www.linkedin.com/in/vijaykumarbalusa/' target='_blank'>Vijay Kumar Balusa</a>
        </div>
        <div style='background:#eaf5ff;color:#1567ad;border-radius:10px;padding:8px;text-align:center;margin-bottom:12px;font-size:15px;font-weight:500;animation:pulse 2s infinite;'>
            👉 <a href='https://www.linkedin.com/in/vijaykumarbalusa/' target='_blank' style='color:#1567ad;text-decoration:underline;'>Connect with me on LinkedIn</a>
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown("---")
    st.markdown(
        """
        <b>How does it work?</b>
        <ol style='font-size:15px;'>
        <li>Describe your goal (e.g., "Edit a podcast", "Design a logo")</li>
        <li>Get actionable workflow steps</li>
        <li>Discover the best AI tools for each step</li>
        </ol>
        """, unsafe_allow_html=True
    )
    st.info("💡 Try: 'Generate marketing images', 'Automate resumes', 'Summarize research papers'")

# --- 1. Gemini & Google Sheets Setup ---
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

# --- 2. User Inputs ---
user_goal = st.text_input(
    "What do you want to achieve? (e.g., 'Create a content marketing plan')",
    placeholder="Describe your goal, e.g. 'Plan a trip to Europe'"
)
tool_type_filter = st.selectbox("Filter by Tool Type:", options=["All"] + sorted(tools_df["Type"].dropna().unique()))
search_tool_name = st.text_input("Search tools by name (optional):")

# --- 3. Generate Workflow ---
if user_goal:
    with st.spinner("✨ Generating workflow steps..."):
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

    st.markdown("## 📝 Your Personalized Workflow & AI Tools")

    for i, step in enumerate(steps, 1):
        st.markdown(
            f"""
            <div style='background:#f0f4ff;padding:12px 18px;border-radius:13px;margin-bottom:4px;font-size:17px;'>
            <span style='font-weight:600;color:#1366c2;'>Step {i}:</span> <span style='color:#193458;'>{step}</span>
            </div>
            """, unsafe_allow_html=True
        )

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

        # Filter by type/name
        if tool_type_filter != "All":
            matched_tools = matched_tools[matched_tools["Type"] == tool_type_filter]
            universal_tools = universal_tools[universal_tools["Type"] == tool_type_filter]
        if search_tool_name:
            matched_tools = matched_tools[matched_tools["Tool Name"].str.lower().str.contains(search_tool_name.lower(), na=False)]
            universal_tools = universal_tools[universal_tools["Tool Name"].str.lower().str.contains(search_tool_name.lower(), na=False)]

        tools_to_show = pd.concat([matched_tools, universal_tools]).drop_duplicates("Tool Name")

        if not tools_to_show.empty:
            for _, row in tools_to_show.iterrows():
                st.markdown(
                    f"""- <span style='font-weight:600;'><a href="{row['Link']}" target="_blank">{row['Tool Name']}</a></span> 
                    <span style='color:#356db1;font-size:14px;'>[{row['Type']}]</span>  
                    <br><span style='color:#193458;font-size:14px;'>{row['Description']}</span>""",
                    unsafe_allow_html=True
                )
        else:
            st.warning("No tools found for this step. Try changing the filter or search.")

else:
    st.info("Enter your goal above to get started!")

st.markdown("---")
st.caption("© 2025 SmartToolMatch • Built with ❤️ by [Vijay Kumar Balusa](https://www.linkedin.com/in/vijaykumarbalusa/) • Powered by Gemini, Google Sheets, and Streamlit")
