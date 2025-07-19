# 🚀 SmartToolMatch

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