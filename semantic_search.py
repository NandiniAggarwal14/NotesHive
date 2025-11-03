import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')

def semantic_search(query, data, top_k=5, min_similarity=0.2):
    if data is None or data.empty:
        return pd.DataFrame(columns=['title', 'description', 'file_path', 'similarity'])

    data['combined_text'] = data['title'].fillna('') + " " + data['description'].fillna('')

    note_embeddings = model.encode(data['combined_text'].tolist())
    query_emb = model.encode([query])

    scores = cosine_similarity(query_emb, note_embeddings)[0]

    relevant_indices = np.where(scores >= min_similarity)[0]
    if len(relevant_indices) == 0:
        return pd.DataFrame(columns=['title', 'description', 'file_path', 'similarity'])

    sorted_indices = relevant_indices[np.argsort(scores[relevant_indices])[::-1]][:top_k]

    results = data.iloc[sorted_indices].copy()
    results['similarity'] = scores[sorted_indices]

    return results[['title', 'description', 'file_path', 'similarity']].reset_index(drop=True)


if __name__ == "__main__":

    dummy_data = pd.DataFrame({
        'title': ['Machine Learning Basics', 'Deep Learning Guide', 'Cooking Pasta'],
        'description': ['Learn ML algorithms', 'Neural networks and CNNs', 'Step by step pasta recipe'],
        'file_path': ['ml.pdf', 'dl.pdf', 'pasta.pdf']
    })

    query = "introduction to deep learning"
    top_notes = semantic_search(query, data=dummy_data, top_k=3, min_similarity=0.2)

    if len(top_notes) == 0:
        print("No relevant notes found for your query.")
    else:
        print(f"\nTop relevant notes for '{query}':")
        print(top_notes)
