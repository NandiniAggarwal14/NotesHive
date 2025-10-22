import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_csv("notes_with_content.csv")
embeddings = np.load("note_embeddings.npy")
model = SentenceTransformer('all-MiniLM-L6-v2')

def semantic_search(query, top_k=3):
    query_emb = model.encode([query])
    scores = cosine_similarity(query_emb, embeddings)[0]
    top_indices = np.argsort(scores)[::-1][:top_k]
    results = df.iloc[top_indices][['title', 'description', 'file_path']].copy()
    results['similarity'] = scores[top_indices]
    return results

if __name__ == "__main__":
    query ="process scheduling in operating system"
    top_notes = semantic_search(query, top_k=5)
    print(top_notes)
