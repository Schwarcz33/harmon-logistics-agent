import streamlit as st
import os
import google.generativeai as genai
from elevenlabs.client import ElevenLabs
from streamlit_mic_recorder import speech_to_text

# --- 🔐 SECURITY ---
try:
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
    ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]
except:
    st.error("🚨 Secrets Error. Please check API keys.")
    st.stop()

# --- 🧠 BRAIN (Classic Stable Version) ---
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def get_gemini_response(prompt, sys_instruct):
    # We use the standard model which is most reliable
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=sys_instruct)
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"System Error: {str(e)}"

# --- 🔊 VOICE ---
voice_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
VOICE_ID = "0NgMq4gSzOuPcjasSGQk" # Paul Harmon

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

# Custom CSS for "Dark Glass" Card Look
st.markdown("""
<style>
    /* 1. MAIN BACKGROUND (Deep Dark) */
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
        color: #FFD700; /* Harmon Yellow */
        font-family: sans-serif;
        font-weight: 800;
        font-size: 26px;
        margin: 0;
        text-transform: uppercase;
    }
    
    /* 4. CONTACT FOOTER (The Missing Piece) */
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
        background-color: #1F6FEB; /* Blue */
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

# --- 🚛 WIDGET HEADER ---
st.markdown("""
<div class="header-container">
    <div class="header-title">🚛 HARMON TRANSPORT</div>
    <div style="color: #28a745; font-size: 12px; font-weight: bold; margin-top: 5px;">● 24/7 DISPATCH ONLINE</div>
</div>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
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

# --- 📜 CHAT HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- ⌨️ INPUT ---
input_container = st.container()
with input_container:
    # Voice Button
    voice_input = speech_to_text(
        language='en', start_prompt="🎙️ PUSH TO TALK", stop_prompt="⏹️ SEND", just_once=False, key="voice_btn", use_container_width=True
    )
    # Text Input
    chat_input = st.chat_input("Type message here...")

# --- 🧠 LOGIC ---
user_prompt = None
# Check for button click
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
    CONTEXT: You are a chat widget. Keep answers SHORT (1-2 sentences).
    FACTS: 
    - HQ: Wangara, WA.
    - Capacity: Up to 24 Tonnes.
    - Service: 24/7 Hot Shots.
    - Safety: FMP/JMP compliant.
    """
    
    with st.spinner("Paul is typing..."):
        bot_reply = get_gemini_response(user_prompt, sys_instruct)

    with st.chat_message("assistant"):
        st.markdown(bot_reply)
        audio_bytes = text_to_speech(bot_reply)
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

# --- 📍 CONTACT FOOTER (Always Visible at Bottom) ---
st.markdown("""
<div class="contact-footer">
    <div class="contact-item">📍 <b>Wangara HQ:</b> 2/11 Uppill Pl, Wangara WA 6065</div>
    <div class="contact-item">📧 paul@harmontransportation.com.au</div>
    <div class="contact-item">📱 0456 198 939</div>
</div>
""", unsafe_allow_html=True)
