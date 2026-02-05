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

# --- 🎨 UI: CLEAN MODERN WIDGET ---
st.set_page_config(page_title="Harmon Dispatch", page_icon="🚛", layout="centered")

# Custom CSS to force the "Clean White Widget" look
st.markdown("""
<style>
    /* 1. BACKGROUND: Clean White/Grey */
    .stApp {
        background-color: #F8F9FA;
        color: #202124;
    }
    
    /* 2. HIDE SIDEBAR (We want a focused widget) */
    section[data-testid="stSidebar"] {display: none;}

    /* 3. HEADER STYLE */
    .header-container {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        text-align: center;
        border-bottom: 3px solid #0056b3; /* Harmon Blue Accent */
    }
    .status-dot {
        height: 10px; width: 10px; 
        background-color: #28a745; 
        border-radius: 50%; 
        display: inline-block;
        margin-right: 5px;
    }

    /* 4. CHAT BUBBLES (iMessage Style) */
    .stChatMessage {
        background-color: white;
        border: none;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border-radius: 20px;
    }
    .stChatMessage[data-testid="user-message"] {
        background-color: #E8F0FE; /* Light Blue */
    }
    
    /* 5. SUGGESTION BUTTONS (Pills) */
    div.stButton > button {
        background-color: white;
        color: #444;
        border: 1px solid #ddd;
        border-radius: 20px;
        padding: 10px 20px;
        font-size: 14px;
        width: 100%;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        border-color: #0056b3;
        color: #0056b3;
        background-color: #f0f7ff;
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

# --- 🚛 HEADER (THE "BOSS IS ONLINE" CARD) ---
st.markdown("""
<div class="header-container">
    <h2 style="margin:0; color:#202124;">🚛 Harmon Transport</h2>
    <div style="color:#666; font-size:14px; margin-top:5px;">
        <span class="status-dot"></span>Boss is Online | 24/7 Operations
    </div>
</div>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 👋 WELCOME SCREEN (Only if chat is empty) ---
if not st.session_state.messages:
    st.markdown("<div style='text-align: center; margin-top: 40px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/2040/2040520.png", width=60) # Chat Icon
    st.markdown("### Connect with Harmon Dispatch")
    st.caption("Tell me where it's going and what it weighs. I'll give you my best price.")
    st.markdown("</div>", unsafe_allow_html=True)

    # Suggestion Pills
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📦 Deliver a 400kg pallet?"):
            st.session_state.messages.append({"role": "user", "content": "Can you deliver a 400kg pallet?"})
            # Trigger reload to process message immediately would require rerun, 
            # but for simplicity we let the user hit enter or handle logic below.
            # Actually, let's auto-process in next loop if we could, but Streamlit is simple.
            # We will just prepopulate input or treat as sent.
            pass 
    with col2:
        if st.button("⚡ Urgent pickup price?"):
            st.session_state.messages.append({"role": "user", "content": "What's the price for an urgent pickup?"})
            pass

# --- 📜 CHAT HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- ⌨️ & 🎙️ INPUT AREA ---
# Create a container for the input controls
input_container = st.container()

with input_container:
    # 1. Voice Button (Styled Minimal)
    voice_input = speech_to_text(
        language='en', start_prompt="🎙️", stop_prompt="⏹️", just_once=False, key="voice_btn"
    )

    # 2. Text Input
    chat_input = st.chat_input("Type your load details...")

# --- 🧠 LOGIC ENGINE ---
user_prompt = None
# Check if a button was clicked (added to history above) or voice/text input
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user" and len(st.session_state.messages) % 2 != 0:
    # This catches the button clicks from the welcome screen
    user_prompt = st.session_state.messages[-1]["content"]
    # Remove it momentarily so we don't double add, or just let the logic below handle "new" response
    # Actually, simpler logic:
    
if voice_input:
    user_prompt = voice_input
elif chat_input:
    user_prompt = chat_input

# Logic to process the prompt
if user_prompt:
    # If it wasn't already in history (button click adds it, inputs don't yet), add it
    if not st.session_state.messages or st.session_state.messages[-1]["content"] != user_prompt:
        st.chat_message("user").markdown(user_prompt)
        st.session_state.messages.append({"role": "user", "content": user_prompt})

    # Paul's Brain
    sys_instruct = """
    ROLE: You are Paul Harmon, Owner of Harmon Transportation.
    TONE: Friendly, Professional, 'Can-Do'. 
    CONTEXT: You are in a chat widget on a website. Keep answers short and punchy.
    FACTS: Wangara HQ, 24 Tonne Capacity, 24/7 Service.
    """
    
    with st.spinner("..."):
        bot_reply = get_gemini_response(user_prompt, sys_instruct)

    with st.chat_message("assistant"):
        st.markdown(bot_reply)
        audio_bytes = text_to_speech(bot_reply)
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
