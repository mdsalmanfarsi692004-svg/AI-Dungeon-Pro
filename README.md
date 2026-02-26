# 🐉 AI Dungeon Pro: Interactive Storyteller

An interactive, AI-powered storytelling text adventure game built with Python and Streamlit. This project uses Generative AI to create a dynamic, multimodal narrative experience complete with text, cinematic images, and voice narration.

## ✨ Key Features
* **Dynamic Storytelling**: Uses Hugging Face's `GPT-2` model for generating creative story responses based on user input.
* **Cinematic Image Generation**: Integrates `Stable Diffusion v1.5` to visually render the current scene based on the genre.
* **Voice Narration**: Implements `gTTS` (Google Text-to-Speech) to read the story aloud.
* **Customizable Vibe**: Choose from multiple genres (Fantasy, Sci-Fi, Horror, Cyberpunk, Mystery).
* **Story Export**: Download the entire adventure log as a text file.

## 🛠️ Tech Stack
* Python, Streamlit, Transformers (Hugging Face), gTTS, Pillow, Requests

## 🚀 How to Run Locally

1. Install the required dependencies:
   `pip install -r requirements.txt`

2. Add your API Token:
   Open `app.py` and replace the placeholder in the `HEADERS` variable with your actual Hugging Face API token.

3. Run the Streamlit app:
   `streamlit run app.py`
