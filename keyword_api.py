from flask import Flask, request, jsonify
from keyword_search import search_notes_by_keyword

app = Flask(__name__)

@app.route("/api/search/keyword", methods=["GET"])
def keyword_search_api():
    query = request.args.get("query")
    user_id = request.args.get("user_id")
    top_n = request.args.get("top_n", 10)

    if user_id is not None:
        try:
            user_id = int(user_id)
        except ValueError:
            return jsonify({"error": "Invalid user_id"}), 400

    try:
        top_n = int(top_n)
    except ValueError:
        return jsonify({"error": "top_n must be an integer"}), 400

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    results = search_notes_by_keyword(query, user_id=user_id, top_n=top_n)
    return jsonify(results)


@app.route("/", methods=["GET"])
def root():
    return "NotesHive Keyword Search API is running!"

if __name__ == "__main__":
    app.run(port=5000, debug=True)
