# Medical AI Assistant - Frontend

A Streamlit-based web interface for the RAG Medical AI Assistant.

## Setup

### Prerequisites
- Python 3.8+
- pip or uv package manager

### Installation

1. Install dependencies:
```bash
cd client
pip install -r requirments.txt
# or
uv pip install -r requirments.txt
```

2. Ensure the backend server is running on `http://127.0.0.1:8000`

### Running the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Features

### 1. **📤 Upload Medical Documents**
   - Upload PDF files containing medical documents
   - Single file upload with processing confirmation
   - Real-time feedback on upload status

### 2. **🩺 Ask Questions**
   - Chat interface to ask questions about uploaded documents
   - AI-powered responses from the medical assistant
   - Source citations for answers
   - Chat history stored in session state

### 3. **📂 Chat History**
   - View all messages from your chat session
   - Download chat history as JSON
   - Clear chat history when needed

## Configuration

Edit `config.py` to change the API URL:
```python
API_URL = "http://127.0.0.1:8000"
```

## Project Structure

```
client/
├── app.py                 # Main Streamlit app
├── config.py             # Configuration (API URL)
├── requirments.txt       # Python dependencies
├── components/           # Streamlit UI components
│   ├── upload.py         # File upload component
│   ├── chatUI.py         # Chat interface component
│   └── history_download.py # History download component
└── utlis/               # Utility functions
    └── api.py           # API communication functions
```

## API Endpoints Used

- `POST /upload_pdfs/` - Upload a single PDF file
- `POST /ask/` - Ask a question about documents
