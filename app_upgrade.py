import streamlit as st
import openai
import json
import re
import pandas as pd

# Get the API key from the sidebar called OpenAI API key
user_api_key = st.sidebar.text_input("OpenAI API key", type="password")

# Set up OpenAI client
openai.api_key = user_api_key

# Updated prompt for generating topic-based questions and answers, and extracting technical terms with descriptions
prompt = """You are an AI assistant capable of generating a list of questions based on a topic. 
            You will receive a random topic. Your task is to:
            1. Generate 10 questions about that topic.
            2. Generate answers for all questions in a separate list.
            3. Extract technical terms (e.g., keywords, important nouns, and domain-specific terms) from the questions and answers.
            4. For each technical term, provide a brief description.
            Return the result in JSON format with four parts:
            - The first part is a JSON array of questions.
            - The second part is a JSON array of answers.
            - The third part is a JSON array of technical terms (e.g., capitalized words, domain-specific terms).
            - The fourth part is a JSON array of descriptions for each technical term.
            """

st.title('Topic-Based Question Generator')
st.markdown('Enter a topic, and AI will generate questions, answers, and extract technical terms with descriptions for you.')

# Text input for the topic
topic = st.text_area("Enter the topic here:", "Your topic here")

# Submit button for processing the topic
if st.button('Generate Questions, Answers, and Technical Terms with Descriptions'):
    # Define the conversation with the model
    messages_so_far = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": topic},
    ]
    
    # Get the response from OpenAI
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages_so_far
    )
    
    # Extract the result from the response
    st.markdown('**AI Response (Raw):**')
    json_response = response.choices[0].message["content"]
    
    # Print the raw response for debugging purposes
    st.markdown(f"**Raw AI Response:**\n{json_response}")
    
    try:
        # Parse the JSON response
        result = json.loads(json_response)
        
        # Get the questions, answers, technical terms, and descriptions from the response
        questions = result.get('questions', [])
        answers = result.get('answers', [])
        technical_terms = result.get('technical_terms', [])
        descriptions = result.get('descriptions', [])
        
        # Display the questions and answers
        if questions and answers:
            st.markdown("### Questions:")
            for idx, question in enumerate(questions, 1):
                st.markdown(f"**Q{idx}:** {question}")
            
            st.markdown("### Answers:")
            for idx, answer in enumerate(answers, 1):
                st.markdown(f"**A{idx}:** {answer}")
            
            # Extract technical terms directly in this block
            all_text = ' '.join(questions + answers)
            technical_terms = re.findall(r'\b[A-Z][a-z]*\b', all_text)  # Extract capitalized words

            # Remove duplicates and sort the terms
            unique_terms = sorted(set(technical_terms))  # Remove duplicates and sort
            
            if unique_terms:
                # Get descriptions for each technical term
                term_descriptions = []
                for term in unique_terms:
                    # Request a description for each technical term from the model
                    description_response = openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "Provide a brief description of the technical term."},
                            {"role": "user", "content": term},
                        ]
                    )
                    term_description = description_response.choices[0].message["content"].strip()
                    term_descriptions.append(term_description)

                # Create a DataFrame to display the technical terms with their descriptions
                terms_df = pd.DataFrame({
                    "Technical Term": unique_terms,
                    "Description": term_descriptions
                })
                
                st.markdown("### Technical Terms with Descriptions:")
                st.table(terms_df)
            else:
                st.warning("No technical terms found.")
        else:
            st.warning("No questions or answers found.")
    
    except json.JSONDecodeError as e:
        st.error(f"Error in parsing the JSON response: {e}")
    except KeyError as e:
        st.error(f"Missing expected key in the response: {e}")
