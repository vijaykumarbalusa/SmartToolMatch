import streamlit as st
import pandas as pd
import google.generativeai as genai
import gspread
import json

st.set_page_config(page_title="SmartToolMatch", layout="wide")
st.title("🔥 SmartToolMatch – Your AI Workflow Assistant")

with st.sidebar:
    st.image("https://avatars.githubusercontent.com/u/103022833?s=280&v=4", width=100)
    st.markdown(
        "Built by [Vijay Kumar Balusa](https://www.linkedin.com/in/vijaykumarbalusa/)  \n"
        "_Connect with me on LinkedIn!_"
    )

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

user_goal = st.text_input(
    "What do you want to achieve?",
    placeholder="e.g., Plan a trip, Generate a resume, Create a presentation"
)

if user_goal:
    with st.spinner("Gemini is analyzing and matching the best AI apps..."):
        tools_string = "\n".join([
            f"{r['Tool Name']} ({r['Type']}) - {r['Description']}" for _, r in tools_df.iterrows()
        ])
        prompt = (
            f"You are an AI app recommendation engine. A user wants to: {user_goal}.\n"
            "You have access to this tool database:\n"
            f"{tools_string}\n\n"
            "Please do the following in your response:\n"
            "1. Briefly explain what this task involves or why it's important (2 sentences max).\n"
            "2. Suggest up to 1 best FREE app, 1 best PAID app, and 1 best UNIVERSAL tool (from the list) that can do the task directly. If no good match for a type, say so. \n"
            "3. For each app, show: Name (with link if possible), short description, and what makes it a good fit.\n"
            "4. End with a unique Gemini Quick Tip relevant to the task, in one line.\n"
            "Reply in clear, friendly language and use markdown bullet points or sections for readability."
        )
        try:
            response = gemini_model.generate_content(prompt)
            answer = response.text.strip()
        except Exception as e:
            answer = f"Gemini API error: {e}"

    st.header("✨ Top AI App Recommendations For Your Goal")
    st.markdown(answer)
else:
    st.info("Enter your goal above to get tailored, actionable AI app picks!")

st.markdown("---")
st.caption("© 2025 SmartToolMatch • Built with ❤️ by [Vijay Kumar Balusa](https://www.linkedin.com/in/vijaykumarbalusa/) • Powered by Gemini & Google Sheets")
