import pandas as pd
from sqlalchemy import create_engine
from sentence_transformers import SentenceTransformer
import numpy as np

user = "root"
password = "Nandini.14"
host = "localhost"
database = "notehive"

engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")

query = "SELECT note_id, title, description, file_path, uploaded_by AS user_id FROM note;"

df = pd.read_sql(query, engine)

# Create combined content for embedding
df['content'] = df['title'].astype(str) + " " + df['description'].astype(str)

# Load sentence transformer model
print("Loading semantic search model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings for each note
print("Generating embeddings for notes...")
embeddings = model.encode(df['content'].tolist(), show_progress_bar=True)

# Add embeddings to dataframe
# Convert embeddings to string format for CSV storage
df['embedding'] = [np.array2string(emb, separator=',') for emb in embeddings]

print("\n" + "="*50)
print("Sample data:")
print(df[['note_id', 'content', 'user_id']].head())
print("="*50)

# Save to CSV
df.to_csv("notes_with_content.csv", index=False)
print("\n✅ CSV 'notes_with_content.csv' generated successfully!")
print(f"   - Total notes: {len(df)}")
print(f"   - Columns: {', '.join(df.columns)}")
print(f"   - Embeddings dimension: {embeddings.shape[1]}")
