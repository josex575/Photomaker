import streamlit as st
import replicate
import os
from PIL import Image
import requests
from io import BytesIO

# 1. Setup Page Config
st.set_page_config(page_title="AI HD Image Restorer", layout="centered")
st.title("📸 Portrait HD Upscaler")
st.write("Upload a photo to enhance it to HD and resize to 630x810.")

# 2. Securely handle your API Token
# In production, set this as an environment variable
os.environ["REPLICATE_API_TOKEN"] = "YOUR_REPLICATE_API_TOKEN_HERE"

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the original
    input_image = Image.open(uploaded_file)
    st.image(input_image, caption="Original Photo", use_container_width=True)
    
    if st.button("Enhance to HD"):
        with st.spinner("Processing... This takes about 10-15 seconds."):
            try:
                # 3. Call the CodeFormer Model on Replicate
                # This model is excellent for face restoration and upscaling
                output_url = replicate.run(
                    "sczhou/codeformer:7de2ea4a3562fd1d33025cdd37ee571789abc300503e9f661351833e2bb74ad3",
                    input={
                        "image": uploaded_file,
                        "upscale": 2, # Increase resolution
                        "face_upsample": True,
                        "background_enhance": True,
                        "codeformer_fidelity": 0.7 # Balance between AI and original
                    }
                )

                # 4. Download the AI generated image
                response = requests.get(output_url)
                hd_image = Image.open(BytesIO(response.content))

                # 5. Resize to exactly 630 x 810
                # We use LANCZOS for the highest quality downsampling/resizing
                final_image = hd_image.resize((630, 810), Image.Resampling.LANCZOS)

                # 6. Display and Download
                st.success("Done!")
                st.image(final_image, caption="Enhanced & Resized (630x810)", use_container_width=False)
                
                # Prepare download button
                buf = BytesIO()
                final_image.save(buf, format="JPEG", quality=95)
                byte_im = buf.getvalue()
                
                st.download_button(
                    label="Download HD Image",
                    data=byte_im,
                    file_name="restored_image_630x810.jpg",
                    mime="image/jpeg"
                )

            except Exception as e:
                st.error(f"An error occurred: {e}")
