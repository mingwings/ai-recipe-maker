import streamlit as st
import requests  # For making HTTP requests to OpenRouter's API

# Set your OpenRouter API key
OPENROUTER_API_KEY = "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"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Streamlit app title
st.title("AI Recipe Maker 🍳 (Powered by OpenRouter)")

# User input for ingredients
ingredients = st.text_area("Enter the ingredients you have (comma-separated):", "chicken, rice, tomatoes, onions")

# User input for notes
notes = st.text_area("Any additional notes or preferences (optional):", "e.g., make it spicy, I don't have an oven, etc.")

# Dropdown for selecting AI model
model = st.selectbox(
    "Choose an AI model:",
    ("gpt-3.5-turbo", "gpt-4", "claude-2", "mistral-7b")  # Add more models as needed
)

# Button to generate recipe
if st.button("Generate Recipe"):
    if ingredients:
        # Create a prompt for the AI, including the notes
        prompt = f"Create a detailed recipe using the following ingredients: {ingredients}."
        if notes:
            prompt += f" Additional notes: {notes}."
        prompt += " Include step-by-step instructions."

        # Prepare the request payload for OpenRouter
        payload = {
            "model": model,  # Use the selected model
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }

        # Add headers (including API key)
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        # Call the OpenRouter API
        response = requests.post(OPENROUTER_API_URL, json=payload, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response (adjust based on OpenRouter's response structure)
            recipe = response.json()["choices"][0]["message"]["content"]
            st.subheader("Generated Recipe:")
            st.write(recipe)
        else:
            st.error(f"Failed to generate recipe. Error: {response.text}")
    else:
        st.warning("Please enter some ingredients!")