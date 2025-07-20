# 🚀 SmartToolMatch

**AI-powered app discovery for whatever you want to build, automate, or learn.**

---

Hi! I’m Vijay. I built SmartToolMatch so anyone can skip the endless search for the right AI app—just type your goal and instantly get the best free, paid, and universal tools, plus step-by-step Gemini AI guidance.

- 💡 **Describe any task or workflow** (from “plan a trip” to “generate a resume”)
- 🎯 **Get the top AI apps for your need**—no duplicates, always fresh
- 🤖 **See why each tool is recommended**
- ✨ **Compare tools side-by-side** and launch them instantly
- 📝 **Add or update tools in Google Sheets—no redeploy needed!**

---

## 🚦 How does it work?

1. **Describe your goal** (career, marketing, creative, travel, etc)
2. The app finds the top tools (live from a Google Sheet) and explains “why” for each
3. Gemini AI gives you a quick, actionable workflow for your goal
4. You can filter by category, compare any two tools, and launch them with one click

---

## 🛠️ Tech behind the scenes

- **Frontend:** Streamlit
- **Live database:** Google Sheets (via gspread)
- **AI:** Google Gemini API
- **Hosting:** Streamlit Cloud

---

## 🖼️ Try it out!

[![Live Demo](https://img.shields.io/badge/TRY%20IT%20LIVE-Streamlit-4B8DF8?logo=streamlit)](https://smarttoolmatch-mzzwgvq2vevayfmheq39b7.streamlit.app)

Or run locally:

```bash
git clone https://github.com/vijaykumarbalusa/SmartToolMatch.git
cd SmartToolMatch
pip install -r requirements.txt
streamlit run app.py
Before you run:

Get your Gemini API key

Set up a Google Service Account

Add both keys to Streamlit secrets (see code comments for details)

✍️ Add your own tools!
Just edit the Google Sheet and your app updates in seconds.

🙋‍♂️ About Me
Made by Vijay Kumar Balusa.
Let’s connect on [![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/vijay-kumar-bvk)


If you find this useful, please star the repo and share it. Thanks for checking out SmartToolMatch!