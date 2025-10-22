# 🧠 NotesHive
**AI-Powered Centralized Notes and Resource Management System**

---

## 🚀 Overview
**NotesHive** is an AI-integrated system designed to store, manage, and intelligently retrieve academic notes and resources.  
It leverages semantic search and embeddings-based similarity to recommend the most relevant notes to users, while maintaining scalability and modularity for future features like role-based access and plagiarism validation.

---

## 🧩 Current Modules

### 1. Database Layer
- **Files:**
  - `dblink.py` – Connects Python to the database using SQLAlchemy.
  - `noteshive_schema.sql` – Contains the database schema for tables and relationships.
  - `noteshive_values.sql` – Inserts initial data/values into the database.

### 2. Embeddings and Semantic Search
- **Files:**
  - `embeddings.py` – Generates embeddings for notes’ title and description using `SentenceTransformer`.
  - `semantic_search.py` – Performs semantic similarity search using vector-based matching.
  - `notes_with_content.csv` – Stores preprocessed notes with title and description.
  - `note_embeddings.pkl` – Stores the generated embeddings for faster retrieval.

### 3. Planned Modules
- **Role-Based Access System (Admin, Student, Contributor)** – For managing uploads and permissions.
- **Frontend Integration** – React or Flask-based interface for uploading and searching notes.
- **Plagiarism / Similarity Check** – To ensure content authenticity and originality.

---

## ⚙️ Tech Stack
- **Backend:** Python, SQLAlchemy
- **AI / ML:** SentenceTransformers (`all-MiniLM-L6-v2`)
- **Database:** MySQL / PostgreSQL
- **Data Handling:** Pandas, NumPy
- **Future Frontend:** ReactJS / Flask

---

## 🗂️ Project Structure
```
NotesHive/
│
├── dblink.py
├── embeddings.py
├── semantic_search.py
├── noteshive_schema.sql
├── noteshive_values.sql
├── notes_with_content.csv
├── note_embeddings.pkl
└── README.md
```

---

## 🔧 Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/NandiniAggarwal14/NotesHive.git
cd NotesHive
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup database
```bash
mysql -u root -p < noteshive_schema.sql
mysql -u root -p < noteshive_values.sql
```

### 4. Run embedding generation and search modules
```bash
python embeddings.py
python semantic_search.py
```

---

## 📌 Future Work
- Implement role-based access control (RBAC).
- Integrate plagiarism check for note uploads.
- Build a polished frontend for a complete end-to-end system.
