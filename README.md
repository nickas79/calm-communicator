# 🪶 Calm Communicator (MVP)
Say what you mean — with calm, clarity, and confidence.

This app helps people analyze and rewrite messages to sound calmer, kinder, and clearer — without losing meaning.

## Features
- Tone analysis (Calm, Empathy, Assertiveness, Clarity, Formality)
- One-click rewrites in selectable styles
- Side-by-side Before/After comparison
- Reflection prompt (What do you want the reader to feel?)
- Session history (see your last few rewrites)

## Quick Start
1. Install Python 3.10+
2. Install dependencies
   ```bash
   pip install streamlit openai python-dotenv
   ```
3. Set your OpenAI API key
   ```bash
   export OPENAI_API_KEY="sk-yourkeyhere"
   ```
   Windows PowerShell:
   ```powershell
   setx OPENAI_API_KEY "sk-yourkeyhere"
   ```
4. Run the app
   ```bash
   streamlit run app.py
   ```

## Deployment
- Upload to GitHub
- Deploy on [Streamlit Cloud](https://streamlit.io)
- In **Settings → Secrets**, add:
  ```
  OPENAI_API_KEY = "sk-yourkeyhere"
  ```

Once deployed, your app will be live at a URL like:
`https://calm-communicator-yourname.streamlit.app`
