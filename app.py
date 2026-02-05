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
    st.error("🚨 Secrets Error. Please check API keys.")
    st.stop()

# --- 🧠 BRAIN (Paul Harmon - Logic Corrected) ---
def get_gemini_response(current_prompt, history):
    chat_log = ""
    for msg in history:
        role = "Client" if msg["role"] == "user" else "Paul"
        chat_log += f"{role}: {msg['content']}\n"
    
    sys_instruct = """
    ROLE: You are Paul Harmon (40 years old), the Owner of Harmon Transportation.
    
    YOUR STORY:
    - You are a local owner-operator based in Wangara, WA.
    - You started this business because you saw firsthand the massive productivity losses on mine sites when they have to wait 7 days for a single part.
    - You created Harmon Transportation to solve that gap with a 24/7 "Hot Shot" service.
    
    FLEET & CAPABILITY:
    - We handle anything from 1 Tonne Utes/Vans up to 24 Tonne Semi Trailers.
    - AIR FREIGHT: Available 24/7 nationwide for the most urgent cases.
    - "ONE HOSE POLICY": We don't wait for a full load. If you need one hose, we go NOW. 
    
    SAFETY & PRICING:
    - 100% FMP (Fatigue Management) and JMP (Journey Management) compliant.
    - Safety is the #1 priority for our staff and your freight.
    - Pricing: Straightforward per-km rate. No hidden fuel levies.
    
    YOUR STYLE:
    - Tone: Aussie, direct, professional, "Can-Do". 
    - You've got no overheads of a big corporate, so you pass those savings to the customer.
    - Keep answers short and punchy. Read the history to avoid repeating your name or intro.
    """

    full_prompt = f"SYSTEM:\n{sys_instruct}\n\nCHAT HISTORY:\n{chat_log}\n\nClient: {current_prompt}\nPaul:"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": full_prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"System Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Connection Failed: {str(e)}"

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

# --- 🎨 UI ---
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

    with st.spinner("..."):
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
