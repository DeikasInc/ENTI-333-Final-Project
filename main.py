import openai
from elevenlabs import ElevenLabs
import streamlit as st
from PIL import Image
import requests
import time
import os

# Set API Keys
openai.api_key = "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"  # Replace with your OpenAI API key
elevenlabs_client = ElevenLabs(api_key="sk_c9bbdeb7ee4502ffe54f997529c49b67c9a69cf998cd8c80") 
# 1. Story Generation System
image_dir = "generated_images"
os.makedirs(image_dir, exist_ok=True)

# 1. Story Generation System
def generate_base_story(theme, age_range, learning_style):
    """Generate the initial story with adaptable elements."""
    prompt = f"""
    Create a children's story based on the theme: {theme}.  

    Tailor the story for the selected age group: {age_range}. 

    Customize the story for the chosen learning style: {learning_style}. 

    Ensure the story includes a clear moral or learning outcome to foster both entertainment and education.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a creative children's story writer."},
            {"role": "user", "content": prompt}
        ]
    )
    return response["choices"][0]["message"]["content"]

# 2. Image Generation with Saving
image_dir = "generated_images"
os.makedirs(image_dir, exist_ok=True)

def generate_images(story):
    """
    Generate and save an image for the story using DALL·E API and binary response format.
    """
    # Extract a meaningful description from the story
    first_scene = story.split('.')[0]
    prompt = f"Generate a bright, colorful illustration for this children's story scene: {first_scene}"

    try:
        # Call the DALL·E API to generate an image
        generation_response = openai.Image.create(
            model="image-alpha-001",  # Explicitly specify the DALL·E model
            prompt=prompt,  # Provide the prompt for the image generation
            n=1,  # Number of images to generate
            size="1024x1024",  # Specify the image size
            response_format="b64_json"  # Request binary response in base64 format
        )

        # Extract the base64 image data
        b64_image_data = generation_response["data"][0]["b64_json"]

        # Decode and save the image locally
        generated_image_name = "generated_image.png"
        generated_image_filepath = os.path.join(image_dir, generated_image_name)

        with open(generated_image_filepath, "wb") as image_file:
            image_file.write(bytearray.fromhex(b64_image_data))

        return generated_image_filepath  # Return the path of the saved image

    except openai.error.OpenAIError as e:
        # Handle errors returned by the OpenAI API
        print(f"OpenAI API error: {e}")
        return None
    except Exception as e:
        # Handle general errors
        print(f"An error occurred: {e}")
        return None
    
# 3. Audio Generation
def generate_audio(text):
    """Generate audio narration using ElevenLabs."""
    audio = elevenlabs_client.generate(
        text=text,
        voice="Rachel",  # Default voice
        model="eleven_monolingual_v1"
    )
    audio_path = "story_audio.mp3"
    with open(audio_path, "wb") as f:
        for chunk in audio:
            f.write(chunk)
    return audio_path

# 4. Main Function to Create Story
def create_adaptive_story(theme, age_range, learning_style):
    """Main function to create a complete adaptive story."""
    base_story = generate_base_story(theme, age_range, learning_style)
    audio = generate_audio(base_story)
    image_path = generate_images(base_story)
    return {
        "text": base_story,
        "audio": audio,
        "image": image_path
    }

# 5. Streamlit Web Interface
def create_web_interface():
    # Custom CSS for a kid-friendly theme
    st.markdown(
        """
        <style>
        body {
            background: linear-gradient(to bottom, #f3c6f1, #c6e3f3);
            font-family: 'Comic Sans MS', cursive, sans-serif;
        }
        h1 {
            text-align: center;
            color: #ff6f61;
        }
        .title {
            color: #ff6f61;
            font-size: 3em;
            text-shadow: 2px 2px #ffa07a;
        }
        .story-box {
            background-color: #ffe4e1;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0px 5px 15px rgba(0,0,0,0.2);
        }
        .button {
            background-color: #f5b7b1;
            border: none;
            padding: 10px 20px;
            border-radius: 10px;
            font-size: 1.2em;
            cursor: pointer;
        }
        .button:hover {
            background-color: #f1948a;
            transform: scale(1.1);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Title with animation
    st.markdown("<h1 class='title'>✨ Magic Story Creator 🐉</h1>", unsafe_allow_html=True)

    # Input section
    theme = st.text_input("What's the theme of your story? 🧙 (e.g., dragons, space, candy land)", "Dragons")
    age_range = st.selectbox("How old are the kids? 🧒", ["3-5", "6-8", "9-11"])
    learning_style = st.selectbox("Learning Style 🎨", ["Visual", "Auditory", "Kinesthetic"])

    if st.button("🌈 Create My Story!"):
        with st.spinner("🌟 Crafting your magical tale..."):
            # Generate story and assets
            story_package = create_adaptive_story(theme, age_range, learning_style)

        # Display results
        st.markdown("<h2 style='color: #ffa07a;'>📖 Your Magical Adventure:</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='story-box'>{story_package['text']}</div>", unsafe_allow_html=True)

        st.markdown("<h3 style='color: #98fb98;'>🎨 Illustration:</h3>", unsafe_allow_html=True)
        if story_package["image"]:
            st.image(story_package["image"], caption="A magical scene from your story", use_column_width=True)
            st.markdown(f"<a href='{story_package['image']}' download='story_image.png'>📥 Download Image</a>", unsafe_allow_html=True)
        else:
            st.error("Image could not be generated. Please try again.")

        st.markdown("<h3 style='color: #ffb6c1;'>🎧 Listen to Your Story:</h3>", unsafe_allow_html=True)
        if story_package["audio"]:
            st.audio(story_package["audio"])

# Entry point
if __name__ == "__main__":
    create_web_interface()