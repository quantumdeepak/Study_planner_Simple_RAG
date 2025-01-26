import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class VectorDatabase:
    def __init__(self, documents):
        """
        Initialize vector database with documents
        
        :param documents: List of document texts
        """
        # Load pre-trained sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Handle empty documents list
        if not documents:
            self.embeddings = np.array([])
            self.index = None
            self.documents = []
            return
        
        # Generate embeddings
        try:
            self.embeddings = self.model.encode(documents)
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            self.embeddings = np.array([])
        
        # Create FAISS index
        if len(self.embeddings) > 0:
            dimension = self.embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(self.embeddings)
        else:
            self.index = None
        
        # Store original documents
        self.documents = documents

    def search_similar_docs(self, query, top_k=3):
        """
        Search for similar documents
        
        :param query: Search query string
        :param top_k: Number of top similar documents to return
        :return: Tuple of (indices of similar documents, relevance scores)
        """
        # Check if index exists
        if self.index is None or len(self.embeddings) == 0:
            return [], []
        
        # Encode query
        query_embedding = self.model.encode([query])
        
        # Search in FAISS index
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Calculate relevance scores (lower distance means higher relevance)
        relevance_scores = 1 / (1 + distances[0])
        
        return indices[0], relevance_scores

    def get_similar_doc_texts(self, query, top_k=3):
        """
        Get texts of similar documents
        
        :param query: Search query string
        :param top_k: Number of top similar documents to return
        :return: List of similar document texts
        """
        indices, _ = self.search_similar_docs(query, top_k)
        return [self.documents[i] for i in indices if i < len(self.documents)]