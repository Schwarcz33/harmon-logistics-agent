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

# --- 🎨 UI OVERHAUL (THE VIOLET THEME) ---
st.set_page_config(page_title="Harmon Logistics", page_icon="🚛", layout="wide")

st.markdown("""
<style>
    /* 1. BACKGROUND GRADIENT (Cosmic Theme) */
    .stApp {
        background: linear-gradient(to bottom right, #050505, #1a0b2e);
        color: #E0E0E0;
    }

    /* 2. SIDEBAR STYLE */
    section[data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #2D1B4E;
    }

    /* 3. GLOWING BUTTONS */
    div.stButton > button {
        background: linear-gradient(90deg, #8A2BE2, #4B0082);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 25px;
        font-weight: bold;
        box-shadow: 0 0 10px rgba(138, 43, 226, 0.5);
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 20px rgba(138, 43, 226, 0.8);
    }

    /* 4. CHAT BUBBLES (Modern Look) */
    .stChatMessage {
        border-radius: 20px;
        padding: 15px;
        margin-bottom: 12px;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    /* User Bubble (Violet) */
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, #2D1B4E, #1a0b2e);
        border-left: 5px solid #8A2BE2;
    }
    /* AI Bubble (Dark Grey/Gold) */
    .stChatMessage[data-testid="assistant-message"] {
        background-color: #161B22;
        border-left: 5px solid #FFD700;
    }

    /* 5. INPUT FIELD */
    .stTextInput input {
        background-color: #161B22;
        color: white;
        border: 1px solid #8A2BE2;
        border-radius: 15px;
    }
    
    /* 6. HIDE HEADER/FOOTER */
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
    return "Connection Error."

# --- 🖥️ SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/7626/7626666.png", width=80)
    st.markdown("### **HARMON DISPATCH**")
    st.caption("📍 Landsdale HQ | 🟢 Online")
    st.markdown("---")
    
    st.markdown("### 🎙️ **Push to Talk**")
    # THE RELIABLE MIC (Styled by CSS above)
    voice_input = speech_to_text(
        language='en', 
        start_prompt="🔴 RECORD", 
        stop_prompt="⏹️ SEND", 
        just_once=False,
        use_container_width=True
    )
    st.markdown("---")
    st.info("💡 **Pro Tip:** Ask about heavy haulage or remote deliveries.")

# --- 🚛 MAIN INTERFACE ---
st.title("🚛 Harmon Transport Agent")
st.markdown("**CEO: Paul Harmon**")
st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 🤖 LOGIC ---
user_prompt = None
if voice_input:
    user_prompt = voice_input
elif chat_input := st.chat_input("Type message here..."):
    user_prompt = chat_input

if user_prompt:
    st.chat_message("user").markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    sys_instruct = """
    ROLE: You are Paul Harmon, Owner of Harmon Transportation.
    TONE: Professional, Aussie, Direct, Capable.
    FACTS: 
    - 24/7 Service, Up to 24 Tonnes, FMP/JMP Safety.
    - Pricing: Per-km rate. NO hidden fees.
    - Philosophy: "We don't wait for a full load. We go."
    """
    
    with st.spinner("Connecting..."):
        bot_reply = get_gemini_response(user_prompt, sys_instruct)

    with st.chat_message("assistant"):
        st.markdown(bot_reply)
        audio_bytes = text_to_speech(bot_reply)
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
