import streamlit as st
from rembg import remove
from PIL import Image, ImageOps, ImageEnhance
import io

# 1. Page Configuration
st.set_page_config(page_title="Free Passport Photo Maker", page_icon="👤")

st.title("📸 Free AI Passport Photo Maker")
st.caption("No Credits Needed • Professional Crop • 630x810 Pixels")
st.divider()

def process_image_free(input_image, bg_color):
    TARGET_WIDTH = 630
    TARGET_HEIGHT = 810
    
    # Step 1: Remove Background (FREE)
    img_bytes = input_image.getvalue()
    result_bytes = remove(img_bytes)
    foreground = Image.open(io.BytesIO(result_bytes)).convert("RGBA")
    
    # Step 2: Create Background and Merge
    # We create a canvas of the same size as the foreground
    final_bg = Image.new("RGBA", foreground.size, bg_color)
    combined = Image.alpha_composite(final_bg, foreground).convert("RGB")
    
    # Step 3: Smart Crop to 630x810
    # ImageOps.fit ensures the face stays centered and the ratio is perfect
    final_img = ImageOps.fit(combined, (TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    
    # Step 4: Digital Sharpening (Emulates "HD" quality)
    enhancer = ImageEnhance.Sharpness(final_img)
    final_img = enhancer.enhance(1.5) # Slight boost to make it look crisp
    
    return final_img

# UI Layout
uploaded_file = st.file_uploader("Upload your photo", type=["jpg", "png", "jpeg"])

col1, col2 = st.columns(2)
with col1:
    bg_choice = st.radio("Background Color:", ["White", "Light Blue"])
with col2:
    brightness = st.slider("Face Brightness", 0.5, 1.5, 1.0)

color_map = {
    "White": (255, 255, 255, 255),
    "Light Blue": (173, 216, 230, 255)
}

if uploaded_file:
    st.image(uploaded_file, caption="Original Photo", width=200)
    
    if st.button("Generate Passport Photo"):
        with st.spinner("Processing locally... (First time takes 1 minute to load AI)"):
            try:
                # Process the image
                result = process_image_free(uploaded_file, color_map[bg_choice])
                
                # Apply brightness adjustment if needed
                if brightness != 1.0:
                    bright_enhancer = ImageEnhance.Brightness(result)
                    result = bright_enhancer.enhance(brightness)
                
                st.success("Done!")
                st.image(result, caption="Final 630x810 Passport Photo")
                
                # Prepare Download
                buf = io.BytesIO()
                result.save(buf, format="JPEG", quality=95)
                st.download_button(
                    label="Download Image",
                    data=buf.getvalue(),
                    file_name="passport_photo.jpg",
                    mime="image/jpeg"
                )
            except Exception as e:
                st.error(f"Error: {e}")

st.divider()
st.info("💡 Note: The very first time you click 'Generate', the app downloads a free AI model (~170MB). After that, it will be much faster.")
