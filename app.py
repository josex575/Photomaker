import streamlit as st
import replicate
import os
import requests
from PIL import Image, ImageOps
from io import BytesIO

# 1. Page Configuration
st.set_page_config(page_title="Passport Photo Maker", page_icon="👤")

# Simplified Header to avoid the metrics_util error
st.title("📸 AI Passport Photo Maker")
st.caption("Convert any portrait into a high-definition 630x810 professional photo.")
st.divider()

# 2. API Token Setup
# Use st.secrets for Streamlit Cloud or sidebar for local testing
REPLICATE_API_TOKEN = st.sidebar.text_input("Replicate API Token", type="password")
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

def process_image(img_file):
    TARGET_WIDTH = 630
    TARGET_HEIGHT = 810
    
    img = Image.open(img_file)
    # This maintains the center of the face while fitting the 630x810 ratio
    img = ImageOps.fit(img, (TARGET_WIDTH, TARGET_HEIGHT), centering=(0.5, 0.5))

    buf = BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    # Call the HD restoration model
    output = replicate.run(
        "sczhou/codeformer:7de2ea4a3562fd1d33025cdd37ee571789abc300503e9f661351833e2bb74ad3",
        input={
            "image": buf,
            "upscale": 2,
            "face_upsample": True,
            "background_enhance": True,
            "codeformer_fidelity": 0.7
        }
    )

    response = requests.get(output)
    final_img = Image.open(BytesIO(response.content))
    # Final precision resize
    return final_img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)

# 3. UI
uploaded_file = st.file_uploader("Upload your photo", type=["jpg", "png", "jpeg"])

if uploaded_file:
    if st.button("Generate HD Passport Photo"):
        if not REPLICATE_API_TOKEN:
            st.warning("Please enter your Replicate API Token in the sidebar.")
        else:
            with st.spinner("Processing..."):
                try:
                    result = process_image(uploaded_file)
                    st.image(result, caption="Final HD Result (630x810)")
                    
                    # Download link
                    img_io = BytesIO()
                    result.save(img_io, 'JPEG', quality=95)
                    st.download_button("Download Image", img_io.getvalue(), "passport.jpg", "image/jpeg")
                except Exception as e:
                    st.error(f"Processing error: {e}")
