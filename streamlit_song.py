pip install -r requirements.txt

import streamlit as st
import openai
import json
import pandas as pd

# Get the API key from the sidebar called OpenAI API key
user_api_key = st.sidebar.text_input("OpenAI API key", type="password")

# Set up OpenAI client
client = openai.OpenAI(api_key=user_api_key)

# Updated prompt to handle both song identification and vocabulary extraction
prompt = """You are an AI assistant capable of handling both translation and vocabulary extraction. 
            You will receive Japanese song lyrics. Your task is to:
            1. Identify the song title and translate the entire lyrics into English.
            2. Extract interesting vocabulary words from the lyrics and provide the following information for each word:
                - "Original Word": The original Japanese word.
                - "English Translation": The English translation of the word.
                - "Synonym (Japanese)": A synonym for the word in Japanese.
                - "Description (Japanese)": A short description of the word in Japanese.
                - "Description (English)": A short description of the word in English.
            Return the result in JSON format with two parts:
            - The first part is the song title and full English translation of the lyrics.
            - The second part is a JSON array of interesting vocabulary with the fields mentioned above.
            """

st.title('Japanese Song Vocabulary Extractor and Translator')
st.markdown('Input the lyrics of a Japanese song, and the AI will extract the song title, translate the lyrics into English, and extract interesting vocabulary with their translations and synonyms.')

# Text input for song lyrics
song_lyrics = st.text_area("Enter the song lyrics here:", "Your lyrics here")

# Submit button for song lyrics processing
if st.button('Submit'):
    # Define the conversation with the model for song identification and translation
    messages_so_far = [
        {"role": "system", "content": prompt},
        {'role': 'user', 'content': song_lyrics},
    ]
    
    # Get the response from OpenAI
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages_so_far
    )
    
    # Extract the result from the response
    st.markdown('**AI response (Song title, translation, and vocabulary extraction in JSON format):**')
    json_response = response.choices[0].message.content
    
    try:
        # Parse the JSON response
        result = json.loads(json_response)
        
        # Show song title and full translation
        song_title = result.get('song_title', 'Unknown Title')
        song_translation = result.get('song_translation', 'No translation available.')
        
        st.markdown(f"**Song Title:** {song_title}")
        st.markdown(f"**English Translation:** {song_translation}")
        
        # Show the vocabulary data as a table
        vocab_data = result.get('vocabulary', [])
        
        # Create a Pandas DataFrame from the vocabulary data
        if vocab_data:
            vocab_df = pd.DataFrame(vocab_data)
            st.table(vocab_df)
        else:
            st.warning("No vocabulary data found.")
    
    except json.JSONDecodeError as e:
        st.error(f"Error in parsing the JSON: {e}")
