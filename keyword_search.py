import pandas as pd
from sqlalchemy import create_engine

# -----------------------------
# Database Configuration (reuse from dblink.py)
# -----------------------------
USER = "root"
PASSWORD = "Nandini.14"
HOST = "localhost"
DATABASE = "notehive"

engine = create_engine(f"mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}/{DATABASE}")

# -----------------------------
# Load Notes Function
# -----------------------------
def load_notes():
    """
    Load notes from DB or fallback CSV.
    Includes user_id for filtering.
    """
    try:
        query = "SELECT note_id, title, description, file_path, uploaded_by AS user_id FROM note;"
        df = pd.read_sql(query, engine)
    except Exception as e:
        print(f"[Warning] Could not fetch from DB ({e}), using CSV fallback.")
        df = pd.read_csv("notes_with_content.csv")

    # Combine title + description for keyword search
    df["content"] = df["title"].astype(str) + " " + df["description"].astype(str)
    return df

# -----------------------------
# Keyword Search Function
# -----------------------------
def search_notes_by_keyword(query: str, user_id: int = None, top_n: int = 10):
    """
    Search notes by keywords in title + description.
    Optional filter by user_id.
    Returns top_n results sorted by keyword match count.
    """
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string.")

    df = load_notes()

    # Optional user filter
    if user_id is not None:
        if "user_id" in df.columns:
            df = df[df["user_id"] == int(user_id)]
        else:
            print("[Warning] user_id column not found. Ignoring user filter.")

    # Split query into lowercase keywords
    keywords = [word.lower() for word in query.split() if word.strip()]

    # Simple keyword frequency scoring
    def score(text):
        text_lower = str(text).lower()
        return sum(text_lower.count(k) for k in keywords)

    df["score"] = df["content"].apply(score)

    # Filter out zero-score entries and sort by score
    df = df[df["score"] > 0].sort_values(by="score", ascending=False)

    # Limit top_n results
    results = df.head(top_n)[["note_id", "title", "description", "file_path", "score"]].to_dict(orient="records")
    return results

# -----------------------------
# Example Run (Standalone Test)
# -----------------------------
if __name__ == "__main__":
    query = "AI basics"
    user_id = 2311  # optional, show only this user's notes
    results = search_notes_by_keyword(query, user_id=user_id, top_n=5)

    if results:
        print("\nTop Keyword Search Results:")
        for r in results:
            print(f"• {r['title']} ({r['score']}) → {r['file_path']}")
    else:
        print("No matches found.")
