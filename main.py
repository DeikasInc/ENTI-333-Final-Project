import os
import openai
from elevenlabs import generate, set_api_key
import streamlit as st
from PIL import Image
import requests
import json

# Set API Keys (use environment variables for security)
openai.api_key = os.getenv("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")  # Set your OpenAI API key
set_api_key(os.getenv("ELEVENLABS_API_KEY"))  # Set your ElevenLabs API key

# 1. Story Generation System
def generate_base_story(theme, age_range, learning_style):
    """Generate the initial story with adaptable elements."""
    prompt = f"""
    Create a children's story about {theme} for ages {age_range}.
    Include elements suitable for {learning_style} learning style.
    Structure the story with clear adaptation points marked with [ADAPT].
    Include sensory details marked with [SENSORY].
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a creative children's story writer."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

# 2. Story Adaptation System
def adapt_for_learning_style(story, style):
    """Adapt the base story for specific learning styles."""
    adaptation_prompt = f"""
    Adapt this story for {style} learners.  
    If visual: Enhance visual descriptions and add image cues.
    If auditory: Add sound effects and rhythmic elements.
    If kinesthetic: Add interactive moments and movement prompts.

    Original story:
    {story}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an educational content adapter."},
            {"role": "user", "content": adaptation_prompt}
        ]
    )
    return response['choices'][0]['message']['content']

# 3. Visual Element Generation
def generate_illustrations(scene_description):
    """Generate illustrations using OpenAI's DALL·E."""
    prompt = f"Child-friendly illustration of: {scene_description}. Style: colorful and simple."
    response = openai.Image.create(prompt=prompt, n=1, size="512x512")
    return response['data'][0]['url']

# 4. Audio Generation
def generate_audio(text):
    """Generate audio narration using ElevenLabs."""
    audio = generate(
        text=text,
        voice="Bella",  # Example child-friendly voice
        model="eleven_monolingual_v1"
    )
    # Save audio to a file for Streamlit
    audio_path = "story_audio.mp3"
    with open(audio_path, "wb") as f:
        f.write(audio)
    return audio_path

# 5. Interactive Element Generation
def create_interactive_elements(story):
    """Create interactive elements based on story content."""
    elements_prompt = f"""
    Create interactive elements for this story:
    {story}
    Include:
    - Click points
    - Movement prompts
    - Response moments
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an interactive content designer."},
            {"role": "user", "content": elements_prompt}
        ]
    )
    try:
        return json.loads(response['choices'][0]['message']['content'])
    except json.JSONDecodeError:
        return []

# 6. Main Function to Create Story
def create_adaptive_story(theme, age_range, learning_style):
    """Main function to create a complete adaptive story."""
    base_story = generate_base_story(theme, age_range, learning_style)
    adapted_story = adapt_for_learning_style(base_story, learning_style)
    visuals = generate_illustrations(adapted_story[:100])  # First 100 chars for scene description
    audio = generate_audio(adapted_story)
    interactive_elements = create_interactive_elements(adapted_story)
    return {
        "text": adapted_story,
        "visuals": visuals,
        "audio": audio,
        "interactive": interactive_elements
    }

# 7. Streamlit Web Interface
def create_web_interface():
    st.title("AI Storyteller's Companion")

    # Input controls
    theme = st.text_input("Story Theme", "garden adventure")
    age_range = st.selectbox("Age Range", ["3-5", "6-8", "9-11"])
    learning_style = st.selectbox("Learning Style", ["Visual", "Auditory", "Kinesthetic"])

    if st.button("Generate Story"):
        with st.spinner("Creating your story..."):
            story_package = create_adaptive_story(theme, age_range, learning_style)

        st.write("### Your Story")
        st.write(story_package["text"])

        st.write("### Visual Elements")
        if story_package["visuals"]:
            st.image(story_package["visuals"], caption="Illustration")

        st.write("### Audio Narration")
        if story_package["audio"]:
            st.audio(story_package["audio"])

        st.write("### Interactive Elements")
        if story_package["interactive"]:
            for element in story_package["interactive"]:
                st.button(element.get("prompt", "Click Here"))

# Entry Point
if __name__ == "__main__":
    create_web_interface()
