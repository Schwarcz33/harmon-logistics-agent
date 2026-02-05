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
    st.error("🚨 Secrets Error. Please check API keys.")
    st.stop()

# --- 🧠 BRAIN (Self-Healing Modern Version) ---
# This list ensures if one model is busy/missing, it tries the next one.
MODELS_TO_TRY = ["gemini-2.5-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash"]
VOICE_ID = "0NgMq4gSzOuPcjasSGQk" # Paul Harmon

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
voice_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def get_gemini_response(prompt, sys_instruct):
    for model in MODELS_TO_TRY:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(system_instruction=sys_instruct)
            )
            return response.text
        except:
            continue
    return "I'm having trouble connecting to the network. Please try again in a moment."

# --- 🔊 VOICE ---
def text_to_speech(text):
    try:
        audio_generator = voice_client.text_to_speech.convert(
            text=text, voice_id=VOICE_ID, model_id="eleven_multilingual_v2", output_format="mp3_44100_128"
        )
        return b"".join(audio_generator)
    except:
        return None

# --- 🎨 UI: DARK MODERN WIDGET ---
st.set_page_config(page_title="Harmon Dispatch", page_icon="🚛", layout="centered")

st.markdown("""
<style>
    /* 1. BACKGROUND */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    
    /* 2. HIDE SIDEBAR */
    section[data-testid="stSidebar"] {display: none;}

    /* 3. HEADER CARD */
    .header-container {
        background-color: #161B22;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #30363D;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .header-title {
        color: #FFD700;
        font-family: sans-serif;
        font-weight: 800;
        font-size: 26px;
        margin: 0;
        text-transform: uppercase;
    }
    
    /* 4. CONTACT FOOTER */
    .contact-footer {
        margin-top: 30px;
        padding: 15px;
        border-top: 1px solid #30363D;
        text-align: center;
        font-size: 13px;
        color: #8b949e;
    }
    .contact-item {
        margin: 5px 0;
        color: #c9d1d9;
    }

    /* 5. CHAT BUBBLES */
    .stChatMessage {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 15px;
    }
    .stChatMessage[data-testid="user-message"] {
        background-color: #1F6FEB;
        color: white;
        border: none;
    }
    
    /* 6. INPUT FIELD */
    .stTextInput input {
        background-color: #0D1117;
        color: white;
        border: 1px solid #30363D;
    }
    
    /* 7. BUTTONS */
    div.stButton > button {
        background-color: #21262D;
        color: white;
        border: 1px solid #30363D;
        width: 100%;
        border-radius: 10px;
    }
    div.stButton > button:hover {
        border-color: #FFD700;
        color: #FFD700;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 🚛 HEADER ---
st.markdown("""
<div class="header-container">
    <div class="header-title">🚛 HARMON TRANSPORT</div>
    <div style="color: #28a745; font-size: 12px; font-weight: bold; margin-top: 5px;">● 24/7 DISPATCH ONLINE</div>
</div>
""", unsafe_allow_html=True)

# --- STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 👋 WELCOME ---
if not st.session_state.messages:
    st.markdown("<div style='text-align: center; margin-bottom: 20px; opacity: 0.8;'>Paul Harmon is listening. How can we move your freight?</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📦 Get a Quote"):
            st.session_state.messages.append({"role": "user", "content": "I need a quote for a load."})
    with c2:
        if st.button("⚡ Urgent Hot Shot"):
            st.session_state.messages.append({"role": "user", "content": "I have an urgent hot shot delivery."})

# --- 📜 HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- ⌨️ INPUT ---
input_container = st.container()
with input_container:
    voice_input = speech_to_text(
        language='en', start_prompt="🎙️ PUSH TO TALK", stop_prompt="⏹️ SEND", just_once=False, key="voice_btn", use_container_width=True
    )
    chat_input = st.chat_input("Type message here...")

# --- 🧠 LOGIC ---
user_prompt = None
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user" and len(st.session_state.messages) % 2 != 0:
    user_prompt = st.session_state.messages[-1]["content"]

if voice_input:
    user_prompt = voice_input
elif chat_input:
    user_prompt = chat_input

if user_prompt:
    if not st.session_state.messages or st.session_state.messages[-1]["content"] != user_prompt:
        st.chat_message("user").markdown(user_prompt)
        st.session_state.messages.append({"role": "user", "content": user_prompt})

    sys_instruct = """
    ROLE: You are Paul Harmon, Owner of Harmon Transportation.
    TONE: Professional, Aussie, Direct.
    CONTEXT: Widget chat. Keep it SHORT.
    FACTS: HQ Wangara, 24T Capacity, 24/7 Service, FMP/JMP Safety.
    """
    
    with st.spinner("Paul is typing..."):
        bot_reply = get_gemini_response(user_prompt, sys_instruct)

    with st.chat_message("assistant"):
        st.markdown(bot_reply)
        audio_bytes = text_to_speech(bot_reply)
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

# --- 📍 FOOTER ---
st.markdown("""
<div class="contact-footer">
    <div class="contact-item">📍 <b>Wangara HQ:</b> 2/11 Uppill Pl, Wangara WA 6065</div>
    <div class="contact-item">📧 paul@harmontransportation.com.au</div>
    <div class="contact-item">📱 0456 198 939</div>
</div>
""", unsafe_allow_html=True)
