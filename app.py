import streamlit as st
from PIL import Image, ImageEnhance
import io

# Set up page configuration
st.set_page_config(page_title="Free Passport Photo Formatter", layout="centered")
st.title("📸 Passport Photo Formatter & Enhancer")
st.write("Upload a portrait to instantly optimize lighting, crop to **630x810**, and compress to **under 100 KB**.")

# File uploader widget
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    original_image = Image.open(uploaded_file)
    st.image(original_image, caption="Original Uploaded Image", width='stretch')
    
    if st.button("Enhance & Format Image"):
        with st.spinner("Processing studio enhancements..."):
            try:
                # 1. Studio Enhancement Simulation (Brightness, Contrast, Sharpness adjustments)
                # This achieves a clean studio look completely on your free Streamlit server
                enhanced = ImageEnhance.Brightness(original_image).enhance(1.05)
                enhanced = ImageEnhance.Contrast(enhanced).enhance(1.1)
                enhanced = ImageEnhance.Sharpness(enhanced).enhance(1.15)
                
                # 2. Precise Crop & Resize to exactly 630 x 810 pixels
                target_width = 630
                target_height = 810
                
                orig_width, orig_height = enhanced.size
                target_ratio = target_width / target_height
                orig_ratio = orig_width / orig_height
                
                if orig_ratio > target_ratio:
                    new_width = int(orig_height * target_ratio)
                    left = (orig_width - new_width) // 2
                    cropped_image = enhanced.crop((left, 0, left + new_width, orig_height))
                else:
                    new_height = int(orig_width / target_ratio)
                    top = (orig_height - new_height) // 2
                    cropped_image = enhanced.crop((0, top, orig_width, top + new_height))
                
                final_image = cropped_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                # 3. Optimize compression to keep file size strictly under 100 KB
                img_buffer = io.BytesIO()
                quality = 90
                file_size_kb = 100.0
                
                while quality > 10:
                    img_buffer.seek(0)
                    img_buffer.truncate(0)
                    if final_image.mode in ("RGBA", "P"):
                        final_image = final_image.convert("RGB")
                    final_image.save(img_buffer, format="JPEG", quality=quality, optimize=True)
                    file_size_kb = img_buffer.tell() / 1024
                    
                    if file_size_kb < 100:
                        break
                    quality -= 5
                
                st.success("Image successfully formatted!")
                
                # Display final result
                st.image(final_image, caption=f"Formatted Image (Size: {file_size_kb:.1f} KB | 630x810)", width='stretch')
                
                # Download button
                st.download_button(
                    label="Download Formatted Photo",
                    data=img_buffer.getvalue(),
                    file_name="passport_photo_630x810.jpg",
                    mime="image/jpeg"
                )
                
            except Exception as e:
                st.error(f"An error occurred during processing: {e}")
