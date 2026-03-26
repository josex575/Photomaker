import streamlit as st
from rembg import remove, new_session
from PIL import Image, ImageOps, ImageEnhance
import io

# 1. Page Configuration
st.set_page_config(page_title="Free Passport Photo Maker", page_icon="👤")

st.title("📸 Free AI Passport Photo Maker")
st.caption("No Credits Needed • Pro Crop • 630x810 Pixels")
st.divider()

# 2. Optimized Session Loading
# We use a function to load the session only when needed
@st.cache_resource
def get_rembg_session():
    # 'u2netp' is the tiny 4MB model. 
    # Using the tiny model prevents the 60-second timeout!
    return new_session("u2netp")

def process_passport_photo(input_file, bg_color, brightness_val):
    TARGET_WIDTH = 630
    TARGET_HEIGHT = 810
    
    # Load AI Session
    session = get_rembg_session()
    
    # Step 1: Remove Background
    img_bytes = input_file.getvalue()
    result_bytes = remove(img_bytes, session=session)
    foreground = Image.open(io.BytesIO(result_bytes)).convert("RGBA")
    
    # Step 2: Create Solid Background
    canvas = Image.new("RGBA", foreground.size, bg_color)
    combined = Image.alpha_composite(canvas, foreground).convert("RGB")
    
    # Step 3: Smart Professional Crop (630x810)
    final_img = ImageOps.fit(combined, (TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    
    # Step 4: Enhancements
    if brightness_val != 1.0:
        enhancer = ImageEnhance.Brightness(final_img)
        final_img = enhancer.enhance(brightness_val)
    
    sharpener = ImageEnhance.Sharpness(final_img)
    final_img = sharpener.enhance(1.4) 
    
    return final_img

# 3. Main User Interface
uploaded_file = st.file_uploader("Upload a Portrait Photo", type=["jpg", "png", "jpeg"])

if uploaded_file:
    st.sidebar.header("Settings")
    bg_choice = st.sidebar.radio("Background Color", ["White", "Light Blue"])
    brightness = st.sidebar.slider("Brightness", 0.5, 1.5, 1.0, 0.1)
    
    color_map = {
        "White": (255, 255, 255, 255),
        "Light Blue": (173, 216, 230, 255)
    }

    st.image(uploaded_file, caption="Original Upload", width=250)
    
    if st.button("Generate Passport Photo"):
        with st.spinner("Processing... The first run takes a moment."):
            try:
                final_photo = process_passport_photo(
                    uploaded_file, 
                    color_map[bg_choice], 
                    brightness
                )
                
                st.success("✅ Success!")
                st.image(final_photo, caption="Final Passport Photo", width=315)
                
                buf = io.BytesIO()
                final_photo.save(buf, format="JPEG", quality=95)
                
                st.download_button(
                    label="📥 Download JPG",
                    data=buf.getvalue(),
                    file_name="passport_630x810.jpg",
                    mime="image/jpeg"
                )
            except Exception as e:
                st.error(f"Processing Error: {e}")
                st.info("The server timed out while downloading the AI. Please click 'Generate' again; it should work now that the file is partially cached.")

else:
    st.info("Upload a photo to begin.")
