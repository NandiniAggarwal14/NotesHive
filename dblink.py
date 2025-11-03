import pandas as pd
from sqlalchemy import create_engine

user = "root"
password = "Nandini.14"
host = "localhost"
database = "notehive"

engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")

query = "SELECT note_id, title, description, file_path, uploaded_by AS user_id FROM note;"

df = pd.read_sql(query, engine)

df['content'] = df['title'].astype(str) + " " + df['description'].astype(str)


print(df[['note_id', 'content', 'user_id']].head())

df.to_csv("notes_with_content.csv", index=False)
print("\nCSV notes_with_content.csv generated successfully with user_id column.")
