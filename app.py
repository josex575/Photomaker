import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import io

# Set up page configuration
st.set_page_config(page_title="HD Passport Photo Generator", layout="centered")
st.title("📸 HD Passport Photo Enhancer")
st.write("Upload a portrait to transform it into an enhanced HD passport photo.")

# Securely fetch the API key from Streamlit Secrets
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.error("Please configure your GEMINI_API_KEY in the Streamlit Secrets.")
    st.stop()

# Initialize the GenAI Client
client = genai.Client(api_key=api_key)

# File uploader widget
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    original_image = Image.open(uploaded_file)
    st.image(original_image, caption="Original Uploaded Image", width='stretch')
    
    if st.button("Enhance & Format Image"):
        with st.spinner("AI is enhancing your portrait... (This may take a moment)"):
            try:
                # Convert uploaded file to bytes for the API
                uploaded_file.seek(0)
                image_bytes = uploaded_file.read()
                
                # 1. Generate content with image modality using the correct image generation model
                response = client.models.generate_content(
                    model='gemini-2.5-flash-image',
                    contents=[
                        types.Part.from_bytes(
                            data=image_bytes,
                            mime_type="image/jpeg"
                        ),
                        "Analyze the features of the person in this photo. Re-create and generate an enhanced, professional high-definition passport portrait matching this person exactly. Use clean, crisp textures, soft professional studio lighting, and fine skin details. The person must have a natural, neutral expression, facing directly forward. Set the background to a perfectly solid, plain, light-colored off-white studio background with no patterns or shadows."
                    ],
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                    )
                )
                
                # Extract the inline image data from the response parts
                image_parts = [part for part in response.candidates[0].content.parts if part.inline_data]
                
                if not image_parts:
                    st.error("The model did not return a generated image. Please try adjusting your prompt or checking your API permissions.")
                    st.stop()
                    
                generated_image = Image.open(io.BytesIO(image_parts[0].inline_data.data))
                
                # 2. Precise Crop & Resize to exactly 630 x 810 pixels
                target_width = 630
                target_height = 810
                
                orig_width, orig_height = generated_image.size
                target_ratio = target_width / target_height
                orig_ratio = orig_width / orig_height
                
                if orig_ratio > target_ratio:
                    new_width = int(orig_height * target_ratio)
                    left = (orig_width - new_width) // 2
                    cropped_image = generated_image.crop((left, 0, left + new_width, orig_height))
                else:
                    new_height = int(orig_width / target_ratio)
                    top = (orig_height - new_height) // 2
                    cropped_image = generated_image.crop((0, top, orig_width, top + new_height))
                
                final_image = cropped_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                # 3. Optimize compression to keep file size strictly under 100 KB
                img_buffer = io.BytesIO()
                quality = 90
                file_size_kb = 100.0
                
                while quality > 10:
                    img_buffer.seek(0)
                    img_buffer.truncate(0)
                    final_image.save(img_buffer, format="JPEG", quality=quality, optimize=True)
                    file_size_kb = img_buffer.tell() / 1024
                    
                    if file_size_kb < 100:
                        break
                    quality -= 5
                
                st.success("Image beautifully enhanced!")
                
                # Display final result
                st.image(final_image, caption=f"Enhanced HD Image (Size: {file_size_kb:.1f} KB | 630x810)", width='stretch')
                
                # Download button
                st.download_button(
                    label="Download Enhanced Photo",
                    data=img_buffer.getvalue(),
                    file_name="passport_photo_hd.jpg",
                    mime="image/jpeg"
                )
                
            except Exception as e:
                st.error(f"An error occurred during processing: {e}")
