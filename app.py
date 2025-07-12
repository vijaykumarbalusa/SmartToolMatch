import streamlit as st
import pandas as pd
import google.generativeai as genai
import gspread
import json
from fuzzywuzzy import fuzz

st.set_page_config(page_title="SmartToolMatch", layout="wide")

st.title("🔥 SmartToolMatch – Your AI Workflow Assistant")

# --- 1. Configure Gemini API with the correct model
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
gemini_model = genai.GenerativeModel("gemini-1.5-pro")  # <- Use only this!

# --- 2. Connect to Google Sheets
try:
    service_account_info = json.loads(st.secrets["GSPREAD_SERVICE_ACCOUNT"])
    gc = gspread.service_account_from_dict(service_account_info)
    # ⚠️ Replace this with your actual Sheet URL or name!
    SHEET_URL = "https://docs.google.com/spreadsheets/d/13KVDHGDG7xITg7gLor1LphhSHJEI-_LGmy3NDUVDNi8/edit?usp=sharing"
    worksheet = gc.open_by_url(SHEET_URL).sheet1
    tools_data = worksheet.get_all_records()
    tools_df = pd.DataFrame(tools_data)
except Exception as e:
    st.error(f"Google Sheets connection failed: {e}")
    st.stop()

# --- 3. User Inputs
user_goal = st.text_input(
    "What do you want to achieve? (e.g., 'Create a content marketing plan')",
    placeholder="Describe your goal, e.g. 'Plan a trip to Europe'"
)

tool_type_filter = st.selectbox("Filter by Tool Type:", options=["All"] + sorted(tools_df["Type"].dropna().unique()))
search_tool_name = st.text_input("Search tools by name (optional):")

# --- 4. Process Input and Generate Workflow
if user_goal:
    with st.spinner("Generating workflow steps with Gemini..."):
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

    st.header("Your Personalized Workflow & AI Tools")
    for i, step in enumerate(steps, 1):
        st.subheader(f"Step {i}: {step}")

        # --- Tool matching: exact and fuzzy
        def match_tools(step, tools_df):
            # First, exact match by Category
            matches = tools_df[tools_df["Category"].str.lower().str.contains(step.split()[0].lower(), na=False)]

            # If no exact matches, use fuzzy matching on Category
            if matches.empty:
                threshold = 60
                tools_df["fuzz_ratio"] = tools_df["Category"].apply(
                    lambda x: fuzz.partial_ratio(x.lower(), step.lower()) if pd.notna(x) else 0
                )
                matches = tools_df[tools_df["fuzz_ratio"] >= threshold]
            return matches

        matched_tools = match_tools(step, tools_df)
        universal_tools = tools_df[tools_df["Type"].str.lower() == "universal"]

        # Filter by tool type if not "All"
        if tool_type_filter != "All":
            matched_tools = matched_tools[matched_tools["Type"] == tool_type_filter]
            universal_tools = universal_tools[universal_tools["Type"] == tool_type_filter]

        # Filter by tool name search if provided
        if search_tool_name:
            matched_tools = matched_tools[matched_tools["Tool Name"].str.lower().str.contains(search_tool_name.lower(), na=False)]
            universal_tools = universal_tools[universal_tools["Tool Name"].str.lower().str.contains(search_tool_name.lower(), na=False)]

        tools_to_show = pd.concat([matched_tools, universal_tools]).drop_duplicates("Tool Name")

        if not tools_to_show.empty:
            for _, row in tools_to_show.iterrows():
                st.markdown(
                    f"- [{row['Tool Name']}]({row['Link']}) — *{row['Type']}*<br>{row['Description']}",
                    unsafe_allow_html=True
                )
        else:
            st.warning("No tools found for this step. Try changing the filter or search.")

else:
    st.info("Enter your goal above to get started!")

st.caption("© 2024 SmartToolMatch • Powered by Gemini, Google Sheets, and Streamlit")
