import streamlit as st
import replicate
import os
import requests
from PIL import Image, ImageOps
from io import BytesIO

# 1. Page Configuration
st.set_page_config(page_title="Pro Passport Photo Maker", page_icon="👤")

st.title("📸 AI Passport Photo Maker")
st.caption("HD Quality • Auto Background Removal • 630x810 Pixels")
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
    
    # --- STEP 1: Background Removal ---
    # We use the latest stable pointer for lucataco/remove-bg
    st.write("🔄 Step 1: Removing background...")
    bg_remove_output = replicate.run(
        "lucataco/remove-bg",
        input={"image": img_file}
    )
    
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

    # --- STEP 4: HD Enhancement (CodeFormer) ---
    st.write("✨ Step 2: Enhancing to HD Quality...")
    hd_output = replicate.run(
        "sczhou/codeformer",
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
            st.error("Please add your Replicate API Token!")
        else:
            status_placeholder = st.empty()
            with st.spinner("Processing..."):
                try:
                    selected_color = color_map[bg_choice]
                    result = process_image(uploaded_file, selected_color)
                    
                    st.success("Professional Photo Ready!")
                    st.image(result, caption="630x810 HD Passport Photo")
                    
                    # Download
                    img_io = BytesIO()
                    result.save(img_io, 'JPEG', quality=95)
                    st.download_button("Download Image", img_io.getvalue(), "passport_pro.jpg", "image/jpeg")
                except Exception as e:
                    st.error(f"Error: {e}")
