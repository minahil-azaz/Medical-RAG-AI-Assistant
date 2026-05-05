import importlib
import time
import requests

config = importlib.import_module("config")
API_URL = getattr(config, "API_URL", None) or getattr(config, "APU_URL", "http://127.0.0.1:8000")


def post_with_retry(url, data=None, files=None, timeout=120, retries=1):
    for attempt in range(retries + 1):
        try:
            if files:
                response = requests.post(url, files=files, timeout=timeout)
            else:
                response = requests.post(url, data=data, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout:
            if attempt < retries:
                time.sleep(5)
                continue
            raise


def upload_pdf(file):
    """Upload a single PDF file to the backend"""
    files = {"file": (file.name, file, "application/pdf")}
    try:
        response = post_with_retry(f"{API_URL}/upload_pdfs/", files=files, timeout=120, retries=1)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def ask_question(question):
    """Send a question to the backend and get an answer"""
    try:
        response = post_with_retry(
            f"{API_URL}/ask/",
            data={"question": question},
            timeout=120,
            retries=1
        )
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}