import streamlit as st
import os
import sys

sys.path.append(os.path.abspath('../'))

class QuizManager:
    def __init__(self, questions: list):
        """
        Initilize the QuizManager class with a list of quiz question
        """
        self.questions = questions
        self.total_questions = len(questions)

    def get_question_at_index(self, index: int):
        """
        Retrieves the quiz question object at the specified index. If the index is out og bounds.
        it restarts from the beginning index
        """
        valid_index = index % self.total_questions
        return self.questions[valid_index]

    def next_question_index(self, direction=1):
        """
        Adjust the current quiz question index based on the specified direction
        """

        next_index = (st.session_state["question_index"] + direction) % self.total_questions
        st.session_state["question_index"] = next_index
        return self.questions[next_index]

# Test the Object
if __name__ == "__main__":
    
    from components.document_processor import DocumentProcessor
    from components.embedding_client import EmbeddingClient
    from components.chroma_collection import ChromaCollectionCreator
    from components.quiz_generator import QuizGenerator

    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": "sample-mission-421421",
        "location": "us-central1"
    }
    
    screen = st.empty()
    with screen.container():
        st.header("Quiz Builder")
        processor = DocumentProcessor()
        processor.ingest_documents()
    
        embed_client = EmbeddingClient(**embed_config) 
    
        chroma_creator = ChromaCollectionCreator(processor, embed_client)
    
        question = None
        question_bank = None
    
        with st.form("Load Data to Chroma"):
            st.subheader("Quiz Builder")
            st.write("Select PDFs for Ingestion, the topic for the quiz, and click Generate!")
            
            topic_input = st.text_input("Topic for Generative Quiz", placeholder="Enter the topic of the document")
            questions = st.slider("Number of Questions", min_value=1, max_value=10, value=1)
            
            submitted = st.form_submit_button("Submit")
            if submitted:
                chroma_creator.create_chroma_collection()
                
                st.write(topic_input)
                
                # Test the Quiz Generator
                generator = QuizGenerator(topic_input, questions, chroma_creator)
                question_bank = generator.generate_quiz()

    if question_bank:
        screen.empty()
        with st.container():
            st.header("Generated Quiz Question: ")
            
            # Task 9
            ##########################################################
            quiz_manager = QuizManager(question_bank) # Use our new QuizManager class
            # Format the question and display
            with st.form("Multiple Choice Question"):
                ##### YOUR CODE HERE #####
                index_question = quiz_manager.get_question_at_index(0) # Use the get_question_at_index method to set the 0th index
                ##### YOUR CODE HERE #####
                
                # Unpack choices for radio
                choices = []
                for choice in index_question['choices']: # For loop unpack the data structure
                    ##### YOUR CODE HERE #####
                    # Set the key from the index question 
                    key = choice['key']
                    # Set the value from the index question
                    value = choice['value']
                    ##### YOUR CODE HERE #####
                    choices.append(f"{key}) {value}")
                
                ##### YOUR CODE HERE #####
                # Display the question onto streamlit
                st.text(index_question['question'])
                ##### YOUR CODE HERE #####
                
                answer = st.radio( # Display the radio button with the choices
                    'Choose the correct answer',
                    choices
                )
                st.form_submit_button("Submit")
                
                if submitted: # On click submit 
                    correct_answer_key = index_question['answer']
                    if answer.startswith(correct_answer_key): # Check if answer is correct
                        st.success("Correct!")
                    else:
                        st.error("Incorrect!")