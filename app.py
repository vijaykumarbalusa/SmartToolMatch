import streamlit as st
import pandas as pd
import google.generativeai as genai
import gspread
import json
from fuzzywuzzy import fuzz

st.set_page_config(page_title="SmartToolMatch", layout="wide")
st.title("🔥 SmartToolMatch – Your AI Workflow Assistant")

# --- 1. Configure Gemini API (make sure to use gemini-1.5-pro)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
gemini_model = genai.GenerativeModel("gemini-1.5-pro")

# --- 2. Connect to Google Sheets
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

user_goal = st.text_input("What do you want to achieve?", placeholder="Describe your goal (e.g., Plan a trip to Europe)")
tool_type_filter = st.selectbox("Filter by Tool Type:", options=["All"] + sorted(tools_df["Type"].dropna().unique()))
search_tool_name = st.text_input("Search tools by name (optional):")

def rank_best_tool(step, df):
    # 1. Try exact category match on step's noun
    core_words = [w for w in step.lower().split() if len(w) > 3]  # Exclude "the", "and", etc.
    for word in core_words:
        # Look for tool whose Category matches this word
        candidates = df[df["Category"].str.lower().str.contains(word, na=False, regex=False)]
        if not candidates.empty:
            # Rank by fuzzy match score, then select top
            candidates["score"] = candidates["Category"].apply(lambda x: fuzz.ratio(word, x.lower()))
            return candidates.sort_values("score", ascending=False).iloc[0]
    # 2. Fallback: Fuzzy match with threshold
    df["score"] = df["Category"].apply(lambda x: fuzz.partial_ratio(x.lower(), step.lower()) if pd.notna(x) else 0)
    best_row = df[df["score"] == df["score"].max()]
    if not best_row.empty and best_row.iloc[0]["score"] > 60:
        return best_row.iloc[0]
    # 3. As last resort, return universal tool
    return None

if user_goal:
    with st.spinner("Generating workflow steps..."):
        prompt = f"Break down the following user goal into 3-6 actionable workflow steps. Goal: {user_goal}"
        try:
            response = gemini_model.generate_content(prompt)
            steps = [s.strip().lstrip("1234567890. ").capitalize()
                     for s in response.text.split("\n") if s.strip()]
        except Exception as e:
            st.error(f"Gemini API error: {e}")
            steps = []
    st.header("Your Personalized Workflow & AI Tools")
    for i, step in enumerate(steps, 1):
        st.markdown(
            f"<div style='background:#f0f4ff;padding:12px 18px;border-radius:13px;margin-bottom:4px;font-size:17px;'>"
            f"<b>Step {i}:</b> <span style='color:#193458;'>{step}</span></div>", unsafe_allow_html=True
        )
        # Only show the best tool!
        filtered_tools = tools_df
        if tool_type_filter != "All":
            filtered_tools = filtered_tools[filtered_tools["Type"] == tool_type_filter]
        if search_tool_name:
            filtered_tools = filtered_tools[filtered_tools["Tool Name"].str.lower().str.contains(search_tool_name.lower(), na=False)]

        best_tool = rank_best_tool(step, filtered_tools)
        if best_tool is not None:
            st.markdown(
                f"**[{best_tool['Tool Name']}]({best_tool['Link']})** &mdash; _{best_tool['Type']}_  \n"
                f"{best_tool['Description']}"
            )
        else:
            st.info("No direct specialized tool found for this step. See universal tools below.")

    # --- Always show universal tools (as 'other options') ---
    universal_tools = tools_df[tools_df["Type"].str.lower() == "universal"]
    if not universal_tools.empty:
        st.markdown("#### 🌍 Other AI Assistants You Can Use For Any Step")
        for _, row in universal_tools.iterrows():
            st.markdown(
                f"- **[{row['Tool Name']}]({row['Link']})** &mdash; {row['Description']}"
            )
else:
    st.info("Enter your goal above to get started!")

st.caption("© 2025 SmartToolMatch • Built by [Vijay Kumar Balusa](https://www.linkedin.com/in/vijaykumarbalusa/) • Powered by Gemini, Google Sheets, and Streamlit")
