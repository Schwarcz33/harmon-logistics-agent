import streamlit as st
import os
from google import genai
from google.genai import types
from elevenlabs.client import ElevenLabs
from streamlit_mic_recorder import speech_to_text

# --- 🔐 SECURITY ---
try:
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
    ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]
except:
    st.error("🚨 Key Error. Please check Secrets.")
    st.stop()

# --- 🧠 CONFIG ---
MODELS_TO_TRY = ["gemini-2.5-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash"]
VOICE_ID = "0NgMq4gSzOuPcjasSGQk" # Paul Harmon

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
voice_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# --- 🎨 UI: DARK MODERN WIDGET ---
st.set_page_config(page_title="Harmon Dispatch", page_icon="🚛", layout="centered")

# Custom CSS for "Dark Glass" Card Look
st.markdown("""
<style>
    /* 1. MAIN BACKGROUND (Deep Dark) */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* 2. HIDE SIDEBAR */
    section[data-testid="stSidebar"] {display: none;}

    /* 3. HEADER CARD */
    .header-container {
        background-color: #161B22;
        padding: 25px;
        border-radius: 20px;
        border: 1px solid #30363D;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    .header-title {
        color: #FFD700; /* Harmon Yellow */
        font-family: sans-serif;
        font-weight: 800;
        font-size: 24px;
        margin: 0;
    }
    .status-badge {
        background-color: #1F6FEB;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        text-transform: uppercase;
        display: inline-block;
        margin-top: 10px;
    }

    /* 4. CHAT BUBBLES (Dark & Sleek) */
    .stChatMessage {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 18px;
    }
    /* User: Dark Blue Tint */
    .stChatMessage[data-testid="user-message"] {
        background-color: #1a1a2e; 
        border: 1px solid #2d2d44;
        color: #E6EDF3;
    }
    /* AI: Dark Grey */
    .stChatMessage[data-testid="assistant-message"] {
        background-color: #161B22;
        border: 1px solid #30363D;
        color: #E6EDF3;
    }
    
    /* 5. SUGGESTION PILLS (Dark Mode) */
    div.stButton > button {
        background-color: #21262D;
        color: #E6EDF3;
        border: 1px solid #30363D;
        border-radius: 20px;
        width: 100%;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        border-color: #FFD700;
        color: #FFD700;
        background-color: #30363D;
    }
    
    /* 6. INPUT FIELD (Clean Dark) */
    .stTextInput input {
        background-color: #0D1117;
        color: white;
        border: 1px solid #30363D;
        border-radius: 12px;
    }
    
    /* 7. HIDE JUNK */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- FUNCTIONS ---
def text_to_speech(text):
    try:
        audio_generator = voice_client.text_to_speech.convert(
            text=text, voice_id=VOICE_ID, model_id="eleven_multilingual_v2", output_format="mp3_44100_128"
        )
        return b"".join(audio_generator)
    except:
        return None

def get_gemini_response(prompt, sys_instruct):
    for model in MODELS_TO_TRY:
        try:
            response = client.models.generate_content(
                model=model, contents=prompt, config=types.GenerateContentConfig(system_instruction=sys_instruct)
            )
            return response.text
        except:
            continue
    return "Connection Error."

# --- 🚛 WIDGET HEADER ---
st.markdown("""
<div class="header-container">
    <div class="header-title">🚛 HARMON TRANSPORT</div>
    <div class="status-badge">● 24/7 Operations Online</div>
</div>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 👋 WELCOME (Dark Mode) ---
if not st.session_state.messages:
    st.markdown("<div style='text-align: center; margin-top: 20px; margin-bottom: 30px; opacity: 0.8;'>", unsafe_allow_html=True)
    st.markdown("##### Connect with Dispatch")
    st.caption("Paul Harmon is listening. What are we moving today?")
    st.markdown("</div>", unsafe_allow_html=True)

    # Quick Action Pills
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📦 Quote a Pallet"):
            st.session_state.messages.append({"role": "user", "content": "I need a quote for a pallet delivery."})
    with col2:
        if st.button("⚡ Urgent Hot Shot"):
            st.session_state.messages.append({"role": "user", "content": "I need an urgent hot shot delivery."})

# --- 📜 HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- ⌨️ INPUT AREA ---
input_container = st.container()
with input_container:
    # Voice Button (Small & Dark)
    voice_input = speech_to_text(
        language='en', start_prompt="🎙️ PUSH TO TALK", stop_prompt="⏹️ SEND AUDIO", just_once=False, key="voice_btn", use_container_width=True
    )
    # Text Input
    chat_input = st.chat_input("Enter details...")

# --- 🧠 LOGIC ---
user_prompt = None
# Check for button click (from welcome screen)
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user" and len(st.session_state.messages) % 2 != 0:
    user_prompt = st.session_state.messages[-1]["content"]

if voice_input:
    user_prompt = voice_input
elif chat_input:
    user_prompt = chat_input

if user_prompt:
    # Prevent double-posting if it came from a button
    if not st.session_state.messages or st.session_state.messages[-1]["content"] != user_prompt:
        st.chat_message("user").markdown(user_prompt)
        st.session_state.messages.append({"role": "user", "content": user_prompt})

    sys_instruct = """
    ROLE: You are Paul Harmon, Owner of Harmon Transportation.
    TONE: Professional, Aussie, Direct.
    CONTEXT: Chat widget. Keep it short.
    FACTS: Wangara HQ, 24 Tonne Capacity, 24/7 Service.
    """
    
    with st.spinner("Paul is typing..."):
        bot_reply = get_gemini_response(user_prompt, sys_instruct)

    with st.chat_message("assistant"):
        st.markdown(bot_reply)
        audio_bytes = text_to_speech(bot_reply)
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
