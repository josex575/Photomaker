import streamlit as st
from rembg import remove, new_session
from PIL import Image, ImageOps, ImageEnhance
import io

# 1. Page Configuration
st.set_page_config(page_title="Free Passport Photo Maker", page_icon="👤")

# --- CUSTOM CSS FOR BETTER LOOKS ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    </style>
    """, unsafe_content_html=True)

st.title("📸 Free AI Passport Photo Maker")
st.caption("No Credits Needed • Pro Crop • 630x810 Pixels")
st.divider()

# 2. Initialize AI Session (Using the Lightweight 'u2netp' model)
# This prevents timeouts by loading the model into the app state
if 'rembg_session' not in st.session_state:
    try:
        # 'u2netp' is the lightweight version of the background remover
        st.session_state.rembg_session = new_session("u2netp")
    except Exception as e:
        st.error(f"Error initializing AI: {e}")

def process_passport_photo(input_file, bg_color, brightness_val):
    TARGET_WIDTH = 630
    TARGET_HEIGHT = 810
    
    # Load Image
    img = Image.open(input_file)
    
    # Step 1: Remove Background using the pre-loaded session
    img_bytes = input_file.getvalue()
    result_bytes = remove(img_bytes, session=st.session_state.rembg_session)
    foreground = Image.open(io.BytesIO(result_bytes)).convert("RGBA")
    
    # Step 2: Create Solid Background
    # Use the foreground size to match dimensions before compositing
    canvas = Image.new("RGBA", foreground.size, bg_color)
    combined = Image.alpha_composite(canvas, foreground).convert("RGB")
    
    # Step 3: Smart Professional Crop (630x810)
    # LANCZOS provides high-quality downsampling/sharpening
    final_img = ImageOps.fit(combined, (TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    
    # Step 4: Brightness & Sharpness Enhancements
    # Adjust Brightness
    if brightness_val != 1.0:
        enhancer = ImageEnhance.Brightness(final_img)
        final_img = enhancer.enhance(brightness_val)
    
    # Apply a slight sharpening to emulate "HD" quality
    sharpener = ImageEnhance.Sharpness(final_img)
    final_img = sharpener.enhance(1.4) 
    
    return final_img

# 3. Main User Interface
uploaded_file = st.file_uploader("Upload a Portrait Photo", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Sidebar Controls
    st.sidebar.header("Settings")
    bg_choice = st.sidebar.radio("Background Color", ["White", "Light Blue"])
    brightness = st.sidebar.slider("Brightness", 0.5, 1.5, 1.0, 0.1)
    
    color_map = {
        "White": (255, 255, 255, 255),
        "Light Blue": (173, 216, 230, 255)
    }

    # Display Original Preview
    st.image(uploaded_file, caption="Original Upload", width=250)
    
    if st.button("Generate Passport Photo"):
        with st.spinner("Processing... (The first run takes a moment to load AI)"):
            try:
                # Process
                final_photo = process_passport_photo(
                    uploaded_file, 
                    color_map[bg_choice], 
                    brightness
                )
                
                # Show Result
                st.success("✅ Success! Your 630x810 photo is ready.")
                st.image(final_photo, caption="Final Passport Photo", width=315)
                
                # Download
                buf = io.BytesIO()
                final_photo.save(buf, format="JPEG", quality=95)
                byte_im = buf.getvalue()
                
                st.download_button(
                    label="📥 Download High Quality JPG",
                    data=byte_im,
                    file_name="passport_630x810.jpg",
                    mime="image/jpeg"
                )
                
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.info("Try refreshing the page if the AI model is still downloading.")

else:
    st.info("Please upload a photo to begin.")
    st.image("https://via.placeholder.com/630x810.png?text=630x810+Preview", width=200)

st.divider()
st.caption("Built with Python & Open Source AI • No API Keys Required")
