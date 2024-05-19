import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
import os
import tempfile
import uuid

class DocumentProcessor:
    """
    This class encapsulates the functionality for processing uploaded PDF documents using Streamlit
    and LangChain's PyPDFLoader. IT provides a method to render a file uploader widget, process the 
    uploaded PDF files, extract their pages, and display the total number of pages extracted.
    """

    def __init__(self):
        self.pages = [] # List to keep track of pages from all documents

    def ingest_document(self):
        """
        Renders a file uploader in Streamlit app, processes uploaded PDF file,
        extracts their pages, and upadtes the self.pages list with the total number of pages.
        """

        # Render a file uploader widget
        uploaded_files = st.file_uploader(
            label="Choose a file",
            type=['pdf'],
            accept_multiple_files=True
        )

        if uploaded_files is not None:
            for file in uploaded_files:
                # Generate a unique identifier to append to the file's original name
                unique_id = uuid.uuid4().hex
                original_name, file_extension = os.path.splitext(file.name)
                temp_file_name = f"{original_name}_{unique_id}{file_extension}"
                temp_file_path = os.path.join(tempfile.gettempdir(), temp_file_name)

                # Write the uploaded PDF to temporary file
                with open(temp_file_path, 'wb') as f:
                    f.write(file.getvalue())

                # Process the temporary file
                loader = PyPDFLoader(temp_file_path)

                # Add the extracted pages to the 'pages' list
                self.pages.extend(loader.load_and_split())

                # Clean up by deleting the temp file
                os.unlink(temp_file_path)
            # Display the total number of pages processed
            st.write(f"Total pages processed: {len(self.pages)}")

if __name__ == "__main__":
    processor = DocumentProcessor()
    processor.ingest_document()