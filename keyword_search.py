import pandas as pd
from sqlalchemy import create_engine

USER = "root"
PASSWORD = "Nandini.14"
HOST = "localhost"
DATABASE = "notehive"

engine = create_engine(f"mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}/{DATABASE}")

def load_notes():

    try:
        query = "SELECT note_id, title, description, file_path, uploaded_by AS user_id FROM note;"
        df = pd.read_sql(query, engine)
    except Exception as e:
        print(f"[Warning] Could not fetch from DB ({e}), using CSV fallback.")
        df = pd.read_csv("notes_with_content.csv")

    df["content"] = df["title"].astype(str) + " " + df["description"].astype(str)
    return df

def search_notes_by_keyword(query: str, user_id: int = None, top_n: int = 10):
    
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string.")

    df = load_notes()

  
    if user_id is not None:
        if "user_id" in df.columns:
            df = df[df["user_id"] == int(user_id)]
        else:
            print("[Warning] user_id column not found. Ignoring user filter.")

    keywords = [word.lower() for word in query.split() if word.strip()]

    def score(text):
        text_lower = str(text).lower()
        return sum(text_lower.count(k) for k in keywords)

    df["score"] = df["content"].apply(score)

    df = df[df["score"] > 0].sort_values(by="score", ascending=False)

    results = df.head(top_n)[["note_id", "title", "description", "file_path", "score"]].to_dict(orient="records")
    return results

if __name__ == "__main__":
    query = "AI basics"
    user_id = 2311 
    results = search_notes_by_keyword(query, user_id=user_id, top_n=5)

    if results:
        print("\nTop Keyword Search Results:")
        for r in results:
            print(f"• {r['title']} ({r['score']}) → {r['file_path']}")
    else:
        print("No matches found.")
