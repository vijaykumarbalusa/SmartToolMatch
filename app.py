import streamlit as st
import gspread
import pandas as pd
import requests
import json
import difflib
import google.generativeai as genai

# --- 1. Google Sheets Authentication (from Streamlit Secrets) ---
service_account_info = json.loads(st.secrets["GSPREAD_SERVICE_ACCOUNT"])
gc = gspread.service_account_from_dict(service_account_info)

# --- 2. Open your Google Sheet ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/13KVDHGDG7xITg7gLor1LphhSHJEI-_LGmy3NDUVDNi8/edit#gid=0"
worksheet = gc.open_by_url(SHEET_URL).sheet1
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# --- 3. Gemini setup ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# --- 4. Streamlit UI ---
st.title("SmartToolMatch 🚀")
st.write("Find the best AI tools for your workflow!")

user_goal = st.text_input(
    "Describe your task or goal (e.g., create and edit a YouTube video, AI gym plan, resume review, etc):"
)
tool_type = st.selectbox("Filter by Tool Type:", ["All"] + sorted(df["Type"].unique()))
search_name = st.text_input("Search tools by name:")

# --- 5. LLM Workflow Step Generation ---
def get_workflow_steps(user_goal):
    prompt = f"Given the user wants to: '{user_goal}', list 3-6 high-level, actionable workflow steps they should take, with each step as a clear phrase."
    try:
        response = genai.GenerativeModel("gemini-pro").generate_content(prompt)
        steps = [line.strip("1234567890). ").strip("- ") for line in response.text.split("\n") if line.strip()]
        steps = [step for step in steps if len(step) > 6]
        return steps[:6]
    except Exception as e:
        st.error(f"Error generating workflow: {e}")
        return []

# --- 6. Tool Matching (by Category, then fallback to fuzzy match in Description/Name) ---
def find_relevant_tools(df, step, selected_type):
    # Try to match by Category (strict)
    matches = df[df["Category"].str.lower().str.contains(step.split()[0].lower())]
    # Fallback: fuzzy match to Description or Tool Name
    if matches.empty:
        matches = df[
            df["Description"].str.lower().str.contains(step.split()[0].lower())
            | df["Tool Name"].str.lower().str.contains(step.split()[0].lower())
        ]
    if selected_type != "All":
        matches = matches[matches["Type"].str.contains(selected_type, case=False)]
    return matches

# --- 7. Display Section ---
if user_goal:
    st.markdown(f"### Smart AI-Generated Workflow & Tools:")

    workflow_steps = get_workflow_steps(user_goal)
    if not workflow_steps:
        st.warning("Couldn't generate workflow steps. Try a different or clearer goal.")
    else:
        for step in workflow_steps:
            st.markdown(f"#### {step}")

            relevant_tools = find_relevant_tools(df, step, tool_type)

            if not relevant_tools.empty:
                for _, row in relevant_tools.iterrows():
                    st.markdown(
                        f"- [{row['Tool Name']}]({row['Link']}) _(Type: {row['Type']})_<br>{row['Description']}",
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No relevant tools found for this step.")

            # Always show universal tools
            universal_tools = df[df["Type"].str.lower() == "universal"]
            if not universal_tools.empty:
                st.markdown("**Universal Tools (Good for any step):**")
                for _, row in universal_tools.iterrows():
                    st.markdown(
                        f"- [{row['Tool Name']}]({row['Link']}) _(Type: {row['Type']})_<br>{row['Description']}",
                        unsafe_allow_html=True,
                    )

# --- 8. Global Name Search ---
if search_name.strip():
    matches = df[df["Tool Name"].str.lower().str.contains(search_name.lower())]
    if not matches.empty:
        st.markdown("### Search Results")
        for _, row in matches.iterrows():
            st.markdown(
                f"- [{row['Tool Name']}]({row['Link']}) _(Type: {row['Type']})_<br>{row['Description']}",
                unsafe_allow_html=True,
            )
    else:
        st.info("No tools found with that name.")

