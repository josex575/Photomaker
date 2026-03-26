import streamlit as st
import replicate
import os
import requests
from PIL import Image, ImageOps
from io import BytesIO

# 1. Page Configuration
st.set_page_config(page_title="Passport Photo Maker", page_icon="👤")

st.title("📸 AI Passport Photo Maker")
st.caption("HD Quality • Professional Crop • 630x810 Pixels")
st.divider()

# 2. Token Logic: Check Secrets first, then Sidebar
if "REPLICATE_API_TOKEN" in st.secrets:
    replicate_api_token = st.secrets["REPLICATE_API_TOKEN"]
else:
    replicate_api_token = st.sidebar.text_input("Enter Replicate API Token", type="password")

# Set the environment variable for the replicate library
if replicate_api_token:
    os.environ["REPLICATE_API_TOKEN"] = replicate_api_token

def process_image(img_file):
    # Target size: 630x810
    TARGET_WIDTH = 630
    TARGET_HEIGHT = 810
    
    img = Image.open(img_file)
    
    # Pre-crop to aspect ratio to ensure face is centered and not stretched
    img = ImageOps.fit(img, (TARGET_WIDTH, TARGET_HEIGHT), centering=(0.5, 0.5))

    buf = BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    # Calling CodeFormer for HD restoration
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
    
    # Final resize to exact 630x810
    return final_img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)

# 3. Main UI
uploaded_file = st.file_uploader("Upload your photo", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Preview
    st.image(uploaded_file, caption="Uploaded Photo", width=250)
    
    if st.button("Generate HD Passport Photo"):
        if not replicate_api_token:
            st.error("Missing API Token! Please add it to Secrets or the sidebar.")
        else:
            with st.spinner("Enhancing to HD..."):
                try:
                    result = process_image(uploaded_file)
                    st.success("Done!")
                    st.image(result, caption="Final HD Passport Photo (630x810)")
                    
                    # Prepare Download
                    img_io = BytesIO()
                    result.save(img_io, 'JPEG', quality=95)
                    st.download_button(
                        label="Download HD Photo",
                        data=img_io.getvalue(),
                        file_name="passport_hd.jpg",
                        mime="image/jpeg"
                    )
                except Exception as e:
                    st.error(f"Error: {e}")
