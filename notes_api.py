# notes_api.py
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from sqlalchemy import create_engine, text
from datetime import timedelta, datetime
import requests

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "notehive_secret_key"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)

jwt = JWTManager(app)

user = "root"
password = "Nandini.14"
host = "localhost"
database = "notehive"

engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")

@app.route("/api/addNote", methods=["POST"])
@jwt_required()
def add_note():
    try:
        data = request.get_json()
        current_user = get_jwt_identity()

        title = data.get("title")
        description = data.get("description")
        file_path = data.get("file_path")
        subject_id = data.get("subject_id")
        subject_name = data.get("subject_name")
        upload_date = data.get("upload_date")

        if not upload_date:
            upload_date = datetime.now().date().isoformat()

        if not all([title, description, file_path]):
            return jsonify({"error": "Missing required fields (title, description, file_path)"}), 400

        with engine.begin() as conn:
            if subject_id:
                subject_id = int(subject_id)
            elif subject_name:
                subject_query = text("SELECT subject_id FROM Subject WHERE subject_name = :sname")
                subject = conn.execute(subject_query, {"sname": subject_name}).fetchone()
                if subject:
                    subject_id = subject[0]
                else:
                    insert_subject = text("INSERT INTO Subject (subject_name) VALUES (:sname)")
                    result = conn.execute(insert_subject, {"sname": subject_name})
                    subject_id = result.lastrowid
            else:
                return jsonify({"error": "Either subject_id or subject_name is required"}), 400

            insert_note = text("""
                INSERT INTO Note (title, description, file_path, subject_id, uploaded_by, upload_date)
                VALUES (:title, :description, :file_path, :subject_id, :uploaded_by, :upload_date)
            """)
            conn.execute(insert_note, {
                "title": title,
                "description": description,
                "file_path": file_path,
                "subject_id": subject_id,
                "uploaded_by": current_user,
                "upload_date": upload_date
            })

        try:
            requests.post("http://127.0.0.1:5000/api/refresh_index")
        except Exception as e:
            print(" Warning: Could not refresh search index:", e)

        return jsonify({"message": "Note added successfully"}), 201

    except Exception as e:
        print("Error adding note:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/deleteNote/<int:note_id>", methods=["DELETE"])
@jwt_required()
def delete_note(note_id):
    try:
        current_user = get_jwt_identity()

        with engine.begin() as conn:
            role_query = text("SELECT role FROM User WHERE user_id = :uid")
            user_role_result = conn.execute(role_query, {"uid": current_user}).fetchone()

            if not user_role_result:
                return jsonify({"error": "User not found"}), 404

            user_role = user_role_result[0]
            if user_role != "teacher":
                return jsonify({"error": "Only teachers can delete notes"}), 403

            delete_query = text("DELETE FROM Note WHERE note_id = :note_id")
            result = conn.execute(delete_query, {"note_id": note_id})

            if result.rowcount == 0:
                return jsonify({"error": "Note not found"}), 404

        try:
            requests.post("http://127.0.0.1:5000/api/refresh_index")
        except Exception as e:
            print(" Warning: Could not refresh search index after deletion:", e)

        return jsonify({"message": "Note deleted successfully"}), 200

    except Exception as e:
        print("Error deleting note:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/getToken/<int:user_id>", methods=["GET"])
def get_token(user_id):
    token = create_access_token(identity=str(user_id))
    return jsonify({"token": token})


if __name__ == "__main__":
    app.run(port=5001, debug=True)
