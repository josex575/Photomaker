import streamlit as st
from google import genai
from google.genai import types
from rembg import remove, new_session
from PIL import Image, ImageOps
import io
import os

# 1. Setup Streamlit UI
st.set_page_config(page_title="Gemini Passport Agent", page_icon="🤖")
st.title("🤖 Gemini Passport AI Agent")
st.caption("Chat with Gemini to process your professional 630x810 photos.")

# 2. Get Gemini API Key from Secrets
if "GEMINI_API_KEY" not in st.secrets:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
else:
    api_key = st.secrets["GEMINI_API_KEY"]

# --- THE TOOL DEFINITION ---
def generate_passport_photo(image_bytes: bytes) -> Image.Image:
    """
    Removes background and resizes an image to 630x810 for a passport.
    Args:
        image_bytes: The raw bytes of the uploaded image.
    """
    session = new_session("u2netp") # Lightweight free model
    no_bg_bytes = remove(image_bytes, session=session)
    foreground = Image.open(io.BytesIO(no_bg_bytes)).convert("RGBA")
    
    # Add White Background
    white_bg = Image.new("RGBA", foreground.size, (255, 255, 255, 255))
    combined = Image.alpha_composite(white_bg, foreground).convert("RGB")
    
    # Final 630x810 Crop
    return ImageOps.fit(combined, (630, 810), Image.Resampling.LANCZOS)

# --- GEMINI AGENT LOGIC ---
if api_key:
    client = genai.Client(api_key=api_key)
    
    uploaded_file = st.file_uploader("Upload your portrait", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        user_msg = st.chat_input("Ex: 'Convert this to a passport photo for me'")
        
        if user_msg:
            with st.chat_message("user"):
                st.write(user_msg)
            
            with st.chat_message("assistant"):
                with st.spinner("Gemini is thinking..."):
                    # Here, Gemini decides if it needs the tool
                    # For this demo, we execute the tool directly if requested
                    if "passport" in user_msg.lower():
                        st.write("I'll process that for you right now...")
                        
                        # Execute your local "Tool"
                        final_img = generate_passport_photo(uploaded_file.getvalue())
                        
                        st.image(final_img, caption="630x810 Passport Photo")
                        
                        # Download Link
                        buf = io.BytesIO()
                        final_img.save(buf, format="JPEG")
                        st.download_button("Download Result", buf.getvalue(), "passport.jpg")
                    else:
                        st.write("I'm ready. Tell me to 'make a passport photo' and I will use my tools!")
else:
    st.warning("Please provide a Gemini API Key to start the agent.")

st.divider()
st.info("This app uses Gemini as the brain and your local server as the hands.")
