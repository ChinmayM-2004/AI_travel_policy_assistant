import json
from pathlib import Path

import faiss
import numpy as np


EMBEDDINGS_FILE = Path("data/embeddings/policy_embeddings.npy")
METADATA_FILE = Path("data/embeddings/embedding_metadata.json")

VECTOR_STORE_DIR = Path("vector_store")
INDEX_FILE = VECTOR_STORE_DIR / "policy_index.faiss"
METADATA_OUTPUT_FILE = VECTOR_STORE_DIR / "policy_metadata.json"


def load_embeddings():
    if not EMBEDDINGS_FILE.exists():
        print(f"Error: Embeddings file not found: {EMBEDDINGS_FILE}")
        return None

    embeddings = np.load(EMBEDDINGS_FILE)

    if embeddings.size == 0:
        print("Error: Embeddings file is empty.")
        return None

    return embeddings


def load_metadata():
    if not METADATA_FILE.exists():
        print(f"Error: Metadata file not found: {METADATA_FILE}")
        return []

    try:
        metadata = json.loads(
            METADATA_FILE.read_text(encoding="utf-8")
        )

        return metadata

    except (OSError, json.JSONDecodeError) as e:
        print(f"Error loading metadata: {e}")
        return []


def build_faiss_index(embeddings):
    # Convert embeddings to float32 because FAISS expects float32.
    embeddings = embeddings.astype("float32")

    # Normalize vectors so inner product becomes cosine similarity.
    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]

    # IndexFlatIP uses inner product.
    # With normalized vectors, inner product = cosine similarity.
    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    return index


def save_vector_store(index, metadata):
    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(INDEX_FILE))

    METADATA_OUTPUT_FILE.write_text(
        json.dumps(metadata, indent=4),
        encoding="utf-8"
    )

    print(f"FAISS index saved to: {INDEX_FILE}")
    print(f"Vector metadata saved to: {METADATA_OUTPUT_FILE}")


def main():
    print("Loading embeddings...")

    embeddings = load_embeddings()

    if embeddings is None:
        return

    print(f"Number of vectors: {embeddings.shape[0]}")
    print(f"Vector dimensions: {embeddings.shape[1]}")

    print("\nLoading metadata...")

    metadata = load_metadata()

    if not metadata:
        return

    print(f"Metadata records: {len(metadata)}")

    if len(embeddings) != len(metadata):
        print(
            "Error: Number of embeddings does not match "
            "number of metadata records."
        )
        return

    print("\nBuilding FAISS index...")

    index = build_faiss_index(embeddings)

    print(f"FAISS index type: {type(index).__name__}")
    print(f"Vectors stored in index: {index.ntotal}")
    print(f"Index dimension: {index.d}")

    save_vector_store(index, metadata)

    print("\nVector store created successfully.")


if __name__ == "__main__":
    main()
