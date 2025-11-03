from flask import Flask, request, jsonify
from keyword_search import search_notes_by_keyword
from semantic_search import semantic_search
from sqlalchemy import create_engine, text
import pandas as pd

app = Flask(__name__)

# -----------------------------
# Database Config
# -----------------------------
user = "root"
password = "Nandini.14"
host = "localhost"
database = "notehive"
engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")

# -----------------------------
# Combined Search Endpoint
# -----------------------------
@app.route("/api/search", methods=["GET"])
def search_api():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    user_id = request.args.get("user_id")
    top_n = request.args.get("top_n", 5)
    search_type = request.args.get("search_type", "semantic").lower()
    min_similarity = request.args.get("min_similarity", 0.2)

    # Convert types
    try:
        top_n = int(top_n)
        min_similarity = float(min_similarity)
        if user_id is not None:
            user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "Invalid query parameters"}), 400

    try:
        # Fetch latest notes from DB to ensure search is up-to-date
        with engine.connect() as conn:
            query_notes = text("""
                SELECT n.note_id, n.title, n.description, n.file_path, n.subject_id, 
                       s.subject_name, n.uploaded_by, n.upload_date
                FROM Note n
                LEFT JOIN Subject s ON n.subject_id = s.subject_id
            """)
            notes_df = pd.read_sql(query_notes, conn)

        # Perform the selected search type
        if search_type == "keyword":
            results = search_notes_by_keyword(query, user_id=user_id, top_n=top_n)
        elif search_type == "semantic":
            results_df = semantic_search(
                query=query,
                data=notes_df,              
                top_k=top_n,
                min_similarity=min_similarity
            )

            if results_df.empty:
                return jsonify([])

            if user_id is not None and "uploaded_by" in results_df.columns:
                results_df = results_df[results_df["uploaded_by"] == user_id]

            results = results_df.to_dict(orient="records")
        else:
            return jsonify({"error": "Invalid search_type. Use 'keyword' or 'semantic'."}), 400

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def root():
    return "NotesHive Combined Search API is running!"


if __name__ == "__main__":
    app.run(port=5000, debug=True)
