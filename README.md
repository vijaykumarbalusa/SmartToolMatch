# 🚀 SmartToolMatch

<<<<<<< HEAD
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
=======
> Your Personal AI App Discovery & Workflow Assistant

[![Live Demo](https://img.shields.io/badge/Streamlit%20App-Live-4B8DF8?logo=streamlit&logoColor=white)](https://smarttoolmatch-mzzwgvq2vevayfmheq39b7.streamlit.app)  
[![LinkedIn](https://img.shields.io/badge/Built%20by-Vijay%20Kumar%20Balusa-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/vijay-kumar-bvk)  
[![Google Sheets](https://img.shields.io/badge/Data-Google%20Sheets-34A853?logo=googlesheets&logoColor=white)](https://docs.google.com/spreadsheets/d/13KVDHGDG7xITg7gLor1LphhSHJEI-_LGmy3NDUVDNi8/edit?usp=sharing)

---

## ✨ What is SmartToolMatch?

SmartToolMatch is an AI-driven app that:

1. **Recommends the best Free, Paid, and Universal AI tools** for any user-specified goal.  
2. Provides **step-by-step workflow advice**, powered by Google Gemini AI.  
3. Enables **live comparison** of any two tools.  
4. Is fully **editable via Google Sheets** — update your tool library without redeploying.  
5. Features an elegant **two-column layout** perfect for user clarity and recruiter demos.

---

## 🚦 How It Works

| Step | Description |
|------|-------------|
|**1. User Input**| Type a goal (e.g., "Plan a trip", "Build a resume").|
|**2. Gemini AI**| Suggests top tools (Free/Paid/Universal) with "Why this tool?" insights.|
|**3. Workflow Steps**| Gemini also provides a step-by-step guide for your goal.|
|**4. Compare Tools**| Select any two tools and view a side-by-side feature comparison.|
|**5. Instant Launch**| Click tool cards to open apps in new tabs.|

---

## 🛠️ Tech Stack

- **Frontend/UI:** Streamlit  
- **AI Engine:** Google Gemini via `google-generativeai`  
- **Database:** Google Sheets (via `gspread`)  
- **Data Management:** `pandas` & `json`  
- **Deployment:** Streamlit Community Cloud  

---

## 📁 Repo Structure

SmartToolMatch/
│
├─ app.py # Main Streamlit application
├─ requirements.txt # Python dependencies
├─ README.md # Project overview & instructions
├─ .streamlit/ # (Optional) config files (themes, etc.)
└─ LICENSE # (Recommended) MIT or other open-source license


---

## 🚀 Deploy in 5 Minutes

1. **Fork/Clone** this repo:

    ```bash
    git clone https://github.com/vijaykumarbalusa/SmartToolMatch.git
    cd SmartToolMatch
    ```

2. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

3. **Configure Streamlit Secrets**:

   Access the Streamlit Cloud app's *Settings → Secrets* and paste:

    ```toml
    GEMINI_API_KEY = "your-gemini-api-key"
    
    GSPREAD_SERVICE_ACCOUNT = '''
    { 
      "...": "...",
      # entire JSON key contents
    }
    '''
    ```

4. **Update Google Sheet**:

   Use the [Tools database here](https://docs.google.com/spreadsheets/d/13KVDHGDG7xITg7gLor1LphhSHJEI-_LGmy3NDUVDNi8/edit) and ensure it’s shared as “View” or “Editor” for anyone with the link.

5. **Run Locally**:

    ```bash
    streamlit run app.py
    ```

6. **Deploy to Streamlit Cloud**:

   - Push your repo to GitHub.
   - In Streamlit Cloud, click **New app**, select your `SmartToolMatch` repo, use `app.py` as the main file, set branch to `main`.
   - Press **Deploy** and wait for the live URL.

7. **Update README** with your live app URL.

---

## ✅ Recommended Improvements

To further polish your repo and presentation:

- **Add a LICENSE** (e.g., MIT) for open-source clarity.
- **Include screenshots/GIFs** in a `/demo` folder and reference them in README.
- **Add `.streamlit/config.toml`** for UI theming (dark/light toggle).
- **Consider unit tests or CI badge** for quality signals.
- **Add brief CONTRIBUTING.md** to invite collaborators or feedback.

---

## 🙌 Why Invite Recruiters?

SmartToolMatch is more than a demo—it’s a complete AI-backed product with:

- Multi-tool intelligence
- Live data via Google Sheets
- Polished UX/UI
- Real-world utility for any workflow

Perfect for showcasing both your **engineering skills and product mindset**.

---

## 💬 Questions or Feedback?

Reach out to me on LinkedIn 👉 [Vijay Kumar Balusa](https://www.linkedin.com/in/vijay-kumar-bvk)

---

**Ready to go live?** Add your deployed URL above, polish your README with screenshots, and you’re all set to impress recruiters and users alike!
::contentReference[oaicite:0]{index=0}
>>>>>>> 4a4ef8560d175180aeab172910bbfa5cda251518
