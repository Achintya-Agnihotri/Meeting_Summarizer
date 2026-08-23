import os

import requests
import streamlit as st

API_URL = os.getenv("MEETING_API_URL", "http://localhost:8000")
SUPPORTED_TYPES = ["mp3", "wav", "m4a", "mp4", "mpeg", "webm"]

st.set_page_config(page_title="Meeting Summarizer", page_icon="M", layout="wide")
st.markdown("""<style>
.stApp { background:#0b1020; color:#e6edf7; }
.block-container { max-width:1120px; padding-top:2.5rem; padding-bottom:4rem; }
h1,h2,h3,p,li,label { color:#e6edf7 !important; }
.hero { padding:1.2rem 0 2rem; }.eyebrow { color:#8ca7ff !important; font-size:.82rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; }
.hero h1 { font-size:clamp(2.3rem,5vw,4rem); margin:.3rem 0 .7rem; letter-spacing:-.06em; }.hero p { color:#aebbd0 !important; font-size:1.1rem; max-width:42rem; }
.guide { background:linear-gradient(100deg,#121b35,#10182b); border:1px solid #273656; border-radius:18px; padding:1.2rem 1.4rem; margin-bottom:1.5rem; }.guide strong { color:#fff; }.guide span { color:#9badc7; }
[data-testid="stFileUploader"] { background:#11192c; border:1px dashed #496494; border-radius:16px; padding:1rem; }[data-testid="stFileUploader"] section { background:transparent; }[data-testid="stFileUploader"] button { color:#e6edf7; border-color:#506b9e; background:#18243f; }
.stButton > button { min-height:3.25rem; border:0; border-radius:12px; background:#6d7dff; color:#fff; font-weight:700; font-size:1rem; }.stButton > button:hover { background:#8491ff; color:#fff; }
.section-card { background:#11192c; border:1px solid #243250; border-radius:16px; padding:1.3rem 1.4rem; min-height:10rem; }.section-card h3 { margin-top:0; }.section-card p { color:#cbd5e1 !important; line-height:1.65; }.empty { color:#94a3b8 !important; font-style:italic; }
[data-testid="stDataFrame"] { border:1px solid #2b3b5e; border-radius:12px; overflow:hidden; }[data-testid="stExpander"] { background:#11192c; border:1px solid #243250; border-radius:12px; }[data-testid="stAlert"] { border-radius:12px; }
</style>""", unsafe_allow_html=True)
st.markdown("""<div class="hero"><div class="eyebrow">Local and private</div><h1>Meeting Summarizer</h1><p>Upload a recording and get a transcript, key decisions, and clear next steps - all processed on your computer.</p></div><div class="guide"><strong>How it works</strong><br><span>1. Add a meeting recording &nbsp;&nbsp; 2. Process it locally &nbsp;&nbsp; 3. Review the results below</span></div>""", unsafe_allow_html=True)

uploaded = st.file_uploader("Add meeting audio", type=SUPPORTED_TYPES, help="Supported formats: MP3, WAV, M4A, MP4, MPEG, and WebM. Maximum 25 MB.")
if uploaded:
    st.success(f"Ready to process: {uploaded.name} ({uploaded.size / 1024 / 1024:.1f} MB)")

if st.button("Summarize meeting", type="primary", disabled=uploaded is None, use_container_width=True):
    try:
        with st.spinner("Listening to the recording and preparing your meeting notes..."):
            response = requests.post(f"{API_URL}/summarize", files={"audio": (uploaded.name, uploaded.getvalue(), uploaded.type or "application/octet-stream")}, timeout=600)
        if response.ok:
            st.session_state.result = response.json()
            st.success("Your meeting notes are ready.")
        else:
            try:
                detail = response.json().get("detail", "Processing failed.")
            except ValueError:
                detail = "Processing failed. Check that the backend is running."
            st.error(detail)
    except requests.ConnectionError:
        st.error("Cannot reach the backend. Start it with: uvicorn backend.main:app --reload")
    except requests.Timeout:
        st.error("Processing took too long. Try a shorter recording or try again.")

result = st.session_state.get("result")
if result:
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Meeting notes")
    st.markdown(f"<div class='section-card'><h3>Executive summary</h3><p>{result['summary']}</p></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    decisions_col, actions_col = st.columns(2, gap="large")
    with decisions_col:
        st.markdown("<div class='section-card'><h3>Key decisions</h3>", unsafe_allow_html=True)
        if result["key_decisions"]:
            for decision in result["key_decisions"]:
                st.markdown(f"- {decision}")
        else:
            st.markdown("<p class='empty'>No explicit decisions were identified.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with actions_col:
        st.markdown("<div class='section-card'><h3>Action items</h3>", unsafe_allow_html=True)
        if result["action_items"]:
            st.dataframe([{"Task": item["task"], "Owner": item["owner"] or "Not specified", "Deadline": item["deadline"] or "Not specified"} for item in result["action_items"]], use_container_width=True, hide_index=True)
        else:
            st.markdown("<p class='empty'>No explicit action items were identified.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("View full transcript"):
        st.text(result["transcript"])
