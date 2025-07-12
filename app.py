import streamlit as st
import pandas as pd
import google.generativeai as genai
import gspread
import json
from fuzzywuzzy import fuzz

st.set_page_config(page_title="SmartToolMatch", layout="wide", page_icon="🚀")

st.title("🚀 SmartToolMatch")
st.caption("Your AI Workflow and Tool Discovery Assistant")

# ---- Sidebar ----
with st.sidebar:
    st.image("https://avatars.githubusercontent.com/u/103022833?s=280&v=4", width=100)
    st.write("Built by [Vijay Kumar Balusa](https://www.linkedin.com/in/vijaykumarbalusa/)")
    st.info("Try: 'Edit podcast audio', 'Design a presentation', 'Automate data scraping'")

# ---- Sheets & Gemini Setup ----
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

# ---- User Inputs ----
user_goal = st.text_input("What do you want to achieve?", placeholder="e.g., Create a video, Generate blog ideas, Summarize research")
tool_type_filter = st.selectbox("Filter by Tool Type:", options=["All"] + sorted(tools_df["Type"].dropna().unique()))
search_tool_name = st.text_input("Search tools by name (optional):")

# ---- Workflow & Tool Display ----
if user_goal:
    with st.spinner("Gemini is generating your workflow..."):
        prompt = f"Break down the following user goal into 3-6 actionable workflow steps. Goal: {user_goal}"
        try:
            response = gemini_model.generate_content(prompt)
            steps = [s.strip().lstrip("1234567890. ").capitalize() for s in response.text.split("\n") if s.strip()]
            if not steps:
                raise ValueError("Gemini response is empty. Try rephrasing your goal.")
        except Exception as e:
            st.error(f"Gemini API error: {e}")
            st.stop()

    st.subheader("📝 Your Personalized Workflow & AI Tools")

    for i, step in enumerate(steps, 1):
        st.markdown(f"**{i} {step}**")
        # --- Matching ---
        def match_tools(step, tools_df):
            first_word = step.split()[0].lower() if step.split() else ""
            if first_word:
                matches = tools_df[tools_df["Category"].str.lower().str.contains(first_word, na=False, regex=False)]
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
                st.markdown(
                    f"- [{row['Tool Name']}]({row['Link']}) ({row['Type']} | {row['Category']}): {row['Description']}"
                )
        else:
            st.warning("No tools found for this step. Try adjusting the filter or search.")

else:
    st.info("Enter your goal above to get started!")

st.markdown("---")
st.caption("© 2024 SmartToolMatch • Powered by Gemini, Google Sheets, and Streamlit")
