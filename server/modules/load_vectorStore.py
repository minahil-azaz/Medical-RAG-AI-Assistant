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

if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY environment variable is required")

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
    # Use lighter embedding model to reduce memory usage
    embed_model = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},  # Force CPU usage
        encode_kwargs={'normalize_embeddings': True}
    )

    file_paths = []

    # 1. Save uploaded files
    for file in upload_files:
        save_path = Path(UPLOAD_DIR) / file.filename

        with open(save_path, "wb") as f:
            f.write(file.file.read())

        file_paths.append(str(save_path))

    # 2. Process PDFs with smaller chunks
    all_texts = []
    all_metadata = []
    all_ids = []

    for file_path in file_paths:
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        # Smaller chunks to reduce memory usage
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,  # Reduced from 500
            chunk_overlap=50   # Reduced from 100
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

    # 3. Embeddings in smaller batches
    print("Embedding chunks...")
    batch_size = 32  # Process in smaller batches
    embeddings = []
    
    for i in range(0, len(all_texts), batch_size):
        batch_texts = all_texts[i:i + batch_size]
        batch_embeddings = embed_model.embed_documents(batch_texts)
        embeddings.extend(batch_embeddings)
        
        # Clear memory
        del batch_texts, batch_embeddings

    # 4. Upsert to Pinecone in smaller batches
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

    # Smaller batch size for upsert
    upsert_batch_size = 50  # Reduced from 100
    for i in tqdm(range(0, len(vectors), upsert_batch_size), desc="Upserting"):
        batch = vectors[i:i + upsert_batch_size]
        index.upsert(vectors=batch)
        
        # Clear memory
        del batch

    print(f"Upload complete for {len(file_paths)} files.")
    
    # Clean up uploaded files to save disk space
    for file_path in file_paths:
        try:
            os.remove(file_path)
        except:
            pass