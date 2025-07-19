import streamlit as st
import pandas as pd
import google.generativeai as genai
import gspread
import json

st.set_page_config(page_title="SmartToolMatch", layout="wide", page_icon=":rocket:")

# --- Theme toggle (light/dark) ---
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
theme = st.sidebar.radio("Theme", ["dark", "light"], index=0 if st.session_state.theme=="dark" else 1)
st.session_state.theme = theme
primary_bg = "#191936" if theme == "dark" else "#f8f8fc"
card_bg = "#181830" if theme == "dark" else "#f1f5fe"
ai_bg = "#222137" if theme == "dark" else "#f3f0fd"
txt_main = "#e8ebfa" if theme == "dark" else "#2a253f"
txt_sub = "#aaa" if theme == "dark" else "#50506d"
card_shadow = "0 2px 10px #10101a40" if theme == "dark" else "0 2px 10px #b2b4e433"
accent = "#6fa1ff"
good = "#84eea3"
compare_highlight = "#fde68a"

# --- Sidebar with filters and profile ---
with st.sidebar:
    st.markdown(f"""
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
            <hr style="margin:15px 0 5px 0; border:0; border-top:1px solid #414171;">
            <b>Filter by Category</b><br>
    """, unsafe_allow_html=True)
    # --- Category filter ---
    try:
        service_account_info = json.loads(st.secrets["GSPREAD_SERVICE_ACCOUNT"])
        gc = gspread.service_account_from_dict(service_account_info)
        SHEET_URL = "https://docs.google.com/spreadsheets/d/13KVDHGDG7xITg7gLor1LphhSHJEI-_LGmy3NDUVDNi8"
        worksheet = gc.open_by_url(SHEET_URL).sheet1
        tools_data = worksheet.get_all_records()
        tools_df = pd.DataFrame(tools_data)
        tools_df.columns = [col.strip() for col in tools_df.columns]
        categories_available = sorted(list(set(tools_df["Category"].dropna().unique())))
    except:
        categories_available = []
    cat_filter = st.multiselect("Show only these categories:", categories_available)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Branding and Title ---
st.markdown(f"""
<div style='text-align:center; margin-bottom:22px'>
    <img src="https://cdn-icons-png.flaticon.com/512/3468/3468379.png" width="84" style="margin-bottom:-10px;box-shadow:0 2px 8px #1a1a2b25;border-radius:22px;">
    <h1 style='margin-bottom:0;color:#1266c2;font-size:2.3rem;font-family:Segoe UI,Arial;'>SmartToolMatch</h1>
    <div style='font-size:18px;margin-top:0;color:{txt_sub};font-weight:500;'>Your AI App Discovery & Guidance Engine</div>
</div>
""", unsafe_allow_html=True)

# --- Gemini setup (if not done above) ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
gemini_model = genai.GenerativeModel("gemini-1.5-pro")

# --- User Input ---
user_goal = st.text_input(
    "What do you want to achieve? (e.g., Plan a trip, Generate a resume, Create a presentation)",
    key="user_goal", help="This will power both AI recommendations and Gemini's step-by-step advice"
)

# --- Gemini-powered tool selection function + 'why' ---
def gemini_tool_picker(goal, df, topn=2):
    if df.empty:
        return []
    tools_brief = "\n".join([f"{row['Tool Name']}: {row['Best For']} | {row['Short Description']}" for _, row in df.iterrows()])
    prompt = (
        f"User wants to: {goal}\n"
        f"From this list of tools (each line: Tool Name: Best For | Short Description):\n{tools_brief}\n\n"
        f"Pick the {topn} best tools for this user's goal (from this list only). For each, reply in this exact format:\n"
        f"Tool Name | Why it's a great match for this goal (1 line)\n"
        f"Only return {topn} tools, no intro."
    )
    try:
        resp = gemini_model.generate_content(prompt).text.strip()
        picks = []
        seen = set()
        for line in resp.split('\n'):
            parts = line.split('|')
            if len(parts) >= 2:
                tool_name = parts[0].strip()
                why = parts[1].strip()
                if tool_name and tool_name not in seen:
                    row = df[df["Tool Name"] == tool_name]
                    if not row.empty:
                        record = dict(row.iloc[0])
                        record["_why"] = why
                        picks.append(record)
                        seen.add(tool_name)
            if len(picks) == topn:
                break
        return picks
    except Exception as e:
        return []

