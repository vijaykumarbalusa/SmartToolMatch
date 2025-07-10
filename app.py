import streamlit as st
import gspread
import pandas as pd
import requests
import difflib

st.set_page_config(page_title="SmartToolMatch 🚀", layout="wide")

# ---- CONFIG ----
SHEET_NAME = 'SmartToolMatch_AI_Tools_Master_Sheet'
WORKSHEET_NAME = 'Sheet1'
SERVICE_ACCOUNT_FILE = 'smarttoolmatch-5e859910ddc2.json'

# ---- PARAPHRASE FUNCTION ----
def paraphrase_user_input(user_input):
    prompt = f"""
Rewrite the following user request as a clear, actionable goal for an AI-powered workflow assistant. 
Make it as specific and focused as possible.

User request: "{user_input}"

Paraphrased actionable goal:
"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        result = response.json()
        paraphrased_goal = result.get("response", "").strip()
        return paraphrased_goal
    except Exception as e:
        st.error(f"Llama 3 paraphrasing error: {str(e)}")
        return user_input  # fallback to original

# ---- LLM WORKFLOW GENERATION ----
def get_workflow_steps_from_llm(user_task, categories):
    categories_clean = [c.strip().lower() for c in categories]
    categories_text = ", ".join(categories)
    prompt = f"""
You are an expert workflow planner.

- Your job is to break down the following user goal into the most relevant actionable steps.
- Use or adapt steps from this list: {categories_text}
- If a step isn't an exact match, use the closest relevant category from the list or combine steps if needed.
- For ambiguous or novel user goals, map them to the most similar categories you see.

User goal: "{user_task}"

Return the steps as a numbered list, each one matching or closely related to the provided categories.

Steps:
"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            },
            timeout=90
        )
        result = response.json()
        content = result.get("response", "")
        steps = []
        for line in content.split('\n'):
            line_clean = line.strip()
            if line_clean and not line_clean.lower().startswith("steps"):
                step_name = line_clean.lstrip("1234567890. ").strip()
                if step_name:
                    steps.append(step_name)
        return list(dict.fromkeys(steps))  # remove duplicates, keep order
    except Exception as e:
        st.error(f"Llama 3 error: {str(e)}")
        return []

# ---- PRE-FILTERING FUNCTION ----
def filter_tools_for_step(df, step, max_tools=15):
    step_lower = step.lower()
    # Fuzzy match score by category and description
    df['score'] = df.apply(lambda row: (
        max(
            difflib.SequenceMatcher(None, step_lower, str(row['Category']).lower()).ratio(),
            difflib.SequenceMatcher(None, step_lower, str(row['Description']).lower()).ratio()
        )
    ), axis=1)
    filtered = df[df['score'] > 0.25].sort_values('score', ascending=False)
    if filtered.empty:
        filtered = df  # fallback: use all tools if nothing matches
    return filtered.drop(columns='score').head(max_tools)

# ---- LLM TOOL MATCHING ----
def get_tools_from_llm(step, tools):
    tool_lines = []
    for i, row in tools.iterrows():
        tool_lines.append(
            f"{row['Tool Name']} (Type: {row['Type']}), Category: {row['Category']}, Description: {row['Description']}"
        )
    tools_text = "\n".join(tool_lines)
    prompt = f"""
A user wants to accomplish this workflow step: "{step}"

Here is a list of available AI tools, each with its name, type, category, and description:

{tools_text}

Which of these tools are most relevant for the user's workflow step?
Return only the tool names, each on a new line. If none are relevant, return "None".
"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            },
            timeout=90
        )
        result = response.json()
        content = result.get("response", "")
        suggestions = []
        for line in content.split('\n'):
            tool_name = line.strip().lstrip("1234567890.- ").strip()
            if tool_name and tool_name.lower() != "none":
                suggestions.append(tool_name)
        return suggestions
    except Exception as e:
        st.error(f"Llama 3 tool matching error: {str(e)}")
        return []

# ---- LOAD DATA ----
@st.cache_data
def load_data():
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    sh = gc.open(SHEET_NAME)
    worksheet = sh.worksheet(WORKSHEET_NAME)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    return df

df = load_data()

# ---- STREAMLIT UI ----
st.markdown(
    "<h1 style='color:#fff;'>SmartToolMatch 🚀</h1>"
    "<h3 style='color:#aad;'>Find the best AI tools for your workflow!</h3>",
    unsafe_allow_html=True
)

user_task = st.text_input(
    "Describe your task or goal (e.g., create and edit a YouTube video, AI gym plan, resume review, etc):"
)

colA, colB = st.columns([1, 2])
with colA:
    tool_type = st.selectbox("Filter by Tool Type:", ["All", "Free", "Paid", "Universal"])
with colB:
    search_query = st.text_input("Search tools by name:")

if user_task:
    all_categories = df['Category'].unique().tolist()

    # Step 1: Paraphrase user input
    paraphrased_task = paraphrase_user_input(user_task)
    if paraphrased_task != user_task:
        st.info(f"Rephrased your goal as: **{paraphrased_task}**")
    else:
        st.info(f"Your goal: **{user_task}**")

    # Step 2: Generate workflow steps
    workflow_steps = get_workflow_steps_from_llm(paraphrased_task, all_categories)

    if workflow_steps:
        st.markdown("## Smart AI-Generated Workflow & Tools:")
        for step in workflow_steps:
            st.markdown(f"### {step}")

            # 1. Pre-filter tools
            filtered_df = df.copy()
            if tool_type != "All":
                filtered_df = filtered_df[filtered_df['Type'].str.lower().str.contains(tool_type.lower())]
            if search_query.strip():
                search_lower = search_query.strip().lower()
                filtered_df = filtered_df[
                    filtered_df['Tool Name'].str.lower().str.contains(search_lower)
                ]
            filtered_tools = filter_tools_for_step(filtered_df, step)

            # 2. LLM tool matching on small candidate set
            tool_names = get_tools_from_llm(step, filtered_tools)
            if tool_names:
                st.markdown("**LLM-Suggested Tools:**")
                for tool_name in tool_names:
                    tool_rows = filtered_tools[filtered_tools['Tool Name'].str.lower() == tool_name.lower()]
                    if not tool_rows.empty:
                        row = tool_rows.iloc[0]
                        st.markdown(
                            f"- [{row['Tool Name']}]({row['Link']}) _(Type: {row['Type']})_<br>{row['Description']}",
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(f"- {tool_name} (Not found in filtered tools)")
            else:
                st.markdown("_No relevant tools found for this step._")

            # Always show universal tools (optional)
            universal_tools = df[
                (df['Type'].str.lower() == 'universal') | 
                (df['Category'].str.lower().str.contains('universal'))
            ]
            if not universal_tools.empty:
                st.markdown("**Universal Tools (Good for any step):**")
                for _, row in universal_tools.iterrows():
                    st.markdown(
                        f"- [{row['Tool Name']}]({row['Link']}) _(Type: {row['Type']})_<br>{row['Description']}",
                        unsafe_allow_html=True
                    )
            st.markdown("---")
    else:
        st.warning("No workflow steps generated for your goal. Try rephrasing your request.")
