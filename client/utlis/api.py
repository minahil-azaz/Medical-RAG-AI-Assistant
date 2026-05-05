import importlib
import requests

config = importlib.import_module("config")
API_URL = getattr(config, "API_URL", None) or getattr(config, "APU_URL", "http://127.0.0.1:8000")


def upload_pdf(file):
    """Upload a single PDF file to the backend"""
    files = {"file": (file.name, file, "application/pdf")}
    try:
        response = requests.post(f"{API_URL}/upload_pdfs/", files=files, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def ask_question(question):
    """Send a question to the backend and get an answer"""
    try:
        response = requests.post(
            f"{API_URL}/ask/",
            data={"question": question},
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}