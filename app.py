import streamlit as st
import pandas as pd
import google.generativeai as genai
import gspread
import json
from fuzzywuzzy import fuzz

st.set_page_config(page_title="SmartToolMatch", layout="wide", page_icon="🚀")

# --- Modern, readable CSS ---
st.markdown("""
<style>
html, body, .stApp {background: #f6f8fa;}
.tool-card {
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 2px 16px #e3e3e3;
    margin-bottom: 18px;
    padding: 16px 20px;
    border: 1px solid #e1e5eb;
    transition: box-shadow 0.2s;
}
.tool-card:hover {box-shadow: 0 4px 28px #aee3fd44;}
.workflow-step {
    background: linear-gradient(90deg,#d0eaff 0%,#fff 100%);
    border-radius: 14px;
    margin-bottom: 12px;
    padding: 15px 22px;
    font-size: 20px;
    font-weight: 600;
    color: #1760a7;
    box-shadow: 1px 2px 10px #e4ecf7;
}
.step-number {
    background: #1976d2;
    color: #fff;
    border-radius: 50%;
    width: 28px;
    height: 28px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    margin-right: 10px;
    font-size: 16px;
}
.linkedin-cta {
    background: #eaf5ff;
    color: #1567ad;
    border-radius: 10px;
    padding: 10px;
    text-align:center;
    font-size:16px;
    margin-bottom:14px;
    font-weight: 500;
    animation: pulse 2s infinite;
}
@keyframes pulse {
  0% {box-shadow: 0 0 0 0 #8ddcff;}
  70% {box-shadow: 0 0 0 8px #b6e0ff88;}
  100% {box-shadow: 0 0 0 0 #eaf5ff;}
}
h1, h2, h3, h4 {color: #1266c2 !important;}
[data-testid="stAppViewContainer"] { background: #f6f8fa; }
</style>
""", unsafe_allow_html=True)

# --- Logo & Title (emoji for compatibility)
st.markdown(
    """
    <div style='text-align:center; margin-bottom:10px'>
        <span style="font-size:3.0rem;">🚀</span>
        <h1 style='margin-bottom:0;color:#1266c2;font-size:2.4rem;font-family:Segoe UI,Arial;'>
            SmartToolMatch
        </h1>
        <div style='font-size:20px;margin-top:0;color:#333;font-weight:500;'>Your AI Workflow and Tool Discovery Assistant</div>
    </div>
    """, unsafe_allow_html=True
)

# --- Sidebar with avatar ---
with st.sidebar:
    st.image("https://avatars.githubusercontent.com/u/103022833?s=280&v=4", width=102)
    st.markdown("""
        <div class="linkedin-cta">
            <a href='https://www.linkedin.com/in/vijaykumarbalusa/' target='_blank' style='text-decoration:none;'>
            👉 Connect with the creator on <b>LinkedIn</b>!
            <br>
            <span style='font-size:14px;'>Let's network and talk AI projects!</span>
            </a>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
        <span style='font-size:17px;font-weight:500;color:#1666cc;'>How does it work?</span>
        <ul style='font-size:14px;margin-left:-10px;'>
            <li>Describe your goal (e.g. "Generate marketing images")</li>
            <li>Get step-by-step workflow, each step explained</li>
            <li>Discover best-matched AI tools for every step</li>
        </ul>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.info("💡 Try: 'Edit podcast audio', 'Design a presentation', 'Summarize research papers', 'Automate data scraping'")

# --- Sheets & Gemini Setup ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    gemini_model = genai.GenerativeModel("gemini-1.5-pro")
    service_account_info = json.loads(st.secrets["GSPREAD_SERVICE_ACCOUNT"])
    gc = gspread.service_account_from_dict(service_account_info)
    SHEET_URL = "https://docs.google.com/spreadsheets/d/13KVDHGDG7xITg7gLor1LphhSHJEI-_LGmy3NDUVDNi8"
    worksheet = gc.open_by_url(SHEET_URL).sheet1
    tools_data = worksheet.get_all_records()
    tools_df = pd.DataFrame(tools_data)
except Exception as e:
    st.error(f"Error loading AI tools: {e}")
    st.stop()

# --- User Inputs ---
user_goal = st.text_input(
    "What do you want to achieve?",
    placeholder="e.g., Automate blog writing, Create a video, Generate marketing images..."
)
tool_type_filter = st.selectbox("Filter by Tool Type:", options=["All"] + sorted(tools_df["Type"].dropna().unique()))
search_tool_name = st.text_input("Search tools by name (optional):")

# --- Workflow Steps and Tool Cards (GUARANTEED: markdown only, never code blocks!) ---
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

    st.markdown("### 📝 <span style='color:#1166d1;font-size:1.13em;'>Your Personalized Workflow & AI Tools</span>", unsafe_allow_html=True)

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

        # Fallback: if nothing matched, always show universal tools at minimum
        if tool_type_filter != "All":
            matched_tools = matched_tools[matched_tools["Type"] == tool_type_filter]
            universal_tools = universal_tools[universal_tools["Type"] == tool_type_filter]
        if search_tool_name:
            matched_tools = matched_tools[matched_tools["Tool Name"].str.lower().str.contains(search_tool_name.lower(), na=False)]
            universal_tools = universal_tools[universal_tools["Tool Name"].str.lower().str.contains(search_tool_name.lower(), na=False)]

        tools_to_show = pd.concat([matched_tools, universal_tools]).drop_duplicates("Tool Name")

        if not tools_to_show.empty:
            for _, row in tools_to_show.iterrows():
                # Only use PNG/JPG for logos
                logo_url = ""
                name = row["Tool Name"].lower()
                if name == "chatgpt":
                    logo_url = "https://cdn.openai.com/chatgpt/favicon-32x32.png"
                elif name == "gemini":
                    logo_url = "https://www.gstatic.com/lamda/images/gemini-icon-64.png"
                elif name == "claude":
                    logo_url = "https://avatars.githubusercontent.com/u/103022833?s=280&v=4"
                elif name == "midjourney":
                    logo_url = "https://cdn.icon-icons.com/icons2/3914/PNG/512/midjourney_logo_icon_249964.png"
                elif name == "notion ai":
                    logo_url = "https://cdn.icon-icons.com/icons2/3914/PNG/512/notion_logo_icon_249965.png"
                elif name in ["dall·e", "dalle"]:
                    logo_url = "https://cdn.openai.com/dall-e/favicon.ico"
                elif name == "otter.ai":
                    logo_url = "https://pbs.twimg.com/profile_images/1622941428725399552/ywKg5jDQ_400x400.jpg"
                elif name == "zapier ai":
                    logo_url = "https://static.zapier.com/static/images/favicon.png"
                # ... add more as you like!

                tool_card_html = f"""
                    <div class='tool-card'>
                        {'<img src="'+logo_url+'" width="28" style="vertical-align:middle;margin-right:7px;">' if logo_url else ''}
                        <b><a href="{row['Link']}" target="_blank" style="color:#1166cc;">{row['Tool Name']}</a></b>
                        <br><span style="color:#2668bb;font-size:15px;"><i>Type:</i> {row['Type']} &nbsp;|&nbsp; <i>Category:</i> {row['Category']}</span>
                        <br>{row['Description']}
                    </div>
                """

                st.markdown(tool_card_html, unsafe_allow_html=True)  # <-- ONLY this line!
        else:
            st.warning("No tools found for this step. Try adjusting filter or search. Universal tools always available above.")

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