# --- Compare two tools ---
def compare_tools(tool1, tool2):
    def nice(val): return val if pd.notna(val) and str(val).strip() else "-"
    return f"""
    <div style="display:flex;gap:22px;">
      <div style="flex:1;background:{compare_highlight};padding:18px 10px 12px 15px;border-radius:14px;">
        <img src="{tool1['Logo URL']}" width="38" style="border-radius:8px;margin-bottom:8px;">
        <div style="font-size:1.17rem;font-weight:600;color:#1a222f;">{tool1['Tool Name']}</div>
        <div><b>Category:</b> {tool1['Category']}</div>
        <div><b>Best For:</b> {nice(tool1['Best For'])}</div>
        <div><b>Pricing:</b> {nice(tool1['Pricing'])}</div>
        <div><b>Description:</b> {nice(tool1['Short Description'])}</div>
        <div><b>Tags:</b> {nice(tool1['Tags'])}</div>
      </div>
      <div style="flex:1;background:{compare_highlight};padding:18px 10px 12px 15px;border-radius:14px;">
        <img src="{tool2['Logo URL']}" width="38" style="border-radius:8px;margin-bottom:8px;">
        <div style="font-size:1.17rem;font-weight:600;color:#1a222f;">{tool2['Tool Name']}</div>
        <div><b>Category:</b> {tool2['Category']}</div>
        <div><b>Best For:</b> {nice(tool2['Best For'])}</div>
        <div><b>Pricing:</b> {nice(tool2['Pricing'])}</div>
        <div><b>Description:</b> {nice(tool2['Short Description'])}</div>
        <div><b>Tags:</b> {nice(tool2['Tags'])}</div>
      </div>
    </div>
    """

