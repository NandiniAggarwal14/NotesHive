import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np

df = pd.read_csv("notes_with_content.csv")

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(df['content'].tolist())

np.save("note_embeddings.npy", embeddings)
print("Embeddings saved to note_embeddings.npy")