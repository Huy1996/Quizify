import sys
import os
import streamlit as st
sys.path.append(os.path.abspath('../'))
from components.document_processor import DocumentProcessor
from components.embedding_client import EmbeddingClient

from langchain_core.documents import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma

class ChromaCollectionCreator:
    def __init__(self, processor, embed_model):
        """
        Initializes the ChromaCollectionCreator with a DocumemtProcessor instance and embedddings configuration.
        :param processor: An instance of DocumentProcessor that has processed documents.
        :param embed_model: An embedding client for embedding documents
        """
        self.processor = processor
        self.embed_model = embed_model
        self.db = None
    
    def create_chroma_collection(self):
        """
        Create a Chroma colection from the documents processed by the DocumentProcessor instance.
        """

        # Step 1: Check for processed documents
        if len(self.processor.pages) == 0:
            st.error("No documents found!", icon="🚨")
            return
        
        # Step 2: Split documents into text chunks
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200
        )
        texts = text_splitter.split_documents(self.processor.pages)

        if texts is not None:
            st.success(f"Successfully split pages in {len(texts)} documents!", icon="✅")

        # Step 3: Create Chroma Collection
        self.db = Chroma.from_documents(
            texts,
            self.embed_model
        )

        if self.db:
            st.success("Successfully created Chorma Collection!", icon="✅")
        else:
            st.error("Failed to create Chroma Collection!", icon="🚨")

    def query_chroma_collection(self, query) -> Document:
        """
        Queries the created Chroma Collection for documents similar to the query.
        :param query: The query string to search for in the Chorma Collection
        """
        if self.db:
            docs = self.db.similarity_search_by_vector_with_relevance_scores(query)
            if docs:
                return docs[0]
            else:
                st.error("No matching document found!", icon="🚨")
        else:
            st.error("Chroma Collection has not been created!", icon="🚨")

    def as_retriever(self):
        self.db.as_retriever()

if __name__ == "__main__":
    processor = DocumentProcessor() # Initialize from Task 3
    processor.ingest_documents()
    
    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": "sample-mission-421421",
        "location": "us-central1"
    }
    
    embed_client = EmbeddingClient(**embed_config) # Initialize from Task 4
    
    chroma_creator = ChromaCollectionCreator(processor, embed_client)
    
    with st.form("Load Data to Chroma"):
        st.write("Select PDFs for Ingestion, then click Submit")
        
        submitted = st.form_submit_button("Submit")
        if submitted:
            chroma_creator.create_chroma_collection()
    