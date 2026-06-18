import streamlit as st
from PIL import Image
import io

# Set up page configuration
st.set_page_config(page_title="Passport Photo Formatter", layout="centered")
st.title("📸 Passport Photo Formatter & Compressor")
st.write("Upload any photo to instantly crop/resize it to **630x810** and compress it to **under 100 KB**.")

# File uploader widget
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Open and display the original image
    original_image = Image.open(uploaded_file)
    st.image(original_image, caption="Original Uploaded Image", width='stretch')
    
    if st.button("Format & Compress Image"):
        with st.spinner("Processing image geometry..."):
            try:
                # 1. Define target dimensions
                target_width = 630
                target_height = 810
                
                # 2. Smart Crop to maintain aspect ratio without stretching
                orig_width, orig_height = original_image.size
                target_ratio = target_width / target_height
                orig_ratio = orig_width / orig_height
                
                if orig_ratio > target_ratio:
                    # Image is too wide - crop the sides
                    new_width = int(orig_height * target_ratio)
                    left = (orig_width - new_width) // 2
                    cropped_image = original_image.crop((left, 0, left + new_width, orig_height))
                else:
                    # Image is too tall - crop top and bottom
                    new_height = int(orig_width / target_ratio)
                    top = (orig_height - new_height) // 2
                    cropped_image = original_image.crop((0, top, orig_width, top + new_height))
                
                # Resize to exact dimensions
                final_image = cropped_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                # 3. Dynamic compression loop to stay strictly under 100 KB
                img_buffer = io.BytesIO()
                quality = 95
                file_size_kb = 100.0
                
                while quality > 10:
                    img_buffer.seek(0)
                    img_buffer.truncate(0)
                    # Convert to RGB if image is PNG or has transparency
                    if final_image.mode in ("RGBA", "P"):
                        final_image = final_image.convert("RGB")
                        
                    final_image.save(img_buffer, format="JPEG", quality=quality, optimize=True)
                    file_size_kb = img_buffer.tell() / 1024
                    
                    if file_size_kb < 100:
                        break
                    quality -= 5  # Step down quality until it fits the constraint
                
                st.success("Formatting complete!")
                
                # Display final result
                st.image(final_image, caption=f"Final Formatted Image (Size: {file_size_kb:.1f} KB | 630x810)", width='stretch')
                
                # Download button
                st.download_button(
                    label="Download Formatted Photo",
                    data=img_buffer.getvalue(),
                    file_name="passport_photo_630x810.jpg",
                    mime="image/jpeg"
                )
                
            except Exception as e:
                st.error(f"An error occurred during processing: {e}")
