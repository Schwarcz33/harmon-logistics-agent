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
    st.error("🚨 CRITICAL ERROR: API Keys are missing in Secrets!")
    st.stop()

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
        border-right: 2px solid #FFD700;
    }

    /* 3. BUTTONS (Safety Yellow) */
    div.stButton > button {
        background-color: #FFD700;
        color: #000000;
        border: 2px solid #FF0000;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 900;
        text-transform: uppercase;
        box-shadow: 0 4px 0 #b30000;
    }
    div.stButton > button:hover {
        background-color: #FFEA00;
        transform: translateY(2px);
        box-shadow: 0 2px 0 #b30000;
    }

    /* 4. CHAT BUBBLES */
    .stChatMessage[data-testid="user-message"] {
        background-color: #3d0000;
        border-left: 5px solid #FF0000;
        color: #ffffff;
    }
    .stChatMessage[data-testid="assistant-message"] {
        background-color: #1a1a1a;
        border-left: 5px solid #FFD700;
        color: #ffffff;
    }

    /* 5. TITLES */
    h1, h2, h3 {
        color: #FFD700 !important;
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
    st.image("https://cdn-icons-png.flaticon.com/512/7626/7626666.png", width=80)
    st.markdown("### **DISPATCH CENTRE**")
    st.markdown("**Wangara HQ**")
    st.caption("2/11 Uppill Pl, Wangara WA 6065")
    st.markdown("---")
    
    st.markdown("### 📞 **CONTACT**")
    st.markdown("**Paul Harmon**")
    st.markdown("📧 `paul@harmontransportation.com.au`")
    st.markdown("📱 `0456 198 939`")
    st.markdown("---")
    st.warning("⚠️ **SAFETY FIRST**\n\nEnsure FMP/JMP compliance before booking.")

# --- 🚛 MAIN INTERFACE ---
st.title("🚛 HARMON TRANSPORT")
st.markdown("**CEO: Paul Harmon** | *24/7 HOT SHOT SERVICE*")
st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 🤖 LOGIC ---
user_prompt = None
if voice_input:
    user_prompt = voice_input
elif chat_input := st.chat_input("Enter log details..."):
    user_prompt = chat_input

if user_prompt:
    st.chat_message("user").markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    sys_instruct = """
    ROLE: You are Paul Harmon, Owner of Harmon Transportation.
    
    YOUR STYLE: 
    - You are a mining logistics veteran. Direct, reliable, 'Can-Do'.
    - You use terms like: "Hot Shot", "copy that", "no dramas", "load out".
    
    FACTS: 
    - HQ: Wangara, WA.
    - 24/7 Service, Up to 24 Tonnes.
    - Safety is #1 (FMP/JMP).
    - Pricing: Per-km rate.
    """
    
    with st.spinner("Radioing Paul..."):
        bot_reply = get_gemini_response(user_prompt, sys_instruct)

    with st.chat_message("assistant"):
        st.markdown(bot_reply)
        audio_bytes = text_to_speech(bot_reply)
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
