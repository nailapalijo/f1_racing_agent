import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import json

from agent.local_llm import generate_response
from agent.voice_input import transcribe_audio


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="APEX | F1 Racing Intelligence",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==========================================
# SESSION STATE
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "apex_question" not in st.session_state:
    st.session_state.apex_question = ""

if "voice_language" not in st.session_state:
    st.session_state.voice_language = ""

if "voice_recording_id" not in st.session_state:
    st.session_state.voice_recording_id = 0


# ==========================================
# STYLING
# ==========================================

st.markdown("""
<style>

.stApp {
    background: #070910;
    color: #f5f7fb;
}

header, footer, #MainMenu {
    visibility: hidden;
}

.block-container {
    max-width: 100%;
    padding: 1rem 1.5rem 3rem 1.5rem;
}

h1, h2, h3, p, label {
    color: #f5f7fb;
}

.hero-title {
    font-family: Arial, sans-serif;
    font-size: clamp(32px, 5vw, 60px);
    font-weight: 900;
    letter-spacing: 3px;
    margin: 0;
}

.hero-title span,
.ai-heading span {
    color: #ff3038;
}

.hero-sub {
    color: #9ba6bb;
    letter-spacing: 4px;
    font-size: 11px;
    margin-top: 5px;
}

.section-label {
    color: #ff3434;
    font-size: 11px;
    letter-spacing: 3px;
    font-weight: bold;
}

.info-card {
    background: linear-gradient(145deg, #171c29, #0b0e17);
    border: 1px solid #292e3b;
    border-radius: 12px;
    padding: 18px;
    min-height: 105px;
}

.info-label {
    color: #9ba6bb;
    font-size: 11px;
    letter-spacing: 2px;
}

.info-value {
    color: white;
    font-size: 23px;
    font-weight: 800;
    margin-top: 8px;
}

.info-note {
    color: #ff3434;
    font-size: 11px;
    margin-top: 3px;
}

.ai-panel {
    background: linear-gradient(145deg, #141b2a, #090d17);
    border: 1px solid #343b4c;
    border-radius: 16px;
    padding: 22px;
    margin-top: 18px;
    margin-bottom: 12px;
}

.ai-heading {
    color: white;
    font-size: 25px;
    font-weight: 900;
    letter-spacing: 2px;
}

.ai-description {
    color: #9ba6bb;
    font-size: 11px;
    letter-spacing: 1.5px;
    margin-top: 7px;
}

div[data-testid="stTextInput"] input {
    background: #111725 !important;
    color: #ffffff !important;
    border: 1px solid #3a4357 !important;
    border-radius: 10px !important;
}

div[data-testid="stTextInput"] input::placeholder {
    color: #b7c0d2 !important;
}

div[data-testid="stFormSubmitButton"] button {
    background: #e32636 !important;
    color: white !important;
    border: none !important;
    border-radius: 9px !important;
    font-weight: 800 !important;
    min-height: 45px;
}

div[data-testid="stFormSubmitButton"] button:hover {
    background: #ff4350 !important;
}

div[data-testid="stButton"] button {
    border: 1px solid #e32636;
    color: white;
    background: #151b29;
    border-radius: 9px;
    min-height: 40px;
}

div[data-testid="stChatMessage"] {
    background: #111725;
    border: 1px solid #293246;
    border-radius: 12px;
}

div[data-testid="stChatMessage"] p {
    color: #ffffff !important;
}

.stMarkdown, .stCaption {
    color: #d6dbea;
}

div[data-testid="stAudioInput"] {
    background: #111725;
    border: 1px solid #343b4c;
    border-radius: 12px;
    padding: 12px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# HELPER: GENERATE APEX ANSWER
# ==========================================

def process_question(question):

    question = question.strip()

    if not question:
        return

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    try:

        with st.spinner(
            "APEX is thinking... Local Qwen is generating your answer."
        ):

            answer = generate_response(question)

        if not answer:
            answer = "APEX could not generate an answer. Please try again."

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

    except Exception as error:

        st.session_state.messages.append({
            "role": "assistant",
            "content": f"AI engine error: {error}"
        })


# ==========================================
# HERO
# ==========================================

st.markdown(
    '<div class="hero-title">APEX<span>.</span> RACING</div>'
    '<div class="hero-sub">'
    'NEXT-GENERATION FORMULA RACING INTELLIGENCE'
    '</div>',
    unsafe_allow_html=True
)

st.write("")


# ==========================================
# 3D RACING SCENE
# ==========================================

scene_path = (
    Path(__file__).parent
    / "assets"
    / "racing_scene.html"
)

if scene_path.exists():

    html_content = scene_path.read_text(
        encoding="utf-8"
    )

    components.html(
        html_content,
        height=650,
        scrolling=False
    )

else:

    st.error(
        "3D racing scene not found: assets/racing_scene.html"
    )


# ==========================================
# RACE CONTROL CENTER
# ==========================================

st.markdown(
    '<div class="section-label">RACE CONTROL CENTER</div>',
    unsafe_allow_html=True
)

st.write("")

c1, c2, c3, c4 = st.columns(4)

cards = [
    (c1, "ENGINE", "3D SIMULATION", "Three.js powered"),
    (c2, "CIRCUIT", "CUSTOM TRACK", "Animated circuit"),
    (c3, "VEHICLE", "F1 PROTOTYPE", "Procedural 3D model"),
    (c4, "AI MODE", "LOCAL QWEN", "Offline AI inference"),
]

for col, label, value, note in cards:

    with col:

        st.markdown(
            f'<div class="info-card">'
            f'<div class="info-label">{label}</div>'
            f'<div class="info-value">{value}</div>'
            f'<div class="info-note">{note}</div>'
            f'</div>',
            unsafe_allow_html=True
        )


# ==========================================
# APEX AI COMMAND CENTER
# ==========================================

st.write("")

st.markdown(
    '<div class="ai-panel">'
    '<div class="ai-heading">'
    'APEX<span>.</span> AI COMMAND CENTER'
    '</div>'
    '<div class="ai-description">'
    'LOCAL INTELLIGENCE ENGINE | '
    'FORMULA 1 RACING ASSISTANT | '
    'NO EXTERNAL AI API'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)


# ==========================================
# CHAT HEADER AND CLEAR BUTTON
# ==========================================

left, right = st.columns([5, 1])

with left:

    st.caption(
        "Ask questions about Formula 1, drivers, teams, "
        "circuits, engines, tyres and racing strategies."
    )

with right:

    if st.button("CLEAR CHAT", use_container_width=True):

        st.session_state.messages = []
        st.session_state.apex_question = ""
        st.session_state.voice_language = ""

        st.rerun()


# ==========================================
# VOICE CONTROL
# ==========================================

st.write("")

st.markdown(
    '<div class="section-label">VOICE CONTROL</div>',
    unsafe_allow_html=True
)

st.caption(
    "Record your question in English or Urdu. "
    "APEX will recognize your speech and generate an English answer."
)

audio_recording = st.audio_input(
    "Record your F1 question",
    sample_rate=16000,
    key=f"apex_audio_input_{st.session_state.voice_recording_id}"
)

voice_col1, voice_col2 = st.columns(2)

with voice_col1:

    ask_voice_clicked = st.button(
        "ASK APEX WITH VOICE",
        disabled=audio_recording is None,
        use_container_width=True,
        key="apex_voice_answer_button"
    )

with voice_col2:

    delete_voice_clicked = st.button(
        "DELETE RECORDING",
        disabled=audio_recording is None,
        use_container_width=True,
        key="apex_delete_recording_button"
    )


# DELETE RECORDING

if delete_voice_clicked:

    st.session_state.voice_recording_id += 1
    st.rerun()


# ASK APEX WITH VOICE

if ask_voice_clicked:

    try:

        with st.spinner("APEX is recognizing your voice..."):

            transcript, detected_language = transcribe_audio(
                audio_recording
            )

        if not transcript:

            st.warning(
                "No speech detected. Please record your question again."
            )

        else:

            st.session_state.voice_language = detected_language

            process_question(transcript)

            # Reset recording after successful processing.
            st.session_state.voice_recording_id += 1

            st.rerun()

    except Exception as error:

        st.error(
            f"APEX voice recognition error: {error}"
        )


# ==========================================
# QUESTION FORM
# ==========================================

st.write("")

st.markdown(
    '<div class="section-label">ASK APEX</div>',
    unsafe_allow_html=True
)

with st.form(
    "apex_question_form",
    clear_on_submit=True
):

    user_question = st.text_input(
        "YOUR QUESTION",
        placeholder="Type your F1 question here...",
        label_visibility="collapsed",
        key="apex_question"
    )

    submitted = st.form_submit_button(
        "ASK APEX",
        use_container_width=True
    )


# ==========================================
# TEXT QUESTION PROCESSING
# ==========================================

if submitted:

    question = user_question.strip()

    if not question:

        st.warning(
            "Please type or record a question first."
        )

    else:

        process_question(question)
        st.rerun()


# ==========================================
# CHAT HISTORY
# ==========================================

st.write("")

st.markdown(
    '<div class="section-label">CONVERSATION</div>',
    unsafe_allow_html=True
)

if not st.session_state.messages:

    st.info(
        "APEX is ready. Type or record your first Formula 1 question."
    )

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ==========================================
# ENGLISH VOICE RESPONSE
# ==========================================

latest_answer = next(
    (
        message["content"]
        for message in reversed(st.session_state.messages)
        if message["role"] == "assistant"
    ),
    None
)

if latest_answer:

    st.write("")

    st.markdown(
        '<div class="section-label">ENGLISH VOICE RESPONSE</div>',
        unsafe_allow_html=True
    )

    speech_text = json.dumps(
        latest_answer,
        ensure_ascii=True
    ).replace("</", "<\\/")

    speech_html = f"""
    <div style="
        background:#111725;
        border:1px solid #343b4c;
        border-radius:12px;
        padding:14px;
        display:flex;
        gap:10px;
        flex-wrap:wrap;
    ">

        <button id="apexSpeak" style="
            background:#e32636;
            color:white;
            border:0;
            border-radius:8px;
            padding:12px 20px;
            font-weight:bold;
            cursor:pointer;
        ">
            SPEAK ANSWER IN ENGLISH
        </button>

        <button id="apexStop" style="
            background:#293246;
            color:white;
            border:0;
            border-radius:8px;
            padding:12px 20px;
            cursor:pointer;
        ">
            STOP
        </button>

        <span id="apexVoiceStatus" style="
            color:#d6dbea;
            padding:10px;
            font-size:13px;
        ">
            English voice ready
        </span>

    </div>

    <script>

        const answerText = {speech_text};

        const speakButton = document.getElementById("apexSpeak");
        const stopButton = document.getElementById("apexStop");
        const status = document.getElementById("apexVoiceStatus");

        speakButton.onclick = function() {{

            if (!("speechSynthesis" in window)) {{

                status.textContent = "Speech playback is not supported.";
                return;

            }}

            window.speechSynthesis.cancel();

            const speech = new SpeechSynthesisUtterance(answerText);

            speech.lang = "en-US";
            speech.rate = 0.95;
            speech.pitch = 1.0;

            const voices = window.speechSynthesis.getVoices();

            const englishVoice = voices.find(
                voice => voice.lang.toLowerCase().startsWith("en-us")
            ) || voices.find(
                voice => voice.lang.toLowerCase().startsWith("en")
            );

            if (englishVoice) {{
                speech.voice = englishVoice;
            }}

            speech.onstart = function() {{
                status.textContent = "Speaking in English...";
            }};

            speech.onend = function() {{
                status.textContent = "Playback finished.";
            }};

            speech.onerror = function() {{
                status.textContent = "Voice playback error.";
            }};

            window.speechSynthesis.speak(speech);

        }};

        stopButton.onclick = function() {{

            window.speechSynthesis.cancel();
            status.textContent = "Playback stopped.";

        }};

    </script>
    """

    components.html(
        speech_html,
        height=100,
        scrolling=False
    )


# ==========================================
# FOOTER
# ==========================================

st.write("")
st.divider()

st.caption(
    "APEX F1 RACING INTELLIGENCE | "
    "LOCAL QWEN MODEL | OFFLINE WHISPER | "
    "3D RACING ENVIRONMENT"
)