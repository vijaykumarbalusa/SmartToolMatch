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
        "<b>Built by</b> [Vijay Kumar Balusa](https://www.linkedin.com/in/vijay-kumar-bvk)<br>_Let's connect on LinkedIn!_",
        unsafe_allow_html=True
    )
    st.markdown("---")
    st.markdown(
        """
        <div style="font-size:15px;padding-bottom:2px;"><b>About SmartToolMatch</b></div>
        <div style="color:#333;font-size:14px;">
        <ul style="margin-left:-14px;">
        <li>Find the <b>top AI apps</b> for any goal</li>
        <li>See “Best Free”, “Best Paid”, “Best Universal” – up to 2 tools per category</li>
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

def get_top_tools(category, num=2):
    filtered = tools_df[tools_df['Type'].str.lower().str.contains(category.lower(), na=False)].copy()
    if filtered.empty:
        return []
    # Simple relevance: look for user_goal keyword in 'Best For' or 'Short Description'
    score = (
        filtered['Best For'].str.lower().str.contains(user_goal.lower(), na=False).astype(int)
        + filtered['Short Description'].str.lower().str.contains(user_goal.lower(), na=False).astype(int)
    )
    filtered['score'] = score
    top_tools = filtered.sort_values("score", ascending=False).head(num)
    return [row for _, row in top_tools.iterrows()]

if user_goal:
    st.markdown("#### 🔎 Best App Recommendation")
    # Task overview (Gemini)
    try:
        task_overview = gemini_model.generate_content(
            f"In 1-2 lines, explain what the user wants to do: {user_goal}."
        ).text.strip()
        st.markdown(f"<div style='color:#333;font-size:16px;margin-bottom:10px;'>{task_overview}</div>", unsafe_allow_html=True)
    except Exception:
        pass

    categories = [
        ("Free", "🟩 Free Tools"),
        ("Paid", "🟦 Paid Tools"),
        ("Universal", "🟪 Universal Tools"),
    ]
    for cat, cat_label in categories:
        top_tools = get_top_tools(cat, num=2)
        if top_tools:
            st.markdown(f"<div style='font-weight:bold;font-size:17px;margin-top:15px'>{cat_label}</div>", unsafe_allow_html=True)
            cols = st.columns(len(top_tools))
            for i, tool in enumerate(top_tools):
                with cols[i]:
                    st.markdown(f"""
                    <div style="background:#f8fafd;border-radius:12px;padding:16px;margin-bottom:16px;box-shadow:0 2px 10px #e6eaf2;">
                        <div style="display:flex;align-items:center;margin-bottom:7px;">
                            <img src="{tool['Logo URL']}" width="38" height="38" style="border-radius:8px;margin-right:12px;border:1.5px solid #ddd;">
                            <b><a href="{tool['Link']}" target="_blank" style="color:#1366cc;font-size:1.08rem;">{tool['Tool Name']}</a></b>
                        </div>
                        <div style="color:#197d4c;font-size:15px;"><b>Best For:</b> {tool['Best For']}</div>
                        <div style="font-size:15px;margin-top:3px;"><i>{tool['Short Description']}</i></div>
                        <div style="font-size:14px;color:#6079a6;margin-top:2px;"><b>Pricing:</b> {tool['Pricing']}</div>
                        <div style="font-size:13px;color:#aab6c8;margin-top:3px;">{tool['Tags']}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='color:#bbb'>No tools found for {cat}.</span>", unsafe_allow_html=True)

    # Gemini quick tip (optional)
    try:
        tip_prompt = f"Give a 1-line actionable tip for this task: {user_goal}."
        tip_response = gemini_model.generate_content(tip_prompt)
        st.info("💡 Gemini Quick Tip: " + tip_response.text.strip())
    except:
        pass

else:
    st.info("Enter your goal above to see the best 2 tools in each category!")

st.markdown("---")
st.caption("© 2025 SmartToolMatch • Built with ❤️ by [Vijay Kumar Balusa](https://www.linkedin.com/in/vijay-kumar-bvk) • Powered by Gemini & Google Sheets")
