import streamlit as st
import os
from google import genai
from google.genai import types
from elevenlabs.client import ElevenLabs
from streamlit_mic_recorder import speech_to_text

# --- 🔐 SECURITY ---
# Access keys from the Secure Vault
os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]

# --- 🧠 SELF-HEALING BRAIN CONFIG ---
MODELS_TO_TRY = [
    "gemini-2.5-flash", 
    "gemini-2.0-flash-lite", 
    "gemini-1.5-flash"
]
VOICE_ID = "0NgMq4gSzOuPcjasSGQk" # Arnold Violet (Paul's Voice)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
voice_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

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
        st.error(f"ElevenLabs Error: {e}")
        return None

def get_gemini_response(prompt, sys_instruct):
    """Tries models one by one until one works."""
    last_error = None
    for model in MODELS_TO_TRY:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(system_instruction=sys_instruct)
            )
            return response.text, model
        except Exception as e:
            last_error = e
            continue
    return None, str(last_error)

# --- 🖥️ DASHBOARD UI ---
st.set_page_config(page_title="Harmon Logistics", page_icon="🚛", layout="wide")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/7626/7626666.png", width=50)
    st.title("Control Tower")
    st.markdown("---")
    st.write("### 🎙️ Talk to Paul")
    voice_input = speech_to_text(
        language='en', start_prompt="🔴 CLICK TO SPEAK", stop_prompt="🟥 STOP RECORDING", just_once=False, use_container_width=True
    )

st.title("🚛 Harmon Transport Agent")
st.caption("CEO: Paul Harmon | Status: 24/7 Operations 🟢")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 🤖 LOGIC ---
user_prompt = None
if voice_input:
    user_prompt = voice_input
elif chat_input := st.chat_input("Type your message here..."):
    user_prompt = chat_input

if user_prompt:
    st.chat_message("user").markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # --- 🧠 THE NEW KNOWLEDGE BASE ---
    sys_instruct = """
    ROLE: You are Paul Harmon, the Owner and CEO of Harmon Transportation.
    
    YOUR BACKGROUND:
    - You have 45+ years of experience in the WA mining industry.
    - You started this company because you saw mines losing 7 days of production waiting for parts.
    - You are professional, safety-obsessed, but speak like a genuine Aussie business owner.

    YOUR BUSINESS (THE FACTS):
    1. CAPACITY: We handle everything from a single hose up to 24 Tonnes.
       - Fleet: Utes, Vans, Trucks (up to 24T), and Air Freight options.
    2. SPEED: We are a "Hot Shot" service. We do NOT wait for a full load. We pick up and go immediately.
    3. AVAILABILITY: 24/7, 365 days a year. If a warehouse is closed, we wait at the gate for it to open.
    4. SERVICE AREA: All of WA (Remote areas included). We do NOT charge extra for remote locations.
    5. PRICING: 
       - Simple "Per-Kilometre" rate. No hidden surprises.
       - Extra charges: Only if waiting more than 1 hour at pickup (Standing Fee).
       - RULE: Do not calculate the price yourself. Ask them for the details so you can quote it properly.
    6. SAFETY (#1 Priority):
       - We strictly follow Fatigue Management Plans (FMP) and Journey Management Plans (JMP).
       - Drivers are specialized and trained. Vehicles are impeccably maintained.
    7. ENVIRONMENT: We are striving to be carbon-neutral for future generations.

    HOW TO HANDLE QUESTIONS:
    - "Can you take a heavy load?": "Absolutely mate. We do up to 24 tonnes. What have you got?"
    - "Do you do weekends?": "Mines don't stop, so neither do we. We're on the road 24/7/365."
    - "Why choose you?": "Because we don't wait around to fill a truck. We pick up your part and drive it straight there. No downtime."
    
    GOAL: Impress them with your reliability and ask for the job details.
    """
    
    with st.spinner("Connecting to HQ..."):
        bot_reply, debug_info = get_gemini_response(user_prompt, sys_instruct)

    with st.chat_message("assistant"):
        if bot_reply:
            st.markdown(bot_reply)
            
            if "Error" not in bot_reply:
                st.toast("Paul is speaking...")
                audio_bytes = text_to_speech(bot_reply)
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3", autoplay=True)
            
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        else:
            st.error(f"❌ System Crash. Detail: {debug_info}")
