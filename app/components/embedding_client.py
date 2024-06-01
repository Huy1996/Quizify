from langchain_google_vertexai import VertexAIEmbeddings


class EmbeddingClient:
    """
    The EmbeddingClient class capable of intitializing and embedding client with specific configurations
    for model name, project, and location.
    """
    
    def __init__(self, model_name, project, location):
        self.client = VertexAIEmbeddings(
            model_name=model_name,
            project=project,
            location=location
        )

    def embed_query(self, query):
        """
        Use the embbeding client to retrieve embeddings fot the given query
        """
        vectors = self.client.embed_query(query)
        return vectors
    
    def embed_documents(self, documents):
        """
        Retrieve embedding for multiple documents.
        """
        try:
            return self.client.embed_documents(documents)
        except AttributeError:
            print("Method embed_documents not defined for the client.")
            return None