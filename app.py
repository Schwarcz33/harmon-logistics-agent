import streamlit as st
import os
from google import genai
from google.genai import types
from elevenlabs.client import ElevenLabs
from streamlit_mic_recorder import speech_to_text

# --- 🔐 SECURITY ---
os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]

# --- 🧠 BRAIN CONFIG ---
MODELS_TO_TRY = ["gemini-2.5-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash"]
VOICE_ID = "0NgMq4gSzOuPcjasSGQk" # Paul Harmon

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
voice_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# --- 🎨 UI OVERHAUL (YELLOW/RED/BLACK) ---
st.set_page_config(page_title="Harmon Logistics", page_icon="🚛", layout="wide")

st.markdown("""
<style>
    /* 1. BACKGROUND (Asphalt Black) */
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }

    /* 2. SIDEBAR (Dark Grey) */
    section[data-testid="stSidebar"] {
        background-color: #111111;
        border-right: 2px solid #FFD700; /* Yellow Border */
    }

    /* 3. BUTTONS (Safety Yellow) */
    div.stButton > button {
        background-color: #FFD700; /* Harmon Yellow */
        color: #000000; /* Black Text */
        border: 2px solid #FF0000; /* Red Border */
        padding: 12px 24px;
        border-radius: 8px; /* Industrial Square edges */
        font-weight: 900;
        text-transform: uppercase;
        box-shadow: 0 4px 0 #b30000; /* 3D Red Effect */
    }
    div.stButton > button:hover {
        background-color: #FFEA00;
        transform: translateY(2px);
        box-shadow: 0 2px 0 #b30000;
    }

    /* 4. CHAT BUBBLES */
    /* User Bubble (Red) */
    .stChatMessage[data-testid="user-message"] {
        background-color: #3d0000; /* Dark Red */
        border-left: 5px solid #FF0000; /* Bright Red Bar */
        color: #ffffff;
    }
    /* AI Bubble (Black/Yellow) */
    .stChatMessage[data-testid="assistant-message"] {
        background-color: #1a1a1a; /* Dark Grey */
        border-left: 5px solid #FFD700; /* Yellow Bar */
        color: #ffffff;
    }

    /* 5. TITLES & HEADERS */
    h1, h2, h3 {
        color: #FFD700 !important; /* Yellow Text */
        font-family: 'Arial Black', sans-serif;
    }
    
    /* 6. HIDE JUNK */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- FUNCTIONS ---
def text_to_speech(text):
    try:
        audio_generator = voice_client.text_to_speech.convert(
            text=text,
            voice_id=VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )
        return b"".join(audio_generator)
    except:
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
    return "Connection Error. Radio silence."

# --- 🖥️ SIDEBAR ---
with st.sidebar:
    # Use the Official Harmon Logo URL if you have it, otherwise a Truck Icon
    st.image("https://cdn-icons-png.flaticon.com/512/7626/7626666.png", width=80)
    st.markdown("### **DISPATCH CENTRE**")
    st.caption("📍 Wangara HQ | 🟢 Online")  # <--- FIXED HERE
    st.markdown("---")
    
    st.markdown("### 🎙️ **RADIO CHECK**")
    # THE MIC
    voice_input = speech_to_text(
        language='en', 
        start_prompt="🔴 TRANSMIT", 
        stop_prompt="⏹️ OVER", 
        just_once=False,
        use_container_width=True
    )
    st.markdown("---")
    st.warning("⚠️ **SAFETY FIRST**\n\nEnsure FMP/JMP compliance before booking.")

# --- 🚛 MAIN INTERFACE ---
st.title("🚛 HARMON TRANSPORT")
st.markdown("**CEO: Paul Harmon** | *24/7 HOT SHOT SERVICE*")
st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display History
for message in st.session_state.messages:
    with st.chat_message
