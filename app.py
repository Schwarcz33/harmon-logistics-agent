import streamlit as st
import requests
import json
from elevenlabs.client import ElevenLabs
from streamlit_mic_recorder import speech_to_text

# --- 🔐 SECURITY ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]
except:
    st.error("🚨 Secrets Error. Please check API keys in Streamlit Cloud.")
    st.stop()

# --- 🧠 BRAIN (Gemini 3.0 Flash - Paul Harmon Personality) ---
def get_gemini_response(current_prompt, history):
    chat_log = ""
    for msg in history:
        role = "Client" if msg["role"] == "user" else "Paul"
        chat_log += f"{role}: {msg['content']}\n"
    
    # Restored full Harmon Transportation Intelligence
    sys_instruct = """
    ROLE: You are Paul Harmon (40 years old), the Owner of Harmon Transportation.
    
    IDENTITY & STORY:
    - Based in Wangara, WA. You started this because mine sites were losing money waiting 7 days for one part.
    - You are a local owner-operator, not a corporate suit.
    
    CAPABILITIES & FLEET:
    - 1T Utes/Vans, 3T, 5T, 8T Trucks, up to 24T Semi Trailers.
    - 24/7 Hot Shot Perth services for time-critical transport.
    - "ONE HOSE POLICY": You deliver even if it's just one part, ASAP. No waiting for full loads.
    - 24/7 Urgent Air Freight nationwide.
    
    SAFETY & SERVICE:
    - 100% FMP (Fatigue Management) and JMP (Journey Management) compliant.
    - Point-to-point delivery with no detours or stops.
    - Simple per-km pricing. No hidden fuel levies.
    
    STYLE:
    - Aussie, direct, "Can-Do" attitude.
    - SHORT responses (1-2 sentences). 
    - Check the HISTORY below. If you already said hi, don't do it again.
    """

    # TARGETING THE NEW MODELS DIRECTLY
    models = ["gemini-3-flash-preview", "gemini-2.0-flash"]
    
    for model_name in models:
        # v1beta is required for the newest models
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": f"INSTRUCTIONS: {sys_instruct}\n\nHISTORY:\n{chat_log}\n\nClient: {current_prompt}\nPaul:"}]}]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
        except:
            continue
            
    return "Dispatch is lagging. Say again?"

# --- 🔊 VOICE ---
voice_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
VOICE_ID = "0NgMq4gSzOuPcjasSGQk" 

def text_to_speech(text):
    try:
        audio_generator = voice_client.text_to_speech.convert(
            text=text, voice_id=VOICE_ID, model_id="eleven_multilingual_v2", output_format="mp3_44100_128"
        )
        return b"".join(audio_generator)
    except:
        return None

# --- 🎨 UI: THE DARK WIDGET ---
st.set_page_config(page_title="Harmon Dispatch", page_icon="🚛", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    section[data-testid="stSidebar"] {display: none;}
    .header-container {
        background-color: #161B22; padding: 20px; border-radius: 15px;
        border: 1px solid #30363D; text-align: center; margin-bottom: 20px;
    }
    .header-title { color: #FFD700; font-family: sans-serif; font-weight: 800; font-size: 26px; text-transform: uppercase; }
    .contact-footer { margin-top: 30px; padding: 15px; border-top: 1px solid #30363D; text-align: center; font-size: 13px; color: #8b949e; }
    .stChatMessage { background-color: #161B22; border: 1px solid #30363D; border-radius: 15px; }
    .stChatMessage[data-testid="user-message"] { background-color: #1F6FEB; color: white; border: none; }
    div.stButton > button { background-color: #21262D; color: white; border: 1px solid #30363D; width: 100%; border-radius: 10px; }
    div.stButton > button:hover { border-color: #FFD700; color: #FFD700; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-container">
    <div class="header-title">🚛 HARMON TRANSPORT</div>
    <div style="color: #28a745; font-size: 12px; font-weight: bold; margin-top: 5px;">● 24/7 DISPATCH ONLINE</div>
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.messages:
    st.markdown("<div style='text-align: center; margin-bottom: 20px; opacity: 0.8;'>Paul Harmon is listening. How can we move your freight?</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📦 Get a Quote"): st.session_state.messages.append({"role": "user", "content": "I need a quote for a load."})
    with c2:
        if st.button("⚡ Urgent Hot Shot"): st.session_state.messages.append({"role": "user", "content": "I have an urgent hot shot delivery."})

for message in st.session_state.messages:
    with st.chat_message(message["role"]): st.markdown(message["content"])

with st.container():
    voice_input = speech_to_text(language='en', start_prompt="🎙️ PUSH TO TALK", stop_prompt="⏹️ SEND", just_once=False, key="voice_btn", use_container_width=True)
    chat_input = st.chat_input("Type message here...")

user_prompt = None
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user" and len(st.session_state.messages) % 2 != 0:
    user_prompt = st.session_state.messages[-1]["content"]
if voice_input: user_prompt = voice_input
elif chat_input: user_prompt = chat_input

if user_prompt:
    if not st.session_state.messages or st.session_state.messages[-1]["content"] != user_prompt:
        st.chat_message("user").markdown(user_prompt)
        st.session_state.messages.append({"role": "user", "content": user_prompt})

    with st.spinner("Paul is typing..."):
        bot_reply = get_gemini_response(user_prompt, st.session_state.messages)

    with st.chat_message("assistant"):
        st.markdown(bot_reply)
        audio_bytes = text_to_speech(bot_reply)
        if audio_bytes: st.audio(audio_bytes, format="audio/mp3", autoplay=True)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

st.markdown("""
<div class="contact-footer">
    <div>📍 <b>Wangara HQ:</b> 2/11 Uppill Pl, Wangara WA 6065</div>
    <div>📧 paul@harmontransportation.com.au | 📱 0456 198 939</div>
</div>
""", unsafe_allow_html=True)
