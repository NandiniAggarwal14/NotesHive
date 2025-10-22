import pandas as pd
from sqlalchemy import create_engine

user = "root"
password ="Nandini.14"
host = "localhost"
database = "notehive"

engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")

query = "SELECT note_id, title, description, file_path FROM note;"

df = pd.read_sql(query, engine)


df['content'] = df['title'] + " " + df['description']
print(df[['note_id', 'content']].head())

df.to_csv("notes_with_content.csv", index=False)