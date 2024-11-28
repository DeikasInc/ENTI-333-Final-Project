import os
import openai
from elevenlabs import ElevenLabs
import streamlit as st
from PIL import Image
import requests
import json

# Set API Keys
openai.api_key = "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"  # Replace with your OpenAI API key
elevenlabs_client = ElevenLabs(api_key="sk_c9bbdeb7ee4502ffe54f997529c49b67c9a69cf998cd8c80")  # Replace with your ElevenLabs API key

# 1. Story Generation System
def generate_base_story(theme, age_range, learning_style):
    """Generate the initial story with adaptable elements."""
    prompt = f"""
    Create a children's story based on the theme: {theme}.  

  

Tailor the story for the selected age group: {age_range}. 

- For ages 3-5: Use simple sentences, no paragraphs, larger text format, and include repetition or rhyming to support comprehension. Keep the story short (100-150 words). 

- For ages 5-7: Introduce short paragraphs, a clear beginning, middle, and end, and use a slightly larger font. Add engaging dialogue or questions to involve the child. 

- For ages 7-9: Add richer vocabulary, more detailed descriptions, and multi-paragraph storytelling with an easy-to-follow plot.  

- For ages 9-11: Include complex sentences, imaginative world-building, and relatable themes that foster critical thinking and creativity. 

  

Customize the story for the chosen learning style: {learning_style}. 

- For visual learners: Incorporate emojis, visual descriptions, and exclamations to stimulate imagination. For example: "🌟 The stars twinkled brightly in the night sky!" Use vivid imagery to enhance engagement. 

- For auditory learners: Focus on rhythm, rhyme, and onomatopoeia. Use sound-related cues like "BAM!" or "whoosh" to make the story engaging. Structure sentences to flow naturally when read aloud. 

- For kinesthetic learners: Include action-oriented descriptions and prompts for interactive engagement, such as "Clap your hands when the hero cheers!" or "Pretend to jump over the log like the character!" 

  

Ensure the story includes a clear moral or learning outcome to foster both entertainment and education. 

  

Output the story in a format optimized for the age group and learning style, including spacing, layout, and interactivity when applicable. 
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a creative children's story writer."},
            {"role": "user", "content": prompt}
        ]
    )
    return response["choices"][0]["message"]["content"]

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

# 3. Image Generation
def generate_images(story):
    """Generate images for the story using DALL·E."""
    first_scene = story.split('.')[0]  # Get the first sentence for better context
    prompt = f"Generate a bright, colorful illustration for this scene: {first_scene}"    
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="512x512"
    )
    image_url = response['data'][0]['url']
    return image_url

# 4. Audio Generation
def generate_audio(text, voice):
    """Generate audio narration using ElevenLabs."""
    audio = elevenlabs_client.generate(
        text=text,
        voice=voice,  # Voice selected by user
        model="eleven_monolingual_v1"
    )

    # Save audio to a file
    audio_path = "story_audio.mp3"
    with open(audio_path, "wb") as f:
        for chunk in audio:  # Iterate through the generator and write to the file
            f.write(chunk)
    return audio_path

# 5. Main Function to Create Story
def create_adaptive_story(theme, age_range, learning_style, voice):
    """Main function to create a complete adaptive story."""
    base_story = generate_base_story(theme, age_range, learning_style)
    adapted_story = adapt_for_learning_style(base_story, learning_style)
    audio = generate_audio(adapted_story, voice)
    image_url = generate_images(adapted_story)
    return {
        "text": adapted_story,
        "audio": audio,
        "image": image_url
    }

# 6. Streamlit Web Interface
def create_web_interface():
    st.title("AI Storyteller's Companion")

    # Input controls
    theme = st.text_input("Story Theme", "garden adventure")
    age_range = st.selectbox("Age Range", ["3-5", "6-8", "9-11"])
    learning_style = st.selectbox("Learning Style", ["Visual", "Auditory", "Kinesthetic"])

    # Fetch available voices (excluding Bella)
    try:
        voices = [voice.name for voice in elevenlabs_client.voices if voice.name.lower() != "bella"]
    except Exception as e:
        st.error(f"Error fetching voices: {e}")
        voices = ["Rachel"]  # Fallback to a default voice

    voice = st.selectbox("Select Voice for Narration", voices)

    if st.button("Generate Story"):
        with st.spinner("Creating your story..."):
            story_package = create_adaptive_story(theme, age_range, learning_style, voice)

        st.write("### Your Story")
        st.write(story_package["text"])

        st.write("### Illustration")
        if story_package["image"]:
            st.image(story_package["image"], caption="A magical scene from your story", use_container_width=True)

        st.write("### Audio Narration")
        if story_package["audio"]:
            st.audio(story_package["audio"])


# Entry Point
if __name__ == "__main__":
    create_web_interface()
