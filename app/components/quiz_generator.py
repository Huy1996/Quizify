import streamlit as st
from langchain_google_vertexai import VertexAI
from langchain_core.prompts import PromptTemplate
import langchain_core.output_parsers.json as json
import os
import sys
sys.path.append(os.path.abspath('../'))

class QuizGenerator:
    def __init__(self, topic=None, num_questions=1, vectorstore=None):
        """
        Initializes the QuizGenerator with a required topic, the number of questions for the quiz,
        and an optional vectorstore for querying related information.

        :param topic: A string representing the required topic for the quiz
        :param num_questions: An integer representing the number of questions to generate for the quiz, up to a maximum of 10/
        :param vectorstore: An optional vectorstore instance (e.g., ChromaDB) to be used for querying information related to the quiz topic.
        """
        if not topic:
            self.topic = "General Knowledge"
        else:
            self.topic = topic

        if num_questions > 10:
            raise ValueError("Number of questions cannot exceed 10.")
        self.num_questions = num_questions

        self.vectorstore = vectorstore
        self.llm = None
        self.system_template = """
            You are a subject matter expert on the topic: {topic}
            
            Follow the instructions to create a quiz question:
            1. Generate a question based on the topic provided and context as key "question"
            2. Provide 4 multiple choice answers to the question as a list of key-value pairs "choices"
            3. Provide the correct answer for the question from the list of answers as key "answer"
            4. Provide an explanation as to why the answer is correct as key "explanation"
            
            You must respond as a JSON object with the following structure:
            {{
                "question": "<question>",
                "choices": [
                    {{"key": "A", "value": "<choice>"}},
                    {{"key": "B", "value": "<choice>"}},
                    {{"key": "C", "value": "<choice>"}},
                    {{"key": "D", "value": "<choice>"}}
                ],
                "answer": "<answer key from choices list>",
                "explanation": "<explanation as to why the answer is correct>"
            }}
            
            Context: {context}
            """
        
    def init_llm(self):
        """
        Initialize the Large Language Model for quiz question generator/
        """
        self.llm = VertexAI(
            model_name="gemini-pro",
            temperature=0.5,
            max_output_tokens=500
        )

    def generate_question_with_vectorstore(self):
        """
        This method leverages the vectorstore to retrieve relevant context for the quiz topic, then utilizes the LLM to generate a structured quiz question in JSON format.
        The process involves retrieving documents, creating a prompt, and invoking the LLM to generate a question.
        
        Implementation:
        - Utitlize 'RunnableParallel' and 'RunnablePassthrough' to create a chain that integrates documents retrieva; and topic processing.
        - Format the system template with the topic and retrieved contexr to create a comprehensive prompt for the LLM.
        - Use the LLM to generate a quiz question based on the prompt and return the structured response.
        """

        # Initilize the LLM from the 'init_llm' method if not already initizied
        if not self.llm:
            self.init_llm()
        if not self.vectorstore:
            raise ValueError('Vectorstore not provided.')

        from langchain_core.runnables import RunnablePassthrough, RunnableParallel

        # Enable a Retriever using as_retriever() method on the VectorStore object
        retriever = self.vectorstore.as_retriever()

        # Use the system template to create a PromptTemplate
        prompt = PromptTemplate.from_template(self.system_template)

        # RunnableParallel allow Retriver to get relevant documents
        # RunnablePassThrough allows chain.invoke to send self.topic to LLM
        setup_and_retrieval = RunnableParallel(
            {"context": lambda x: retriever, "topic": RunnablePassthrough()}
        )

        # Create a chain with the Retriever, PromptTemplate, and LLM
        chain = setup_and_retrieval | prompt | self.llm

        # Invoke the chain with the topic as input
        response = chain.invoke(self.topic)
        return response

    def generate_quiz(self) -> list:
        """
        Generate a list of unique quiz question based on the specified topic and number of question.
        
        This method orchestrates the quiz generation process by utilizing the `generate_question_with_vectorstore` method to generate
        each question and the `validate_question` method to ensure its uniqueness before adding it to the quiz.

        Returns:
        - A list of distionaries, where each dictionary represents a unique quiz question generated based on the topic
        """

        # Reset question bank
        self.question_bank = []

        retry_limit = 3
        retry_count = 0

        for _ in range(self.num_questions):
            if retry_count >= retry_limit:
                break
            while True:
                # Generate question
                question_str = self.generate_question_with_vectorstore()

                try:
                    question = json.parse_json_markdown(question_str)
                except json.JSONDecodeError:
                    print("Failed to decode question JSON.")
                    retry_count += 1
                    continue # Skip this iteration if JSON decoding fails

                # Validate question using the validate_question method
                if self.validate_question(question):
                    print("Successfully generated unique question.")
                    # Add the valid question into question bank
                    self.question_bank.append(question)
                    retry_count = 0
                    break
                else:
                    print("Duplicate or invalid question detected")
                    retry_count += 1
        
        return self.question_bank
            
    def validate_question(self, question: dict) -> bool:
        """
        Validate a quiz question for uniqueness within generated quiz
        """

        new_question_text = question['question']
        for q in self.question_bank:
            if q['question'] == new_question_text:
                return False
        return True

                    

# Test the Object
if __name__ == "__main__":
    
    from components.document_processor import DocumentProcessor
    from components.embedding_client import EmbeddingClient
    from components.chroma_collection import ChromaCollectionCreator
    
    
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
    
        embed_client = EmbeddingClient(**embed_config) # Initialize from Task 4
    
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
                question = question_bank[0]

    if question_bank:
        screen.empty()
        with st.container():
            st.header("Generated Quiz Question: ")
            for question in question_bank:
                st.write(question)