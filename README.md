# 🤖 Chat Bot Backend

A FastAPI-powered backend for an AI chatbot with **RAG (Retrieval-Augmented Generation)** support.

This backend allows users to:

- Authenticate securely with JWT
- Upload documents
- Store document metadata
- Process files into embeddings
- Store embeddings in a vector database
- Chat with uploaded documents using AI

---

## ✨ Features

### 🔐 Authentication
- User signup
- User login
- JWT access token
- JWT refresh token
- Password hashing with Argon2

---

### 📂 Document Management
- Upload documents
- Get all uploaded documents
- Delete documents
- Store metadata in database

Supported formats:
- PDF
- DOCX
- TXT

---

### 🧠 RAG Pipeline
- Document ingestion
- Text chunking
- Embedding generation
- Vector storage
- Context retrieval
- Grounded AI responses

---

### 💬 Chat System
- Ask questions based on uploaded files
- Retrieve relevant chunks from vectorstore
- Generate contextual responses

---

# 🏗 Project Structure

```text
CHAT_BOT_BACKEND/
│── apis/
│   │── models/
│   │
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── chat_routes.py
│   │   ├── document_routes.py
│   │
│   ├── services/
│   │   ├── jwt_service.py
│   │   ├── rag_service.py
│   │
│   ├── utils/
│   │   ├── exceptions.py
│   │   ├── utils.py
│
│── constants/
│   ├── paths.py
│
│── data/
│   ├── uploads/
│   ├── vectorstore/
│
│── .env
│── main.py
│── requirements.txt
│── README.md
```

---

# ⚙ Tech Stack

## Backend Framework
- FastAPI

## Database
- SQLAlchemy
- SQLite / PostgreSQL

## Authentication
- JWT
- Passlib (Argon2)

## AI / RAG
- LangChain
- Sentence Transformers
- FAISS / ChromaDB

## File Handling
- UploadFile
- Local storage

---

# 🚀 Installation

## Clone repository

```bash
git clone https://github.com/yourusername/chat_bot_backend.git
```

```bash
cd chat_bot_backend
```

---

## Create virtual environment

```bash
python -m venv venv
```

Activate:

### Windows

```bash
venv\Scripts\activate
```

### Mac/Linux

```bash
source venv/bin/activate
```

---

## Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create `.env` file:

```env
JWT_SECRET_KEY=your_secret_key
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=sqlite:///./chatbot.db
```

---

# ▶ Run Server

```bash
uvicorn main:app --reload
```

Server:

```text
http://127.0.0.1:8000
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

---

# 🔐 Authentication Flow

## Signup

```http
POST /auth/signup
```

Body:

```json
{
  "name": "Malik Shakir",
  "email": "user@example.com",
  "password": "123456"
}
```

---

## Login

```http
POST /auth/login
```

Response:

```json
{
  "access_token": "...",
  "refresh_token": "..."
}
```

---

## Refresh Token

```http
POST /auth/refresh
```

Body:

```json
{
  "refresh_token": "..."
}
```

---

# 📂 Document APIs

All document APIs require:

```http
Authorization: Bearer <access_token>
```

---

## Upload Document

```http
POST /documents/upload
```

Form-data:

```text
file: sample.pdf
```

---

## Get All Documents

```http
GET /documents
```

---

## Delete Document

```http
DELETE /documents/{id}
```

---

# 💬 Chat API

Protected route.

```http
POST /chat
```

Body:

```json
{
  "message": "Summarize my uploaded document"
}
```

Flow:

```text
User Question
     ↓
Vector Search
     ↓
Retrieve Relevant Chunks
     ↓
Send Context to LLM
     ↓
Generate Response
```

---

# 📁 Data Storage

## Uploads

Stored in:

```text
data/uploads/
```

---

## Vector Database

Stored in:

```text
data/vectorstore/
```

---

# 🔄 API Flow

```text
User Uploads File
        ↓
Save File Locally
        ↓
Extract Text
        ↓
Chunk Text
        ↓
Generate Embeddings
        ↓
Store in Vector DB
        ↓
User Asks Question
        ↓
Retrieve Context
        ↓
Generate AI Response
```

---

# 🛡 Security

- JWT Authentication
- Password hashing with Argon2
- Protected routes
- User-specific document access
- Token expiration support

---

# 📌 Future Improvements

- Multiple file support
- Cloud storage (AWS S3)
- Chat history persistence
- Multi-user vector isolation
- Streaming responses
- OCR for image PDFs

---

# 👨‍💻 Author

Developed by **Malik Shakir**

Built with FastAPI + RAG + JWT Authentication.