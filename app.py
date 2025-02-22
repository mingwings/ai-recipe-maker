import streamlit as st
import requests  # For making HTTP requests to OpenRouter's API
import pandas as pd

# Set your OpenRouter API key
OPENROUTER_API_KEY = st.text_input("Enter your OpenRouter API key:", type="password")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Initialize ingredient database if not already present
if "ingredient_db" not in st.session_state:
    st.session_state.ingredient_db = pd.DataFrame(columns=["Ingredient", "Quantity", "Unit"])

# Streamlit app title
st.title("Marina's Recipe Maker and Inventory Tracker")

# Section 1: Manage Ingredient Inventory
st.header("Manage Your Ingredient Inventory")
with st.form("add_ingredient_form"):
    ingredient_name = st.text_input("Ingredient Name:")
    ingredient_quantity = st.number_input("Quantity:", min_value=0.0, step=0.1)
    ingredient_unit = st.selectbox("Unit:", ["grams", "pieces"])
    add_ingredient = st.form_submit_button("Add/Update Ingredient")

if add_ingredient and ingredient_name:
    if ingredient_name in st.session_state.ingredient_db["Ingredient"].values:
        idx = st.session_state.ingredient_db["Ingredient"] == ingredient_name
        st.session_state.ingredient_db.loc[idx, ["Quantity", "Unit"]] = [ingredient_quantity, ingredient_unit]
    else:
        new_data = pd.DataFrame({"Ingredient": [ingredient_name], "Quantity": [ingredient_quantity], "Unit": [ingredient_unit]})
        st.session_state.ingredient_db = pd.concat([st.session_state.ingredient_db, new_data], ignore_index=True)
    st.success(f"{ingredient_name} added/updated successfully!")

# Display current inventory
st.subheader("Current Inventory")
st.dataframe(st.session_state.ingredient_db)

# Section 2: Recipe Generation
st.header("Generate a Recipe")

# User input for ingredients
selected_ingredients = st.multiselect(
    "Select ingredients from your inventory:",
    st.session_state.ingredient_db["Ingredient"].tolist()
)

# User input for notes
notes = st.text_area("Any additional notes or preferences (optional):", "e.g., make it spicy, I don't have an oven, etc.")

# Dropdown for selecting AI model
model = st.selectbox(
    "Choose an AI model:",
    ("gpt-3.5-turbo", "gpt-4", "claude-2", "mistral-7b")  # Add more models as needed
)

# Button to generate recipe
if st.button("Generate Recipe"):
    if selected_ingredients:
        # Create a prompt for the AI, including the notes
        ingredients_with_units = [
            f"{row['Ingredient']} ({row['Quantity']} {row['Unit']})"
            for _, row in st.session_state.ingredient_db[st.session_state.ingredient_db["Ingredient"].isin(selected_ingredients)].iterrows()
        ]
        ingredients = ", ".join(ingredients_with_units)
        prompt = f"Create a detailed recipe using the following ingredients: {ingredients}."
        if notes:
            prompt += f" Additional notes: {notes}."
        prompt += " Include step-by-step instructions and list the quantities of ingredients used."

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
            
            # Confirmation to update inventory
            if st.button("Confirm and Update Inventory"):
                # For simplicity, we'll assume 1 unit used for each ingredient
                for ingredient in selected_ingredients:
                    idx = st.session_state.ingredient_db["Ingredient"] == ingredient
                    st.session_state.ingredient_db.loc[idx, "Quantity"] -= 1
                st.success("Inventory updated successfully!")
        elif response.status_code == 401:
            st.error("Invalid API credentials. Please check your OpenRouter API key.")
        else:
            st.error(f"Failed to generate recipe. Error: {response.text}")
    else:
        st.warning("Please select some ingredients!")
