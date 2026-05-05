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

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

PINECONE_ENV = "us-east-1"
PINECONE_INDEX_NAME = "medical-assistance"

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

UPLOAD_DIR = "./uploaded_doc"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

spec = ServerlessSpec(cloud="aws", region=PINECONE_ENV)

existing_indexes = [i["name"] for i in pc.list_indexes()]

if PINECONE_INDEX_NAME not in existing_indexes:
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=384,  # Updated for sentence-transformers model
        metric="dotproduct",
        spec=spec
    )

    while not pc.describe_index(PINECONE_INDEX_NAME).status["ready"]:
        time.sleep(1)

index = pc.Index(PINECONE_INDEX_NAME)


# -------------------------
# Load + Split + Embed + Upsert
# -------------------------
def load_vectorstore(upload_files):
    embed_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    file_paths = []

    # 1. Save uploaded files
    for file in upload_files:
        save_path = Path(UPLOAD_DIR) / file.filename

        with open(save_path, "wb") as f:
            f.write(file.file.read())

        file_paths.append(str(save_path))

    # 2. Process PDFs
    all_texts = []
    all_metadata = []
    all_ids = []

    for file_path in file_paths:
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100
        )

        chunks = splitter.split_documents(documents)

        texts = [chunk.page_content for chunk in chunks]
        metadata = [chunk.metadata for chunk in chunks]

        ids = [
            f"{Path(file_path).stem}-{i}"
            for i in range(len(chunks))
        ]

        all_texts.extend(texts)
        all_metadata.extend(metadata)
        all_ids.extend(ids)

    # 3. Embeddings
    print("Embedding chunks...")
    embeddings = embed_model.embed_documents(all_texts)

    # 4. Upsert to Pinecone
    print("Upserting into Pinecone...")

    vectors = []
    for i in range(len(embeddings)):
        vectors.append({
            "id": all_ids[i],
            "values": embeddings[i],
            "metadata": {
                **all_metadata[i],
                "text": all_texts[i]
            }
        })

    batch_size = 100
    for i in tqdm(range(0, len(vectors), batch_size), desc="Upserting"):
        index.upsert(vectors=vectors[i:i + batch_size])

    print(f"Upload complete for {len(file_paths)} files.")