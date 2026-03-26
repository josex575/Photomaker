import streamlit as st
import replicate
import os
import requests
from PIL import Image, ImageOps
from io import BytesIO

# 1. Page Configuration
st.set_page_config(page_title="Pro Passport Photo Maker", page_icon="👤")

st.title("📸 AI Passport Photo Maker")
st.caption("HD Quality • 2026 Updated Background Removal • 630x810 Pixels")
st.divider()

# 2. Token Logic
if "REPLICATE_API_TOKEN" in st.secrets:
    replicate_api_token = st.secrets["REPLICATE_API_TOKEN"]
else:
    replicate_api_token = st.sidebar.text_input("Enter Replicate API Token", type="password")

if replicate_api_token:
    os.environ["REPLICATE_API_TOKEN"] = replicate_api_token

def process_image(img_file, bg_color):
    TARGET_WIDTH = 630
    TARGET_HEIGHT = 810
    
    # --- STEP 1: Background Removal (Using 851-labs version) ---
    st.info("🔄 Step 1: Removing background...")
    # This version is the stable 2026 standard
    bg_remove_output = replicate.run(
        "851-labs/background-remover:a029dff38972b5fda4ec5d75d7d1cd25aeff621d2cf4946a41055d7db66b80bc",
        input={"image": img_file}
    )
    
    # Download the transparent image
    res = requests.get(bg_remove_output)
    foreground = Image.open(BytesIO(res.content)).convert("RGBA")
    
    # --- STEP 2: Add Solid Background Color ---
    final_bg = Image.new("RGBA", foreground.size, bg_color)
    combined = Image.alpha_composite(final_bg, foreground).convert("RGB")
    
    # --- STEP 3: Smart Crop to 630x810 ---
    combined = ImageOps.fit(combined, (TARGET_WIDTH, TARGET_HEIGHT), centering=(0.5, 0.5))
    
    # Prepare for HD Enhancement
    buf = BytesIO()
    combined.save(buf, format="JPEG")
    buf.seek(0)

    # --- STEP 4: HD Enhancement (Using CodeFormer specific hash) ---
    st.info("✨ Step 2: Enhancing to HD Quality...")
    hd_output = replicate.run(
        "sczhou/codeformer:7de2ea26c616d5bf2245ad0d5e24f0ff9a6204578a5c876db53142edd9d2cd56",
        input={
            "image": buf,
            "upscale": 2,
            "face_upsample": True,
            "background_enhance": True,
            "codeformer_fidelity": 0.7
        }
    )

    response = requests.get(hd_output)
    final_hd = Image.open(BytesIO(response.content))
    
    return final_hd.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)

# 3. Main UI
uploaded_file = st.file_uploader("Upload your photo", type=["jpg", "png", "jpeg"])

bg_choice = st.radio("Select Background Color:", ["White", "Light Blue"], horizontal=True)
color_map = {
    "White": (255, 255, 255, 255),
    "Light Blue": (173, 216, 230, 255)
}

if uploaded_file:
    st.image(uploaded_file, caption="Original Photo", width=250)
    
    if st.button("Generate Professional Passport Photo"):
        if not replicate_api_token:
            st.error("Please add your Replicate API Token in the sidebar or Secrets!")
        else:
            try:
                result = process_image(uploaded_file, color_map[bg_choice])
                
                st.success("Professional Photo Ready!")
                st.image(result, caption="630x810 HD Passport Photo")
                
                # Download Button
                img_io = BytesIO()
                result.save(img_io, 'JPEG', quality=95)
                st.download_button("Download Image", img_io.getvalue(), "passport_pro.jpg", "image/jpeg")
            except Exception as e:
                st.error(f"Something went wrong: {e}")

st.divider()
st.caption("Note: Processing usually takes 15-20 seconds due to high-resolution AI rendering.")
