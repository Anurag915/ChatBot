# 🚀 Document & Multimedia Q&A ChatBot (Advanced RAG System)

A state-of-the-art **Retrieval-Augmented Generation (RAG)** platform designed to ingest, transcribe, embed, and query across diverse media types including **PDF documents, audio, and video files**. 

Equipped with a **local automated transcription engine (OpenAI Whisper)** and **HuggingFace embeddings**, this system allows users to chat with their documents and media. Answers include **timestamped citations** that enable users to jump directly to specific segments in a synchronized interactive media player!

---

## 🌟 Key Features

*   🛡️ **Secure Authentication:** Complete user registration, login, and secure session management powered by **JSON Web Tokens (JWT)** and **Bcrypt** password hashing.
*   📄 **High-Fidelity PDF Processing:** Smart text extraction using **PyMuPDF (fitz)**, optimized document parsing, and semantic text chunking.
*   🎙️ **Local Audio & Video Transcription:** Multi-format ingestion (`.mp3`, `.wav`, `.m4a`, `.aac`, `.ogg`, `.mp4`, `.mov`, `.avi`, `.mkv`, etc.) transcribed locally with high precision using the **OpenAI Whisper** model.
*   ⏱️ **Interactive Timestamped Citations:** Segments in transcribed media are preserved with precise starting and ending times. Q&A answers generate interactive citations that link directly to these timestamps.
*   📺 **Synchronized Multimedia Player:** A premium built-in React media player with seeking capabilities, letting users click on citations and jump instantly to that moment in the video or audio!
*   ⚡ **Blazing-Fast Conversational Answers:** Powered by the ultra-fast **Groq API** (e.g. Llama 3) to deliver immediate, accurate, and context-aware responses.
*   🔍 **Local Semantic Search:** Leveraging **HuggingFace Embeddings** (`all-MiniLM-L6-v2`) and **FAISS** local vector stores for highly accurate, sub-millisecond document retrieval.
*   🐳 **Containerized & Production Ready:** Configured for multi-container deployment with Docker and Docker Compose.

---

## 🛠️ Tech Stack

