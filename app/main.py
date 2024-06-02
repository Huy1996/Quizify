import streamlit as st
import os
import sys
import json

from components.chroma_collection import ChromaCollectionCreator
from components.document_processor import DocumentProcessor
from components.embedding_client import EmbeddingClient
from components.quiz_generator import QuizGenerator
from components.quiz_manager import QuizManager

if __name__ == "__main__":
    
    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": "sample-mission-421421",
        "location": "us-central1"
    }
    
    # Add Session State
    if 'question_bank' not in st.session_state or len(st.session_state['question_bank']) == 0:
        
        # init the question bank list in st.session_state
        st.session_state['question_bank'] = []
    
        screen = st.empty()
        with screen.container():
            st.header("Quiz Builder")
            
        
            # Create a new st.form flow control for Data Ingestion
            with st.form("Load Data to Chroma"):

                processor = DocumentProcessor()
                processor.ingest_documents()
                embed_client = EmbeddingClient(**embed_config) 
                chroma_creator = ChromaCollectionCreator(processor, embed_client)

                st.write("Select PDFs for Ingestion, the topic for the quiz, and click Generate!")
                
                # Set topic input and number of questions
                topic_input = st.text_input("Enter the quiz topic:", placeholder="Enter the topic of the document")
                num_question = st.slider("Select the number of questions", min_value=1, max_value=20, value=5)
                    
                submitted = st.form_submit_button("Submit")
                
                if submitted:
                    chroma_creator.create_chroma_collection()
                        
                    if len(processor.pages) > 0:
                        st.write(f"Generating {num_question} questions for topic: {topic_input}")
                    
                    # Initialize a QuizGenerator class using the topic, number of questrions, and the chroma collection
                    generator = QuizGenerator(topic_input, num_question, chroma_creator)
                    question_bank = generator.generate_quiz()
                    # Initialize the question bank list in st.session_state
                    st.session_state.question_bank = question_bank
                    # Set a display_quiz flag in st.session_state to True
                    st.session_state['display_quiz'] = True
                    # Set the question_index to 0 in st.session_state
                    st.session_state['question_index'] = 0
                    
                    print(st.session_state.question_bank)
                    st.rerun()


    elif st.session_state["display_quiz"]:        
        st.empty()
        with st.container():
            st.header("Generated Quiz Question: ")
            # quiz_manager = QuizManager(question_bank)
            quiz_manager = QuizManager(st.session_state['question_bank'])
            
            # Format the question and display it
            with st.form("MCQ"):
                ##### YOUR CODE HERE #####
                # Step 7: Set index_question using the Quiz Manager method get_question_at_index passing the st.session_state["question_index"]
                index_question = quiz_manager.get_question_at_index(st.session_state['question_index'])
                ##### YOUR CODE HERE #####
                
                # Unpack choices for radio button
                choices = []
                for choice in index_question['choices']:
                    key = choice['key']
                    value = choice['value']
                    choices.append(f"{key}) {value}")
                
                # Display the Question
                st.write(f"{st.session_state['question_index'] + 1}. {index_question['question']}")
                answer = st.radio(
                    "Choose an answer",
                    choices,
                    index = None
                )
                
                answer_choice = st.form_submit_button("Submit")
                
                # Use the example below to navigate to the next and previous questions
                st.form_submit_button("Next Question", on_click=lambda: quiz_manager.next_question_index(direction=1))
                st.form_submit_button("Previous Question", on_click=lambda: quiz_manager.next_question_index(direction=-1))
                
                if answer_choice and answer is not None:
                    correct_answer_key = index_question['answer']
                    if answer.startswith(correct_answer_key):
                        st.success("Correct!")
                    else:
                        st.error("Incorrect!")
                    st.write(f"Explanation: {index_question['explanation']}")