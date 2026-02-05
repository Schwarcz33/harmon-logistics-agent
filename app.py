import streamlit as st
import os
from google import genai
from google.genai import types
from elevenlabs.client import ElevenLabs

# --- 🔐 SECURITY ---
os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]

# --- 🧠 SELF-HEALING BRAIN CONFIG ---
MODELS_TO_TRY = ["gemini-2.5-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash"]
VOICE_ID = "0NgMq4gSzOuPcjasSGQk" # Paul Harmon

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
voice_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# --- 🎨 UI CONFIGURATION (THE VISUAL UPGRADE) ---
st.set_page_config(page_title="Harmon Logistics", page_icon="🚛", layout="wide")

# Custom CSS to force Dark Mode, rounded corners, and "Violet" branding
st.markdown("""
<style>
    /* 1. MAIN BACKGROUND */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* 2. SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }
    
    /* 3. CHAT BUBBLES */
    .stChatMessage {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
    }
    /* User Bubble (Violet) */
    .stChatMessage[data-testid="user-message"] {
        background-color: #2D1B4E; /* Dark Violet */
        border: 1px solid #8A2BE2; /* Bright Violet Border */
    }
    /* AI Bubble (Dark Grey/Gold Accent) */
    .stChatMessage[data-testid="assistant-message"] {
        background-color: #0D1117;
        border-left: 4px solid #FFD700; /* Gold Bar */
    }

    /* 4. BUTTONS */
    .stButton button {
        background-color: #8A2BE2; /* Violet */
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #7B1FA2; /* Darker Violet */
    }
    
    /* 5. HIDE STREAMLIT BRANDING */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def text_to_speech(text):
    try:
        audio_generator = voice_client.text_to_speech.convert(
            text=text,
            voice_id=VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )
        return b"".join(audio_generator)
    except Exception as e:
        return None

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
    return "Connection Error. Please try again."

# --- 🖥️ SIDEBAR ---
with st.sidebar:
    # Use a local image or URL for the logo if you have one
    st.image("https://cdn-icons-png.flaticon.com/512/7626/7626666.png", width=60)
    st.markdown("### **CONTROL TOWER**")
    st.markdown("---")
    st.info("🟢 **System Status:** ONLINE")
    st.markdown("---")
    st.caption("© 2026 Harmon Transportation")

# --- 🚛 MAIN INTERFACE ---
st.title("🚛 Harmon Transport Agent")
st.markdown("**CEO: Paul Harmon** | *24/7 Operations*")
st.markdown("---")

# Initialize Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 🎤 NEW AUDIO INPUT (Cleaner UI) ---
# This puts the mic right next to the chat bar
audio_value = st.audio_input("Record voice message")

if audio_value:
    # 1. User sent audio -> We pretend it's text for now (Since we don't have Whisper set up yet)
    # TRICK: To keep it simple without adding Whisper costs, we ask user to type OR 
    # if you want real transcription, we need one more API key. 
    # FOR NOW: Let's stick to TEXT input or MIC-RECORDER styled better.
    # Actually, let's use the OLD recorder but styled, because the new one requires Whisper.
    st.warning("Voice received! (Transcription disabled to save costs - using text below)")

# --- ⌨️ CHAT INPUT ---
if prompt := st.chat_input("Message Paul Harmon..."):
    # 1. User Message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. System Instruction
    sys_instruct = """
    ROLE: You are Paul Harmon, Owner of Harmon Transportation.
    TONE: Professional, Aussie, Direct, Capable.
    FACTS: 24/7 Service, Up to 24 Tonnes, FMP/JMP Safety, No price quotes without details.
    """
    
    # 3. AI Response
    with st.spinner("Paul is typing..."):
        bot_reply = get_gemini_response(prompt, sys_instruct)

    # 4. Display & Speak
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
        audio_bytes = text_to_speech(bot_reply)
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
