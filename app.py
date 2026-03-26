import streamlit as st
import replicate
import os
import requests
from PIL import Image, ImageOps
from io import BytesIO

# 1. Page Configuration
st.set_page_config(page_title="Professional Passport Photo Maker", page_icon="👤")

st.markdown("""
    <style>
    .main-title { font-size: 42px; font-weight: bold; color: #1E3A8A; text-align: center; }
    .subtitle { font-size: 18px; text-align: center; color: #6B7280; margin-bottom: 30px; }
    </style>
    <div class="main-title">AI Passport Photo Maker</div>
    <div class="subtitle">Convert any portrait into a high-definition, 630x810 professional passport photo.</div>
    """, unsafe_content_html=True)

# 2. API Token Setup
# Replace with your actual token or set as a Streamlit Secret
REPLICATE_API_TOKEN = st.sidebar.text_input("Enter Replicate API Token", type="password")
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

def process_image(img_file):
    # Target dimensions
    TARGET_WIDTH = 630
    TARGET_HEIGHT = 810
    
    # Step A: Initial Crop to Aspect Ratio (prevents stretching)
    img = Image.open(img_file)
    target_ratio = TARGET_WIDTH / TARGET_HEIGHT
    img = ImageOps.fit(img, (int(img.height * target_ratio), img.height), centering=(0.5, 0.5))

    # Step B: AI Enhancement via Replicate (CodeFormer)
    # Using BytesIO to send the cropped image to the API
    buf = BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

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

    # Step C: Final Resize to exact pixels
    response = requests.get(output)
    final_img = Image.open(BytesIO(response.content))
    final_img = final_img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    
    return final_img

# 3. UI Logic
uploaded_file = st.file_uploader("Upload your portrait", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="Original Image", width=300)
    
    if st.button("Generate HD Passport Photo"):
        if not REPLICATE_API_TOKEN:
            st.error("Please enter your Replicate API Token in the sidebar.")
        else:
            with st.spinner("Enhancing quality and cropping to 630x810..."):
                try:
                    result_img = process_image(uploaded_file)
                    
                    st.success("Image Generated Successfully!")
                    st.image(result_img, caption="HD Passport Photo (630x810)")
                    
                    # Download Button
                    img_byte_arr = BytesIO()
                    result_img.save(img_byte_arr, format='JPEG', quality=95)
                    
                    st.download_button(
                        label="Download HD Photo",
                        data=img_byte_arr.getvalue(),
                        file_name="passport_photo_hd.jpg",
                        mime="image/jpeg"
                    )
                except Exception as e:
                    st.error(f"Error: {e}")

st.divider()
st.info("Tip: For best results, ensure the face is well-lit and centered in the original photo.")