# --- Main Layout: 2 columns ---
if user_goal:
    col1, col2 = st.columns([1.15, 1.05], gap="large")
    # --- Left: Recommendations ---
    with col1:
        st.markdown(
            f"<div style='font-size:1.4rem;font-weight:700;margin-bottom:6px;color:{accent};letter-spacing:-1px;'>🔎 Best AI App Recommendations</div>",
            unsafe_allow_html=True,
        )
        default_logo = "https://cdn-icons-png.flaticon.com/512/3468/3468379.png"
        already_picked = set()
        category_map = [
            ("Free", "🟩 Free Tools"),
            ("Paid", "🟦 Paid Tools"),
            ("Universal", "🟪 Universal Tools"),
        ]
        # --- Category filter applied ---
        df_filtered = tools_df.copy()
        if cat_filter:
            df_filtered = df_filtered[df_filtered["Category"].isin(cat_filter)]

        tool_for_compare = []  # For compare mode
        for cat, cat_label in category_map:
            df_cat = df_filtered[
                df_filtered['Type'].str.lower().str.contains(cat.lower(), na=False) &
                ~df_filtered['Tool Name'].isin(already_picked)
            ]
            picks = gemini_tool_picker(user_goal, df_cat, topn=2)
            if not picks and not df_cat.empty:
                filtered = df_cat.copy()
                score = (
                    filtered['Best For'].str.lower().str.contains(user_goal.lower(), na=False).astype(int)
                    + filtered['Short Description'].str.lower().str.contains(user_goal.lower(), na=False).astype(int)
                )
                filtered['score'] = score
                picks = [dict(row) for _, row in filtered.sort_values("score", ascending=False).head(2).iterrows()]
            if picks:
                already_picked.update([tool["Tool Name"] for tool in picks])
                st.markdown(f"<div style='font-weight:600;font-size:17px;margin-top:14px;color:{txt_main};text-shadow:0 1px 5px #1c213150;'>{cat_label}</div>", unsafe_allow_html=True)
                cols = st.columns(len(picks))
                for i, tool in enumerate(picks):
                    tool_logo = tool['Logo URL']
                    if not (isinstance(tool_logo, str) and tool_logo.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))):
                        tool_logo = default_logo
                    with cols[i]:
                        st.markdown(f"""
                        <div style="background:{card_bg};border-radius:15px;padding:18px 12px 13px 12px;margin-bottom:13px;box-shadow:{card_shadow};transition:box-shadow 0.18s;">
                            <div style="display:flex;align-items:center;margin-bottom:9px;">
                                <img src="{tool_logo}" width="48" height="48" style="border-radius:11px;margin-right:11px;border:2px solid #444;">
                                <div>
                                    <b><a href="{tool['Link']}" target="_blank" style="color:{accent};font-size:1.13rem;">{tool['Tool Name']}</a></b>
                                    <div style="font-size:13.7px;color:{txt_sub};">({tool['Category']})</div>
                                </div>
                            </div>
                            <div style="color:{good};font-size:15px;"><b>Best For:</b> {tool['Best For']}</div>
                            <div style="font-size:15px;margin-top:2.5px;color:{txt_main};"><i>{tool['Short Description']}</i></div>
                            <div style="font-size:14px;color:{accent};margin-top:2.5px;"><b>Pricing:</b> {tool['Pricing']}</div>
                            <div style="font-size:13px;color:#b2b5c6;margin-top:2px;">{tool['Tags']}</div>
                            <div style="margin-top:8px;font-size:14px;color:#ffe68b;">
                                <b>Why this tool?</b> <span style="color:#ffe;">{tool.get('_why', 'Gemini matched this tool to your goal')}</span>
                            </div>
                            <div style="margin-top:7px;">
                                <button style="background:{accent};color:#fff;padding:3px 13px 4px 13px;border:none;border-radius:6px;cursor:pointer;font-size:13px;" onclick="window.parent.postMessage({{compareTool:'{tool['Tool Name']}' }}, '*')">Compare</button>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        # For compare mode, keep track:
                        tool_for_compare.append(tool)

        # --- Compare Mode UI ---
        st.markdown("----")
        st.markdown("<div style='font-size:1.07rem;font-weight:600;margin-bottom:7px;'>🆚 Compare any two tools side by side:</div>", unsafe_allow_html=True)
        tool_names = [tool["Tool Name"] for tool in tool_for_compare]
        c1, c2 = st.columns(2)
        tool1 = c1.selectbox("Tool 1", ["None"] + tool_names, key="compare_tool1")
        tool2 = c2.selectbox("Tool 2", ["None"] + tool_names, key="compare_tool2")
        if tool1 != "None" and tool2 != "None" and tool1 != tool2:
            t1 = next(t for t in tool_for_compare if t["Tool Name"] == tool1)
            t2 = next(t for t in tool_for_compare if t["Tool Name"] == tool2)
            st.markdown(compare_tools(t1, t2), unsafe_allow_html=True)

    # --- Right: Gemini/AI Assistant ---
    with col2:
        st.markdown(
            f"<div style='font-size:1.3rem;font-weight:700;margin-bottom:9px;margin-top:2px;color:#f6baff;letter-spacing:-1px;'>🤖 AI Assistant Advice</div>",
            unsafe_allow_html=True,
        )
        try:
            ai_response = gemini_model.generate_content(
                f"You are a helpful, positive AI assistant. The user wants to: {user_goal}. "
                "Give a practical, step-by-step answer (5–8 sentences), mentioning where AI helps. "
                "Don't just list tools—be insightful, warm, and actionable. Start with a friendly greeting."
            ).text.strip()
            st.markdown(f"""
            <div style="background:{ai_bg};padding:18px 20px 15px 17px;border-radius:16px;margin-bottom:20px;box-shadow:0 2px 14px #25023c22;">
                <span style="font-size:1.09rem;color:{txt_main};">{ai_response}</span>
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
<<<<<<< HEAD
st.caption("© 2025 SmartToolMatch • Built with ❤️ by [Vijay Kumar Balusa](https://www.linkedin.com/in/vijay-kumar-bvk) • Powered by Gemini & Google Sheets")
=======
st.caption("© 2025 SmartToolMatch • Built with ❤️ by [Vijay Kumar Balusa](https://www.linkedin.com/in/vijay-kumar-bvk) • Powered by Gemini & Google Sheets")
>>>>>>> 74338c0 (Save local changes before pull)
