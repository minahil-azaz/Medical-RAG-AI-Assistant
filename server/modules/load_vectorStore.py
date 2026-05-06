import os
import time
from pathlib import Path
from dotenv import load_dotenv
from tqdm.auto import tqdm

from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()

PINECONE_ENV = "us-east-1"
PINECONE_INDEX_NAME = "medical-assistance"
UPLOAD_DIR = "./uploaded_doc"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ✅ FIX 1: Singleton — model loaded ONCE, reused everywhere
_embed_model = None
_pinecone_index = None


def get_embed_model():
    global _embed_model
    if _embed_model is None:
        _embed_model = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embed_model


def get_pinecone_index():
    """✅ FIX 2: Lazy init — only connects when first needed, not at import time."""
    global _pinecone_index
    if _pinecone_index is not None:
        return _pinecone_index

    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    if not pinecone_api_key:
        raise ValueError("PINECONE_API_KEY environment variable is required")

    pc = Pinecone(api_key=pinecone_api_key)
    spec = ServerlessSpec(cloud="aws", region=PINECONE_ENV)
    existing_indexes = [i["name"] for i in pc.list_indexes()]

    if PINECONE_INDEX_NAME not in existing_indexes:
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=384,
            metric="dotproduct",
            spec=spec,
        )
        while not pc.describe_index(PINECONE_INDEX_NAME).status["ready"]:
            time.sleep(1)

    _pinecone_index = pc.Index(PINECONE_INDEX_NAME)
    return _pinecone_index


def load_vectorstore(upload_files):
    embed_model = get_embed_model()   # reuses singleton
    index = get_pinecone_index()      # reuses singleton

    file_paths = []
    for file in upload_files:
        save_path = Path(UPLOAD_DIR) / file.filename
        with open(save_path, "wb") as f:
            f.write(file.file.read())
        file_paths.append(str(save_path))

    all_texts, all_metadata, all_ids = [], [], []

    for file_path in file_paths:
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
        chunks = splitter.split_documents(documents)

        texts = [chunk.page_content for chunk in chunks]
        metadata = [chunk.metadata for chunk in chunks]
        ids = [f"{Path(file_path).stem}-{i}" for i in range(len(chunks))]

        all_texts.extend(texts)
        all_metadata.extend(metadata)
        all_ids.extend(ids)

    print("Embedding chunks...")
    batch_size = 32
    embeddings = []
    for i in range(0, len(all_texts), batch_size):
        batch_texts = all_texts[i : i + batch_size]
        batch_embeddings = embed_model.embed_documents(batch_texts)
        embeddings.extend(batch_embeddings)

    print("Upserting into Pinecone...")
    vectors = [
        {
            "id": all_ids[i],
            "values": embeddings[i],
            "metadata": {**all_metadata[i], "text": all_texts[i]},
        }
        for i in range(len(embeddings))
    ]

    upsert_batch_size = 50
    for i in tqdm(range(0, len(vectors), upsert_batch_size), desc="Upserting"):
        index.upsert(vectors=vectors[i : i + upsert_batch_size])

    print(f"Upload complete for {len(file_paths)} files.")

    for file_path in file_paths:
        try:
            os.remove(file_path)
        except Exception:
            pass