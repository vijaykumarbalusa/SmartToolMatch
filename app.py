import streamlit as st
import pandas as pd
import google.generativeai as genai
import gspread
import json

st.set_page_config(page_title="SmartToolMatch", layout="wide", page_icon=":rocket:")

# --- Sidebar ---
with st.sidebar:
    st.markdown("""
        <div style="background: linear-gradient(135deg,#252550,#454593 80%); border-radius:16px; padding:18px 14px 14px 14px;">
            <div style="display:flex;align-items:center;">
                <img src="https://avatars.githubusercontent.com/u/103022833?s=280&v=4" width="64" style="border-radius:14px;margin-right:12px;border:2px solid #fff;">
                <div style="margin-top:2px;">
                    <span style="color:#fff;font-weight:bold;">Built by</span><br>
                    <a href="https://www.linkedin.com/in/vijay-kumar-bvk" style="color:#ffd858;text-decoration:underline;font-weight:bold;" target="_blank">Vijay Kumar Balusa</a>
                    <div style="font-size:13px;color:#ddd;margin-top:2px;">Connect with me on LinkedIn!</div>
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

# --- Branding and Title ---
st.markdown("""
<div style='text-align:center; margin-bottom:22px'>
    <img src="https://cdn-icons-png.flaticon.com/512/3468/3468379.png" width="84" style="margin-bottom:-10px;box-shadow:0 2px 8px #1a1a2b25;border-radius:22px;">
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
    tools_df.columns = [col.strip() for col in tools_df.columns]
except Exception as e:
    st.error(f"Google Sheets connection failed: {e}")
    st.stop()

# --- User Input (single functional search bar) ---
user_goal = st.text_input(
    "Describe your task or goal (e.g., Plan a trip, Generate a resume, Create a presentation)", key="user_goal", 
    help="This will power both AI recommendations and Gemini's step-by-step advice"
)

# --- Gemini-powered tool selection function ---
def gemini_tool_picker(goal, df, topn=2):
    if df.empty:
        return []
    tools_brief = "\n".join([f"{row['Tool Name']}: {row['Best For']} | {row['Short Description']}" for _, row in df.iterrows()])
    prompt = (
        f"User wants to: {goal}\n"
        f"From this list of tools (each line: Tool Name: Best For | Short Description):\n{tools_brief}\n\n"
        f"Pick the {topn} best tools for this user's goal (from this list only). For each, reply in this exact format:\n"
        f"Tool Name | Why it's a great match for this goal (1 line)\n"
        f"Only return {topn} tools, no explanation, no intro."
    )
    try:
        resp = gemini_model.generate_content(prompt).text.strip()
        names = []
        for line in resp.split('\n'):
            parts = line.split('|')
            if len(parts) >= 1:
                tool_name = parts[0].strip()
                if tool_name:
                    names.append(tool_name)
        # Remove any duplicates in names list:
        seen = set()
        unique_names = []
        for n in names:
            if n not in seen:
                unique_names.append(n)
                seen.add(n)
        return [row for _, row in df.iterrows() if row["Tool Name"] in unique_names][:topn]
    except Exception as e:
        return []

# --- Main Layout: 2 columns ---
if user_goal:
    col1, col2 = st.columns([1.15, 1.05], gap="large")

    # ---- LEFT: Tool Recommender ----
    with col1:
        st.markdown("""
        <div style='font-size:1.4rem;font-weight:700;margin-bottom:5px;color:#7cd4fe;letter-spacing:-1px;'>
            🔎 Best AI App Recommendations
        </div>
        """, unsafe_allow_html=True)

        default_logo = "https://cdn-icons-png.flaticon.com/512/3468/3468379.png"
        already_picked = set()
        category_map = [
            ("Free", "🟩 Free Tools"),
            ("Paid", "🟦 Paid Tools"),
            ("Universal", "🟪 Universal Tools"),
        ]

        for cat, cat_label in category_map:
            df_cat = tools_df[
                tools_df['Type'].str.lower().str.contains(cat.lower(), na=False) &
                ~tools_df['Tool Name'].isin(already_picked)
            ]
            top_tools = gemini_tool_picker(user_goal, df_cat, topn=2)
            # Fallback if Gemini picks same tool twice or returns <2:
            unique_tools = []
            names_seen = set()
            for tool in top_tools:
                if tool["Tool Name"] not in names_seen:
                    unique_tools.append(tool)
                    names_seen.add(tool["Tool Name"])
            if not unique_tools and not df_cat.empty:
                filtered = df_cat.copy()
                score = (
                    filtered['Best For'].str.lower().str.contains(user_goal.lower(), na=False).astype(int)
                    + filtered['Short Description'].str.lower().str.contains(user_goal.lower(), na=False).astype(int)
                )
                filtered['score'] = score
                unique_tools = [row for _, row in filtered.sort_values("score", ascending=False).head(2).iterrows()]
            if unique_tools:
                already_picked.update([tool["Tool Name"] for tool in unique_tools])
                st.markdown(f"<div style='font-weight:600;font-size:17px;margin-top:16px;color:#fff;text-shadow:0 1px 5px #1c213150;'>{cat_label}</div>", unsafe_allow_html=True)
                cols = st.columns(len(unique_tools))
                for i, tool in enumerate(unique_tools):
                    tool_logo = tool['Logo URL']
                    if not (isinstance(tool_logo, str) and tool_logo.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))):
                        tool_logo = default_logo
                    with cols[i]:
                        st.markdown(f"""
                        <div style="background:#181830;border-radius:15px;padding:18px 12px 15px 12px;margin-bottom:15px;box-shadow:0 2px 12px #10101a30;">
                            <div style="display:flex;align-items:center;margin-bottom:10px;">
                                <img src="{tool_logo}" width="52" height="52" style="border-radius:11px;margin-right:12px;border:2px solid #444;">
                                <div>
                                    <b><a href="{tool['Link']}" target="_blank" style="color:#73c9fa;font-size:1.13rem;">{tool['Tool Name']}</a></b>
                                    <div style="font-size:14px;color:#a4adc4;">({tool['Category']})</div>
                                </div>
                            </div>
                            <div style="color:#80e6a0;font-size:15px;"><b>Best For:</b> {tool['Best For']}</div>
                            <div style="font-size:15px;margin-top:4px;color:#dde;"><i>{tool['Short Description']}</i></div>
                            <div style="font-size:14px;color:#74acef;margin-top:3px;"><b>Pricing:</b> {tool['Pricing']}</div>
                            <div style="font-size:13px;color:#b2b5c6;margin-top:3px;">{tool['Tags']}</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color:#bbb'>No tools found for {cat}.</span>", unsafe_allow_html=True)

    # ---- RIGHT: Gemini/AI Assistant ----
    with col2:
        st.markdown("""
        <div style='font-size:1.3rem;font-weight:700;margin-bottom:9px;margin-top:2px;color:#f6baff;letter-spacing:-1px;'>
            🤖 AI Assistant Advice
        </div>
        """, unsafe_allow_html=True)
        try:
            ai_response = gemini_model.generate_content(
                f"You are a helpful, positive AI assistant. The user wants to: {user_goal}. "
                "Give a practical, step-by-step answer (5–8 sentences), mentioning where AI helps. "
                "Don't just list tools—be insightful, warm, and actionable. Start with a friendly greeting."
            ).text.strip()
            st.markdown(f"""
            <div style="background:#222137;padding:18px 20px 15px 17px;border-radius:16px;margin-bottom:20px;box-shadow:0 2px 14px #25023c22;">
                <span style="font-size:1.09rem;color:#eaeaf4;">{ai_response}</span>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.warning("Gemini AI response unavailable right now.")

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
