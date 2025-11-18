# 📝 NotesHive

**NotesHive** is a Flask-based web application for creating, managing, organizing, and searching personal notes with role-based access control. It features both keyword and AI-powered semantic search capabilities, Google Drive integration, and a beautiful, responsive UI.

---

## 🌟 Features

### Core Functionality
- **User Authentication**: Secure login system with role-based access (Student/Teacher)
- **CRUD Operations**: Create, Read, Update, and Delete notes
- **File Management**: Upload files or attach Google Drive links
- **Smart Search**: Combined keyword and semantic search using AI embeddings
- **Role-Based Access Control**:
  - **Students**: View all notes, download files, search content
  - **Teachers**: Full CRUD access, can delete any note, manage all content

### Advanced Features
- **Semantic Search**: AI-powered search using sentence transformers (finds related content by meaning)
- **Google Drive Integration**: Attach, preview, and download files from Google Drive
- **Responsive UI**: Modern, mobile-friendly design with toast notifications
- **Real-time Feedback**: Flash messages and interactive UI elements
- **Session Management**: Secure user sessions with automatic logout

---

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: MySQL
- **ORM**: SQLAlchemy, mysql-connector-python
- **AI/ML**:
  - sentence-transformers (all-MiniLM-L6-v2)
  - scikit-learn (cosine similarity)
  - pandas, numpy

### Frontend
- **HTML5** with Jinja2 templating
- **CSS3** (Custom styles with Inter font)
- **Vanilla JavaScript** (No frameworks)
- **Google Fonts**: Inter font family

### Security
- **Session-based authentication**
- **Role-based access control**
- **Password protection** (Plain text for development, can be hashed)

---

## 📁 Project Structure
```
NotesHive/
│
├── app.py
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
