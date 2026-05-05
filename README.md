# Medical RAG AI Assistant

A retrieval-augmented generation (RAG) application for medical documents.

This repository includes:
- `server/`: FastAPI backend for PDF upload, text extraction, embedding, vector storage, and question answering.
- `client/`: Streamlit frontend for uploading PDFs and chatting with the assistant.

## Features
- Upload PDF medical documents to the backend
- Extract text from PDFs and create embeddings
- Store document vectors in a database
- Ask questions and get answers from uploaded content
- Sidebar upload UI with an `Upload to Database` button

## Requirements
- Python 3.11+
- `pip` or another Python package manager
- Backend configuration for embeddings and vector store (see server setup)

## Setup
1. Create and activate a virtual environment in the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install backend dependencies:

```bash
pip install -r server/requirments.txt
```

3. Install frontend dependencies:

```bash
pip install -r client/requirments.txt
```

## Run the backend

From the project root:

```bash
uvicorn server.main:app --reload
```

The backend should be available at `http://127.0.0.1:8000`.

## Run the frontend

From the `client/` directory:

```bash
streamlit run app.py
```

This opens the Streamlit app in your browser and connects to the backend.

## Usage
1. Start the backend server.
2. Open the Streamlit app.
3. Upload a PDF medical document using the sidebar.
4. Click `Upload to Database` to process and store the document.
5. Ask questions in the chat area and review answers sourced from the uploaded file.

## Notes
- Both backend and frontend must be running for the app to work.
- Update `client/config.py` if your backend uses a different address or port.
- Use `.gitignore` files to exclude virtual environments, caches, logs, and temporary files from version control.

## Project Structure
- `server/`: backend source code and routes
- `client/`: Streamlit frontend app and utilities

## Troubleshooting
- If uploads fail, verify the backend is running and reachable.
- If the front end cannot connect, check the backend URL in `client/config.py`.
- Ensure required environment files are present and configured correctly.
