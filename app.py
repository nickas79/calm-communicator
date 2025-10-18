import os
import json
import difflib
from textwrap import dedent
from typing import List, Dict
import streamlit as st

# ----------------- Config -----------------
DEFAULT_MODEL = "gpt-4o-mini"

# Read API key from Streamlit Secrets first, then env var (works on Streamlit Cloud)
OPENAI_API_KEY = None
try:
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", None)
except Exception:
    OPENAI_API_KEY = None
if not OPENAI_API_KEY:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Lazy import so app still loads without key
client = None
if OPENAI_API_KEY:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception:
        client = None

st.set_page_config(page_title="Calm Communicator", page_icon="🪶", layout="wide")

# ----------------- Helpers -----------------
def call_llm(messages: List[Dict], temperature: float = 0.3) -> str:
    if client is None:
        return "⚠️ No API key detected. Add OPENAI_API_KEY in Streamlit Secrets or environment."
    try:
        resp = client.chat.completions.create(
            model=DEFAULT_MODEL,
            temperature=temperature,
            messages=messages,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"⚠️ LLM error: {e}"

def analyze_tone(text: str) -> Dict:
    system = dedent("""
    You are a communication analyst. Rate the following text on a 0–100 scale for:
    - Calm (higher = calmer)
    - Empathy
    - Assertiveness
    - Clarity
    - Formality
    Also return a short label for overall tone (e.g., Calm, Tense, Defensive, Passive, Curt, Empathetic, Formal) and a 1–2 sentence rationale.
    Respond as compact JSON with keys: label, calm, empathy, assertiveness, clarity, formality, rationale.
    """)
    user = f'Text:\\n\"\"\"\\n{text}\\n\"\"\"'
    out = call_llm([{"role":"system","content": system},
                    {"role":"user","content": user}], temperature=0.0)
    try:
        data = json.loads(out)
        return data
    except Exception:
        try:
            start = out.find("{")
            end = out.rfind("}") + 1
            return json.loads(out[start:end])
        except Exception:
            return {"label":"Unknown","calm":0,"empathy":0,"assertiveness":0,"clarity":0,"formality":0,"rationale":out}

REWRITE_STYLES = {
    "Empathetic": "Empathetic, warm, validating the other person's perspective while keeping boundaries.",
    "Direct but Kind": "Direct, concise, specific; kind but clear about limits and expectations.",
    "Professional": "Neutral, concise, formal register appropriate for workplace email.",
    "Supportive": "Encouraging, collaborative, offers help and next steps without overpromising.",
    "Boundary-Setting": "Respectful but firm; clarifies limits, consequences, and next actions."
}

def rewrite_text(text: str, style: str) -> str:
    style_desc = REWRITE_STYLES.get(style, "Calm and clear.")
    system = dedent(f"""
    You are a calm communication coach. You preserve meaning while improving tone, clarity,
    and kindness. Use concise sentences. Avoid sarcasm and blame. Offer confident but warm language.
    Rewrite in the requested style. Only return the rewritten message.
    Requested style description: {style_desc}
    """)
    user = f'Original message:\\n\"\"\"\\n{text}\\n\"\"\"'
    return call_llm([{"role":"system","content": system},
                     {"role":"user","content": user}], temperature=0.4)

def make_diff(orig: str, new: str) -> str:
    o = orig.split()
    n = new.split()
    diff = difflib.ndiff(o, n)
    out_tokens = []
    for token in diff:
        if token.startswith("  "):
            out_tokens.append(token[2:])
        elif token.startswith("- "):
            out_tokens.append(f"~~{token[2:]}~~")
        elif token.startswith("+ "):
            out_tokens.append(f"**{token[2:]}**")
    return " ".join(out_tokens)

# ----------------- UI -----------------
st.title("🪶 Calm Communicator")
st.caption("Say what you mean — with calm, clarity, and confidence.")

with st.expander("How it works & privacy", expanded=False):
    st.markdown("""
- Paste any message. Click **Analyze** to see tone & scores.
- Choose a **Rewrite Style** and click **Rewrite** for an improved draft.
- This prototype calls an external LLM provider. Avoid sensitive identifiers.
- This tool does not provide legal, medical, or mental-health advice.
""")

col_left, col_right = st.columns([1,1])

with col_left:
    st.subheader("Your Message")
    text = st.text_area("Paste your message", height=260, placeholder="Type or paste an email, DM, or announcement…")

    st.markdown("**Optional reflection:** What do you want the reader to feel?")
    intent = st.text_input("e.g., respected, informed, reassured, accountable")
    analyze_btn = st.button("Analyze Tone")
    style = st.selectbox("Rewrite Style", list(REWRITE_STYLES.keys()))
    rewrite_btn = st.button("Rewrite Message")

with col_right:
    st.subheader("Results")
    if analyze_btn and text.strip():
        res = analyze_tone(text.strip())
        st.markdown(f"**Overall tone:** {res.get('label','Unknown')}")
        st.markdown(f"- Calm: {res.get('calm',0)}")
        st.markdown(f"- Empathy: {res.get('empathy',0)}")
        st.markdown(f"- Assertiveness: {res.get('assertiveness',0)}")
        st.markdown(f"- Clarity: {res.get('clarity',0)}")
        st.markdown(f"- Formality: {res.get('formality',0)}")
        st.markdown(f"> {res.get('rationale','')}")

    if rewrite_btn and text.strip():
        prompt = text.strip()
        if intent.strip():
            prompt += f"\n\nWriter's intent: Make the reader feel {intent.strip()}."
        rewritten = rewrite_text(prompt, style)
        st.markdown("### Rewritten")
        st.text_area("Improved draft", value=rewritten, height=220)
        st.download_button("⬇️ Copy/Download Rewritten", data=rewritten.encode("utf-8"), file_name="calm_communicator_rewrite.txt")

        st.markdown("### Before / After (diff)")
        st.markdown(make_diff(text.strip(), rewritten))

# Simple session history
st.markdown("---")
st.subheader("History (this session)")
if "history" not in st.session_state:
    st.session_state.history = []

if rewrite_btn and text.strip():
    st.session_state.history.append(
        {"original": text.strip(), "style": style, "intent": intent.strip(), "rewritten": rewritten}
    )

if st.session_state.history:
    for i, item in enumerate(reversed(st.session_state.history[-5:]), start=1):
        st.markdown(f"**#{i}** • Style: *{item['style']}* • Intent: *{item['intent'] or '—'}*")
        st.markdown("**Original**")
        st.code(item["original"])
        st.markdown("**Rewritten**")
        st.code(item["rewritten"])