### Backend
*   **Core:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
*   **Database:** [MongoDB](https://www.mongodb.com/) (using asynchronous driver **Motor**)
*   **Cache:** [Redis](https://redis.io/)
*   **RAG & Embeddings:** [LangChain](https://www.langchain.com/), [FAISS (CPU)](https://github.com/facebookresearch/faiss), [Sentence-Transformers (HuggingFace)](https://huggingface.co/sentence-transformers)
*   **Speech-to-Text:** [OpenAI Whisper](https://github.com/openai/whisper)
*   **PDF Extraction:** [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/en/latest/)
*   **Security:** JWT, PyJWT, Bcrypt

### Frontend
*   **Core Framework:** [React 19](https://react.dev/) + [Vite](https://vite.dev/)
*   **Styling:** [Tailwind CSS v4](https://tailwindcss.com/)
*   **HTTP Client:** [Axios](https://axios-http.com/)

---

## 📂 Project Structure

```text
├── backend/
│   ├── app/
│   │   ├── core/               # Configuration settings & environment variables
│   │   ├── db/                 # Database initialization & MongoDB helper
│   │   ├── models/             # Pydantic schemas (auth, upload, chat, health)
│   │   ├── routes/             # FastAPI routers (auth, uploads, chat, health)
│   │   ├── services/           # Business logic (Whisper, PDF parser, FAISS RAG, Groq)
│   │   └── main.py             # FastAPI entrypoint & application setup
│   ├── tests/                  # Unit and integration tests
│   ├── Dockerfile              # Production Dockerfile
│   └── requirements.txt        # Backend dependencies
├── frontend/
│   ├── src/
│   │   ├── assets/             # Images and static assets
│   │   ├── components/         # React sub-components (Auth, ChatWindow, MediaPlayer, etc.)
│   │   ├── services/           # API integration and Axios configuration
│   │   ├── App.jsx             # Main App component
│   │   └── main.jsx            # React mounting
│   ├── package.json            # Frontend dependencies
│   └── vite.config.js          # Vite config with Tailwind CSS integration
├── docker-compose.yml          # Local multi-service orchestration
└── .gitignore                  # Git untracked and ignored files
```

---

## 🚀 Setup & Installation

### Prerequisites
*   [Node.js (v18+)](https://nodejs.org/) & [NPM](https://www.npmjs.com/)
*   [Python (3.10+)](https://www.python.org/) & [Pip](https://pip.pypa.io/)
*   [MongoDB](https://www.mongodb.com/) (Running locally or a Cloud Atlas URI)
*   [FFmpeg](https://ffmpeg.org/) (Required by Whisper for local media transcription)
*   A **Groq API Key** (Obtain one for free from the [Groq Console](https://console.groq.com/))

---

### Method 1: Local Manual Execution (Recommended for Development)

#### 1. Setup Backend
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Configure environment variables. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and fill in your details, notably:
   ```env
   GROQ_API_KEY="your_actual_groq_api_key_here"
   MONGO_URI="mongodb://localhost:27017"
   MONGO_DB_NAME="chatbot"
   ```
5. Run the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   The interactive API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

#### 2. Setup Frontend
1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the Vite development server:
   ```bash
   npm run dev
   ```
   Open your browser and navigate to [http://localhost:5173](http://localhost:5173).

---

### Method 2: Docker Compose (Automated Orchestration)

To spin up the entire stack (FastAPI Backend, React Frontend, MongoDB, and Redis) automatically:

1. Create a `.env` file in the **root** of the project directory (alongside `docker-compose.yml`) and specify your Groq API key:
   ```env
   GROQ_API_KEY=gsk_your_groq_api_key_here
   ```
2. Build and launch all services in detached mode:
   ```bash
   docker-compose up --build -d
   ```
3. Verify running containers:
   ```bash
   docker-compose ps
   ```
4. Access the applications:
   *   **Frontend:** [http://localhost:5173](http://localhost:5173)
   *   **Backend Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
5. To shut down the services:
   ```bash
   docker-compose down
   ```

---

## 🔌 API Documentation

The backend exposes several secure endpoints. For development, a fully interactive OpenAPI Swagger UI is available at `http://localhost:8000/docs`.

### 1. Authentication
*   **`POST /auth/register`** - Register a new user.
    *   *Request Body:* `{"username": "user", "password": "password"}`
    *   *Response:* `{"message": "User registered successfully"}`
*   **`POST /auth/login`** - Authenticate credentials and receive a JWT.
    *   *Request Body:* `{"username": "user", "password": "password"}`
    *   *Response:* `{"access_token": "eyJhbGciOi..."}`

### 2. File Upload & Processing
*   **`POST /upload`** - Upload and process a PDF, audio, or video file.
    *   *Headers:* `Authorization: Bearer <JWT_TOKEN>`
    *   *Request (Multipart):* `file` (binary)
    *   *Response:* `{"file_id": "uuid", "file_name": "filename.mp4", "file_type": "video", "extraction": {...}}`

### 3. Interactive Chat
*   **`POST /chat`** - Ask a question about an uploaded file using semantic search RAG.
    *   *Headers:* `Authorization: Bearer <JWT_TOKEN>`
    *   *Request Body:* `{"query": "your question", "file_id": "uuid"}`
    *   *Response:* `{"answer": "Conversational answer...", "sources": ["matching chunks..."], "timestamps": [{"start": 10.5, "end": 14.2}]}`

### 4. Media Summarization
*   **`POST /summarize`** - Generate an AI summary of the uploaded file.
    *   *Headers:* `Authorization: Bearer <JWT_TOKEN>`
    *   *Request Body:* `{"file_id": "uuid"}`
    *   *Response:* `{"summary": "Summary text..."}`

---

## 🧪 Running Tests

The backend contains a rigorous test suite using `pytest` covering units, integration, database connectivity, and RAG pipelines.

1. Ensure your virtual environment is active in the `backend/` folder.
2. Install test dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```
3. Execute the tests:
   ```bash
   pytest
   ```

---

## 🔒 Security Best Practices

*   **Secrets Management:** Never commit secrets or API keys to the repository. Always use environment variables loaded from `.env` files.
*   **CORS Configuration:** Configure `allowed_origins` in production settings to restrict browser requests to trusted origins.
*   **Media Folder:** The `uploads/` folder is designed to store user media temporarily/persistently. Ensure it is included in `.gitignore` so no large media is pushed to Git.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
