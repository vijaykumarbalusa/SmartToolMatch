import streamlit as st
import pandas as pd
import google.generativeai as genai
import gspread
import json

st.set_page_config(page_title="SmartToolMatch", layout="wide", page_icon=":rocket:")

# --- App Logo/Branding ---
st.markdown("""
<div style='text-align:center; margin-bottom:18px'>
    <img src="https://cdn-icons-png.flaticon.com/512/3468/3468379.png" width="70" style="margin-bottom:-10px;">
    <h1 style='margin-bottom:0;color:#1266c2;font-size:2.3rem;font-family:Segoe UI,Arial;'>SmartToolMatch</h1>
    <div style='font-size:18px;margin-top:0;color:#333;font-weight:500;'>Your AI App Discovery & Guidance Engine</div>
</div>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.image("https://avatars.githubusercontent.com/u/103022833?s=280&v=4", width=88)
    st.markdown(
        "<b>Built by</b> [Vijay Kumar Balusa](https://www.linkedin.com/in/vijay-kumar-bvk/)<br>_Connect with me on LinkedIn!_",
        unsafe_allow_html=True
    )
    st.markdown("---")
    st.markdown(
        """
        <div style="font-size:15px;padding-bottom:2px;"><b>About SmartToolMatch</b></div>
        <div style="color:#333;font-size:14px;">
        <ul style="margin-left:-14px;">
        <li>Find the <b>top AI apps</b> for any goal</li>
        <li>See “Best Free”, “Best Paid”, “Best Universal” in each answer</li>
        <li>Now shows up to <b>2 tools per category</b> for broader choices</li>
        <li>Built with Gemini, Google Sheets, and Streamlit</li>
        </ul>
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown("---")
    st.info("💡 Try: 'Plan a trip', 'Write a blog', 'Summarize research', etc.")

# --- Sheets & Gemini Setup ---
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

# --- Input ---
st.markdown("### What do you want to achieve?")
user_goal = st.text_input("Describe your task or goal (e.g., Plan a trip, Generate a resume, Create a presentation)")

def find_top_tools(category, num=2):
    # Find the best N tools in each category for the user_goal (via Gemini prompt)
    # category = 'Free', 'Paid', 'Universal'
    tools_list = tools_df[tools_df['Type'].str.lower().str.contains(category.lower(), na=False)]
    if tools_list.empty:
        return []
    # Prepare Gemini prompt
    tools_string = "\n".join([
        f"{row['Tool Name']} ({row['Category']}): {row['Short Description']}" for _, row in tools_list.iterrows()
    ])
    prompt = (
        f"A user wants to: {user_goal}.\n"
        f"Here is a list of {category} tools:\n{tools_string}\n\n"
        f"Pick up to {num} tools from the list that are the best direct solution for the user’s goal. "
        f"List them in order, and for each, include: Tool Name, a one-line justification, and Short Description."
    )
    try:
        response = gemini_model.generate_content(prompt)
        tool_lines = [line for line in response.text.strip().split('\n') if line.strip()]
        # Parse output for tool names, map back to sheet for full info
        selected = []
        for line in tool_lines[:num]:
            # Try to extract tool name (before any punctuation or "-")
            tool_name = line.split('-')[0].split(':')[0].strip("1234567890. ").strip()
            if not tool_name: continue
            row = tools_list[tools_list['Tool Name'].str.lower() == tool_name.lower()]
            if not row.empty:
                selected.append(row.iloc[0])
        return selected
    except Exception as e:
        return []

# --- Main Output ---
if user_goal:
    st.markdown("#### ✨ Top AI Tools For Your Goal (Up to 2 per Category)")
    st.markdown("<div style='margin-bottom:18px;color:#aaa;font-size:14px;'>Powered by Gemini + 300+ curated tools</div>", unsafe_allow_html=True)
    categories = [("Free", "🟩 Best Free Tools"), ("Paid", "🟦 Best Paid Tools"), ("Universal", "🟪 Best Universal Tools")]
    for cat, header in categories:
        top_tools = find_top_tools(cat, num=2)
        if top_tools:
            st.markdown(f"<div style='margin-top:10px;'><b>{header}:</b></div>", unsafe_allow_html=True)
            for tool in top_tools:
                st.markdown(f"""
                <div style="background:#f8fafd;border-radius:12px;padding:16px 18px;margin:10px 0;box-shadow:0 2px 10px #e7eef6;">
                    <div style="display:flex;align-items:center;">
                        <img src="{tool['Logo URL']}" width="38" height="38" style="border-radius:10px;margin-right:12px;border:1.5px solid #ddd;">
                        <div>
                            <b><a href="{tool['Link']}" target="_blank" style="color:#1464cc;font-size:1.07rem;">{tool['Tool Name']}</a></b>
                            <span style="color:#595a6b;font-size:15px;">({tool['Category']})</span>
                            <div style="font-size:15px;margin-top:4px;"><i>{tool['Best For']}</i></div>
                        </div>
                    </div>
                    <div style="font-size:15px;margin-top:6px;color:#333;">{tool['Short Description']}</div>
                    <div style="font-size:13px;color:#5978a2;margin-top:2px;"><b>Pricing:</b> {tool['Pricing']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='color:#aaa;'>No {cat} tools found for this goal.</span>", unsafe_allow_html=True)
    st.markdown("---")
    # Gemini Quick Tip
    try:
        tip_prompt = f"Share one unique, actionable tip for this user goal: {user_goal} (max 20 words, friendly tone, don't mention tools)."
        tip_response = gemini_model.generate_content(tip_prompt)
        st.info("💡 Gemini Quick Tip: " + tip_response.text.strip())
    except:
        pass
else:
    st.info("Enter your goal above to see the best 2 tools in each category!")

st.markdown("---")
st.caption("© 2025 SmartToolMatch • Built with ❤️ by [Vijay Kumar Balusa](www.linkedin.com/in/vijay-kumar-bvk) • Powered by Gemini & Google Sheets")
