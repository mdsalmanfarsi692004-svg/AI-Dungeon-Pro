import streamlit as st
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from gtts import gTTS
import requests
from PIL import Image
import io
import re

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="AI Dungeon: Pro Edition", page_icon="⚔️", layout="wide")

# --- PROFESSIONAL CSS (FIXED CENTERING) ---
st.markdown("""
<style>
    /* 1. Global Settings */
    body {
        color: #ffffff;
        background-color: #0e1117;
    }
    .stApp {
        text-align: center;
    }

    /* 2. Title & Subtitle */
    .title-text {
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        font-size: 3em;
        background: -webkit-linear-gradient(45deg, #6c5ce7, #a29bfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .subtitle-text {
        text-align: center;
        color: #b2bec3;
        font-size: 1.2em;
        margin-bottom: 30px;
    }

    /* 3. Input Box (Centered Text) */
    .stTextInput > div > div > input {
        text-align: center;
        background-color: #1e1e1e;
        color: white;
        border: 1px solid #444;
        border-radius: 8px;
        padding: 10px;
        font-size: 16px;
    }

    /* 4. BUTTON CENTERING MAGIC (Ye line zaroori hai) */
    /* Isse button ka container hi center ho jayega */
    .stButton {
        display: flex;
        justify-content: center;
    }
    
    .stButton > button {
        background-color: #6c5ce7;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 40px; /* Thoda wide banaya */
        font-size: 16px;
        font-weight: 600;
        transition: background 0.3s;
    }
    .stButton > button:hover {
        background-color: #5a4ad1;
    }

    /* 5. SIDEBAR LABELS CENTERING */
    /* Sirf labels ko pakad ke center kar raha hu */
    [data-testid="stSidebar"] label {
        width: 100%;
        text-align: center !important;
        display: block;
        margin-bottom: 5px;
        font-size: 1rem;
        font-weight: 600;
    }
    
    /* Sidebar Headers Center */
    [data-testid="stSidebar"] h3 {
        text-align: center !important;
    }
    
    /* Settings Checkbox Alignment */
    [data-testid="stCheckbox"] {
        display: flex;
        justify-content: center;
    }

    /* 6. Story Cards */
    .story-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        text-align: center;
    }
    .user-text {
        color: #a29bfe;
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 8px;
    }
    .ai-text {
        color: #dfe6e9;
        font-size: 1.05em;
        line-height: 1.6;
    }

    /* Hide Sidebar Decoration */
    .css-163ttbj {
        background-color: #0e1117;
    }
</style>
""", unsafe_allow_html=True)

# --- API & MODEL ---
API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
HEADERS = {"Authorization": "Bearer YOUR_HUGGINGFACE_TOKEN"}

@st.cache_resource
def load_model():
    model_name = "gpt2"
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPT2LMHeadModel.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    return tokenizer, model

try:
    tokenizer, model = load_model()
except Exception:
    st.error("⚠️ Model loading failed.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🎭 Select Genre")
    genre = st.selectbox("Theme", ["Fantasy", "Sci-Fi", "Horror", "Cyberpunk", "Mystery"])
    
    st.divider()
    st.markdown("### 🎒 Character Profile")
    char_name = st.text_input("Name", "Arthur")
    inventory = st.text_area("Inventory", "Sword, Map, Potion")
    
    st.divider()
    st.markdown("### ⚙️ Settings")
    enable_voice = st.checkbox("Enable Voice", value=True)
    enable_image = st.checkbox("Generate Images", value=True)
    creativity = st.slider("Creativity", 0.1, 1.0, 0.6)
    
    st.divider()
    # Reset Button (CSS handles centering)
    if st.button("🗑️ Reset Story"):
        st.session_state.history = []
        st.rerun()

# --- LOGIC ---
def clean_text(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[<>{}[\]@#_+=\^]', '', text)
    text = re.sub(r'([!?.]){2,}', r'\1', text)
    return text.strip()

def generate_story(prompt):
    inputs = tokenizer(prompt, return_tensors='pt', padding=True)
    output = model.generate(
        inputs.input_ids, 
        max_length=len(inputs.input_ids[0]) + 60, 
        temperature=creativity, 
        repetition_penalty=1.3,
        no_repeat_ngram_size=3,
        do_sample=True, 
        top_p=0.92,
        pad_token_id=tokenizer.eos_token_id
    )
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    return clean_text(generated_text)

def generate_image(prompt):
    try:
        style_map = {
            "Fantasy": "epic fantasy art, magical",
            "Sci-Fi": "futuristic, sci-fi concept art, neon lights",
            "Horror": "dark, horror, eerie atmosphere, mist",
            "Cyberpunk": "cyberpunk city, high tech low life, neon",
            "Mystery": "noir style, mysterious, detective, shadows"
        }
        style = style_map.get(genre, "cinematic art")
        image_prompt = f"{style}, {prompt[:80]}, centered composition, highly detailed"
        response = requests.post(API_URL, headers=HEADERS, json={"inputs": image_prompt})
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
    except:
        pass
    return None

def text_to_speech(text):
    try:
        if len(text) > 5:
            tts = gTTS(text=text, lang='en')
            tts.save("story_audio.mp3")
            return "story_audio.mp3"
    except:
        pass
    return None

# --- MAIN UI ---
st.markdown('<div class="title-text">AI Dungeon Pro</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subtitle-text">Mode: {genre} Adventure | Powered by GenAI</div>', unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []

# Input Area
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    user_action = st.text_input("Action", placeholder="What do you do next?", label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)

# Button Area - Dedicated Row for strict centering
b1, b2, b3 = st.columns([1, 1, 1])
with b2:
    # Button is inside middle column, AND CSS forces it to center
    if st.button("Take Action ➡️"):
        if user_action:
            with st.spinner("Writing the next chapter..."):
                prompt_template = f"{genre} Story.\nHero: {char_name}.\nAction: {user_action}.\nResult:"
                full_text = generate_story(prompt_template)
                
                if "Result:" in full_text:
                    new_story = full_text.split("Result:")[-1].strip()
                else:
                    new_story = full_text.replace(prompt_template, "").strip()

                if not new_story or len(new_story) < 5:
                    new_story = "The darkness shifts, and something unexpected happens."

                img = generate_image(new_story) if enable_image else None
                audio = text_to_speech(new_story) if enable_voice else None

                st.session_state.history.append({
                    "user": user_action,
                    "ai": new_story,
                    "image": img,
                    "audio": audio
                })

# Story Feed
st.divider()

if st.session_state.history:
    full_story_text = ""
    for event in st.session_state.history:
        full_story_text += f"You: {event['user']}\nAI: {event['ai']}\n\n"
    
    d1, d2, d3 = st.columns([1, 1, 1])
    with d2:
        st.download_button(
            label="💾 Download Story",
            data=full_story_text,
            file_name="adventure_log.txt",
            mime="text/plain"
        )

for event in reversed(st.session_state.history):
    with st.container():
        st.markdown(f"""
        <div class="story-card">
            <div class="user-text">👤 {char_name}: {event['user']}</div>
            <div class="ai-text">🔮 {event['ai']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if event['image']:
                st.image(event['image'], use_column_width=True)
            if event['audio']:
                st.audio(event['audio'])