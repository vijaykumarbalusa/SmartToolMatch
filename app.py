import streamlit as st
import pandas as pd
import google.generativeai as genai
import gspread
import json

st.set_page_config(page_title="SmartToolMatch", layout="wide", page_icon=":rocket:")

# --- Sidebar (dark/light mode friendly, with logo and LinkedIn) ---
with st.sidebar:
    st.markdown("""
        <div style="background: linear-gradient(135deg,#252550,#454593 80%); border-radius:16px; padding:18px 14px 14px 14px;">
            <div style="display:flex;align-items:center;">
                <img src="https://avatars.githubusercontent.com/u/103022833?s=280&v=4" width="64" style="border-radius:14px;margin-right:12px;border:2px solid #fff;">
                <div>
                    <span style="color:#fff;font-weight:bold;">Built by <a href="https://www.linkedin.com/in/vijay-kumar-bvk" style="color:#ffd858;" target="_blank">Vijay Kumar Balusa</a></span>
                    <div style="font-size:13px;color:#ddd;">Connect with me on LinkedIn!</div>
                </div>
            </div>
            <hr style="margin:12px 0 8px 0; border:0; border-top:1.5px solid #666;">
            <div style="font-size:15px;color:#eaeaea;font-weight:bold;padding-bottom:5px;">About SmartToolMatch</div>
            <ul style="color:#f4f4f4;font-size:14px;line-height:1.6;margin-left:-18px;">
                <li>Find the <b>best AI apps</b> for any goal</li>
                <li>See <b>2 top apps</b> in Free, Paid, Universal categories</li>
                <li>Instant answers + full workflow</li>
                <li>Powered by Gemini, Streamlit, and Google Sheets</li>
            </ul>
            <div style="background:#2a2a44;padding:10px 10px 8px 10px;border-radius:9px;margin-top:7px;color:#eee;">
                💡 <b>Try:</b> <i>'Plan a trip', 'Generate a resume', 'Automate my marketing'</i>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- Main branding and title ---
st.markdown("""
<div style='text-align:center; margin-bottom:18px'>
    <img src="https://cdn-icons-png.flaticon.com/512/3468/3468379.png" width="80" style="margin-bottom:-10px;box-shadow:0 2px 8px #1a1a2b25;border-radius:20px;">
    <h1 style='margin-bottom:0;color:#1266c2;font-size:2.3rem;font-family:Segoe UI,Arial;'>SmartToolMatch</h1>
    <div style='font-size:18px;margin-top:0;color:#bbb;font-weight:500;'>Your AI App Discovery & Guidance Engine</div>
</div>
""", unsafe_allow_html=True)

# --- Load Data & Gemini ---
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

# --- User Input ---
st.markdown("### What do you want to achieve?")
user_goal = st.text_input(
    "Describe your task or goal (e.g., Plan a trip, Generate a resume, Create a presentation)")

def get_top_tools(category, num=2):
    filtered = tools_df[tools_df['Type'].str.lower().str.contains(category.lower(), na=False)].copy()
    if filtered.empty:
        return []
    score = (
        filtered['Best For'].str.lower().str.contains(user_goal.lower(), na=False).astype(int)
        + filtered['Short Description'].str.lower().str.contains(user_goal.lower(), na=False).astype(int)
    )
    filtered['score'] = score
    top_tools = filtered.sort_values("score", ascending=False).head(num)
    return [row for _, row in top_tools.iterrows()]

# --- Best App Recommendation + AI Assistant Answer ---
if user_goal:
    # --- AI Assistant (ChatGPT/Gemini style) response ---
    try:
        ai_response = gemini_model.generate_content(
            f"You are a helpful, positive AI assistant. The user wants to: {user_goal}. "
            "Give a practical, step-by-step answer (5–8 sentences), mentioning where AI helps. "
            "Don't just list tools—be insightful, warm, and actionable. Start with a friendly greeting."
        ).text.strip()
        st.markdown(f"""
        <div style="background:#181830;padding:18px 18px 15px 18px;border-radius:15px;margin-bottom:28px;
            box-shadow:0 3px 16px #23234540;color:#e8ebfa;font-size:1.15rem;">
            {ai_response}
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        pass

    st.markdown("#### 🔎 Best App Recommendation")

    categories = [
        ("Free", "🟩 Free Tools"),
        ("Paid", "🟦 Paid Tools"),
        ("Universal", "🟪 Universal Tools"),
    ]
    default_logo = "https://cdn-icons-png.flaticon.com/512/3468/3468379.png"

    for cat, cat_label in categories:
        top_tools = get_top_tools(cat, num=2)
        if top_tools:
            st.markdown(f"<div style='font-weight:bold;font-size:18px;margin-top:15px;color:#8af;'>{cat_label}</div>", unsafe_allow_html=True)
            cols = st.columns(len(top_tools))
            for i, tool in enumerate(top_tools):
                # --- LOGO HANDLING WITH FALLBACK, BIGGER LOGOS ---
                tool_logo = tool['Logo URL']
                if not (isinstance(tool_logo, str) and tool_logo.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))):
                    tool_logo = default_logo
                with cols[i]:
                    st.markdown(f"""
                    <div style="background:#191936;border-radius:16px;padding:19px;margin-bottom:18px;box-shadow:0 2px 10px #10101a40;transition:box-shadow 0.18s;">
                        <div style="display:flex;align-items:center;margin-bottom:11px;">
                            <img src="{tool_logo}" width="54" height="54" style="border-radius:13px;margin-right:15px;border:2px solid #444;box-shadow:0 3px 8px #20204525;">
                            <div>
                                <b><a href="{tool['Link']}" target="_blank" style="color:#6fa1ff;font-size:1.16rem;">{tool['Tool Name']}</a></b>
                                <div style="font-size:14px;color:#a4adc4;font-weight:400;">({tool['Category']})</div>
                            </div>
                        </div>
                        <div style="color:#7ee287;font-size:15.5px;"><b>Best For:</b> {tool['Best For']}</div>
                        <div style="font-size:15.5px;margin-top:5px;color:#ddd;"><i>{tool['Short Description']}</i></div>
                        <div style="font-size:14px;color:#5b9acb;margin-top:5px;"><b>Pricing:</b> {tool['Pricing']}</div>
                        <div style="font-size:13px;color:#b2b5c6;margin-top:5px;">{tool['Tags']}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='color:#bbb'>No tools found for {cat}.</span>", unsafe_allow_html=True)

    # --- Gemini quick tip (optional) ---
    try:
        tip_prompt = f"Give a 1-line actionable tip for this task: {user_goal}."
        tip_response = gemini_model.generate_content(tip_prompt)
        st.info("💡 Gemini Quick Tip: " + tip_response.text.strip())
    except:
        pass

else:
    st.info("Enter your goal above to see the best tools and assistant advice!")

st.markdown("---")
st.caption("© 2025 SmartToolMatch • Built with ❤️ by [Vijay Kumar Balusa](https://www.linkedin.com/in/vijay-kumar-bvk) • Powered by Gemini & Google Sheets")
