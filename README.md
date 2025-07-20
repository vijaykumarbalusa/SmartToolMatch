# 🚀 SmartToolMatch

**AI-powered app discovery for whatever you want to build, automate, or learn.**

---

Hi! I’m Vijay. I built SmartToolMatch so you (or anyone) can stop wasting hours searching for the right AI app—just type your goal and instantly get the best free, paid, and universal tools, plus practical step-by-step advice.

- 💡 **Describe any task or workflow** (from “plan a trip” to “generate a resume”)
- 🎯 **Get the top AI apps for your need**—no duplicates, always fresh
- 🤖 **See exactly why each tool is recommended**
- ✨ **Compare tools side-by-side** and launch them instantly
- 📝 **Update the whole tool list by editing a Google Sheet—no redeploy needed!**

---

## 🚦 How does it work?

1. **Tell SmartToolMatch your goal** (anything: career, marketing, creative, travel, etc)
2. The app finds the top tools from a live Google Sheet and explains “why” for each
3. Gemini AI gives you a quick, actionable workflow for your goal
4. You can filter by category, compare any two tools, and click to use them right away

---

## 🛠️ Tech behind the scenes

- **Frontend:** Streamlit
- **Live database:** Google Sheets (via gspread)
- **AI:** Google Gemini API
- **Hosting:** Streamlit Cloud

---

## 🖼️ Try it out!

[![Live Demo](https://img.shields.io/badge/TRY%20IT%20LIVE-Streamlit-4B8DF8?logo=streamlit)](https://smarttoolmatch-mzzwgvq2vevayfmheq39b7.streamlit.app)

Or just clone it, install dependencies, and run:

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

I’m Vijay Kumar Balusa.
Connect on [![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/vijay-kumar-bvk)
 or reach out if you have feedback, ideas, or want to collaborate!
 
If you find this useful, please star the repo and share it. Thanks for checking out SmartToolMatch!