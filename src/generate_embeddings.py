import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


CHUNKS_FILE = Path("data/chunks/policy_chunks.json")
OUTPUT_DIR = Path("data/embeddings")

EMBEDDINGS_FILE = OUTPUT_DIR / "policy_embeddings.npy"
METADATA_FILE = OUTPUT_DIR / "embedding_metadata.json"

MODEL_PATH = Path(
    "/home/nineleaps/.cache/huggingface/hub/"
    "models--sentence-transformers--all-MiniLM-L6-v2/"
    "snapshots/1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
)


def load_chunks():
    if not CHUNKS_FILE.exists():
        print(f"Error: Chunk file not found: {CHUNKS_FILE}")
        return []

    try:
        chunks = json.loads(
            CHUNKS_FILE.read_text(encoding="utf-8")
        )

        if not chunks:
            print("Error: No chunks found.")
            return []

        return chunks

    except (OSError, json.JSONDecodeError) as e:
        print(f"Error loading chunks: {e}")
        return []


def load_embedding_model():
    if not MODEL_PATH.exists():
        print(f"Error: Local model not found: {MODEL_PATH}")
        return None

    print("Loading local embedding model...")

    try:
        model = SentenceTransformer(str(MODEL_PATH))
        return model

    except Exception as e:
        print(f"Error loading embedding model: {e}")
        return None


def generate_embeddings(model, chunks):
    texts = [chunk["text"] for chunk in chunks]

    print(f"Generating embeddings for {len(texts)} chunks...")

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    return embeddings


def save_embeddings(embeddings, chunks):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    np.save(EMBEDDINGS_FILE, embeddings)

    metadata = []

    for chunk in chunks:
        metadata.append({
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "metadata": chunk["metadata"]
        })

    METADATA_FILE.write_text(
        json.dumps(metadata, indent=4),
        encoding="utf-8"
    )

    print(f"\nEmbeddings saved to: {EMBEDDINGS_FILE}")
    print(f"Metadata saved to: {METADATA_FILE}")


def main():
    chunks = load_chunks()

    if not chunks:
        return

    print(f"Total chunks loaded: {len(chunks)}")

    model = load_embedding_model()

    if model is None:
        return

    print(
        f"Embedding dimension: "
        f"{model.get_embedding_dimension()}"
    )

    embeddings = generate_embeddings(model, chunks)

    print("\nEmbedding information:")
    print(f"Number of vectors: {embeddings.shape[0]}")
    print(f"Vector dimensions: {embeddings.shape[1]}")
    print(f"Embedding data type: {embeddings.dtype}")

    save_embeddings(embeddings, chunks)

    print("\nEmbedding pipeline completed successfully.")


if __name__ == "__main__":
    main()