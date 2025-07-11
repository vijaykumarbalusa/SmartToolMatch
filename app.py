import streamlit as st
import pandas as pd
import google.generativeai as genai
import gspread
import json

st.set_page_config(page_title="SmartToolMatch", layout="wide")

st.title("🔥 SmartToolMatch – Your AI Workflow Assistant")

# --- 1. Configure Gemini API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
gemini_model = genai.GenerativeModel("gemini-pro")

# --- 2. Connect to Google Sheets
service_account_info = json.loads(st.secrets["GSPREAD_SERVICE_ACCOUNT"])
gc = gspread.service_account_from_dict(service_account_info)
# ⚠️ Replace below with your sheet URL or name!
SHEET_URL = "https://docs.google.com/spreadsheets/d/13KVDHGDG7xITg7gLor1LphhSHJEI-_LGmy3NDUVDNi8/edit?usp=sharing"
worksheet = gc.open_by_url(SHEET_URL).sheet1
tools_data = worksheet.get_all_records()
tools_df = pd.DataFrame(tools_data)

# --- 3. UI: User enters a workflow goal
user_goal = st.text_input("What do you want to achieve? (e.g., 'Create a content marketing plan')")

if user_goal:
    # --- 4. Paraphrase and Generate Steps with Gemini
    with st.spinner("Generating workflow steps..."):
        prompt = f"Break down the following user goal into 3-6 actionable workflow steps: {user_goal}"
        try:
            response = gemini_model.generate_content(prompt)
            steps = [step.strip() for step in response.text.split("\n") if step.strip()]
        except Exception as e:
            st.error(f"Gemini API error: {e}")
            steps = []

    # --- 5. Display steps & match tools
    st.header("Your Personalized Workflow")
    for i, step in enumerate(steps, 1):
        st.subheader(f"Step {i}: {step}")
        # Exact match by category (simple demo—customize as needed!)
        matches = tools_df[tools_df["Category"].str.lower().str.contains(step.split()[0].lower(), na=False)]
        universal_tools = tools_df[tools_df["Type"].str.lower() == "universal"]
        tools_to_show = pd.concat([matches, universal_tools]).drop_duplicates("Tool Name")

        if not tools_to_show.empty:
            for idx, row in tools_to_show.iterrows():
                st.markdown(f"- [{row['Tool Name']}]({row['Link']}) — *{row['Type']}*<br>{row['Description']}", unsafe_allow_html=True)
        else:
            st.write("No direct tools found for this step. Showing universal tools.")
            for idx, row in universal_tools.iterrows():
                st.markdown(f"- [{row['Tool Name']}]({row['Link']}) — *{row['Type']}*<br>{row['Description']}", unsafe_allow_html=True)
else:
    st.info("Enter your goal above to get started!")

st.caption("© 2024 SmartToolMatch • Powered by Gemini, Google Sheets, and Streamlit")
