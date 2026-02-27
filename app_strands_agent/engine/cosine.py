import math
import numpy as np
 
def cosine_similarity(vec_a, vec_b) -> float:
    """
    Compute cosine similarity between two vectors.
 
    Args:
        vec_a: First vector.
        vec_b: Second vector.
 
    Returns:
        Cosine similarity score.
    """
    dot_product = sum(x * y for x, y in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(x * x for x in vec_a))
    norm_b = math.sqrt(sum(y * y for y in vec_b))
    return dot_product / (norm_a * norm_b)
 
def dot_similarity_batch(query, matrix: np.ndarray) -> np.ndarray:
    """
    Compute dot-product similarity between a query and a matrix of vectors.
 
    For L2-normalized embeddings (e.g. Titan Embed V2 with normalize=True),
    dot product equals cosine similarity. Uses a single BLAS sgemv call.
 
    Args:
        query: 1-D query vector of shape (dim,).
        matrix: 2-D matrix of cached embeddings, shape (N, dim), float32.
 
    Returns:
        1-D array of similarity scores, shape (N,).
    """
    q = np.asarray(query, dtype=np.float32)
    return matrix @ q