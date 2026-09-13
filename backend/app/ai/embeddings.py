import numpy as np

import json

class EmbeddingGenerator:
    """
    Generate embeddings for text using various methods.
    In production, this would use OpenAI embeddings, sentence-transformers, etc.
    """
    
    def __init__(self, model_name: str = "default"):
        self.model_name = model_name
        # In production, load actual ML models here
        self.embedding_dim = 384  # Default dimension for many sentence transformers
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        This is a simplified version using TF-IDF-like approach.
        """
        # In production, use actual embedding models
        # For now, create a simple hash-based embedding
        words = text.lower().split()
        
        # Create a simple feature vector
        embedding = np.zeros(self.embedding_dim)
        
        for i, word in enumerate(words):
            # Use word hash to determine which dimensions to set
            hash_val = hash(word) % self.embedding_dim
            embedding[hash_val] += 1
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def generate_embeddings_batch(self, texts: list[str]) -> list[np.ndarray]:
        """
        Generate embeddings for multiple texts.
        """
        return [self.generate_embedding(text) for text in texts]
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        """
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def find_most_similar(self, query_embedding: np.ndarray, 
                         candidate_embeddings: list[np.ndarray],
                         top_k: int = 5) -> list[tuple]:
        """
        Find the most similar embeddings to a query.
        """
        similarities = []
        
        for i, candidate_emb in enumerate(candidate_embeddings):
            similarity = self.calculate_similarity(query_embedding, candidate_emb)
            similarities.append((i, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]

class OpenAIEmbeddingGenerator(EmbeddingGenerator):
    """
    Generate embeddings using OpenAI's API.
    Requires OPENAI_API_KEY in settings.
    """
    
    def __init__(self, api_key: str = None, model: str = "text-embedding-ada-002"):
        super().__init__(model)
        self.api_key = api_key
        self.model = model
        
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding using OpenAI API.
        """
        if not self.api_key:
            # Fallback to simple embedding if no API key
            return super().generate_embedding(text)
        
        try:
            import openai
            openai.api_key = self.api_key
            
            response = openai.Embedding.create(
                input=text,
                model=self.model
            )
            
            embedding = np.array(response['data'][0]['embedding'])
            return embedding
            
        except Exception as e:
            print(f"Error generating OpenAI embedding: {e}")
            # Fallback to simple embedding
            return super().generate_embedding(text)
