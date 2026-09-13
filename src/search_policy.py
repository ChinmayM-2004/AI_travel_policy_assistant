import json
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer


INDEX_FILE = Path("vector_store/policy_index.faiss")
METADATA_FILE = Path("vector_store/policy_metadata.json")

MODEL_PATH = Path(
    "/home/nineleaps/.cache/huggingface/hub/"
    "models--sentence-transformers--all-MiniLM-L6-v2/"
    "snapshots/1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
)

# Minimum cosine similarity required for a result
# to be considered relevant.
SIMILARITY_THRESHOLD = 0.45


def load_vector_store():
    if not INDEX_FILE.exists():
        print(f"Error: FAISS index not found: {INDEX_FILE}")
        return None, []

    if not METADATA_FILE.exists():
        print(f"Error: Metadata not found: {METADATA_FILE}")
        return None, []

    index = faiss.read_index(str(INDEX_FILE))

    metadata = json.loads(
        METADATA_FILE.read_text(encoding="utf-8")
    )

    return index, metadata


def load_embedding_model():
    if not MODEL_PATH.exists():
        print(f"Error: Model not found: {MODEL_PATH}")
        return None

    print("Loading embedding model...")

    try:
        return SentenceTransformer(str(MODEL_PATH))

    except Exception as e:
        print(f"Error loading model: {e}")
        return None


def search_policy(query, top_k=3):
    index, metadata = load_vector_store()

    if index is None:
        return []

    model = load_embedding_model()

    if model is None:
        return []

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    )

    # Normalize query vector for cosine similarity.
    faiss.normalize_L2(query_embedding)

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for score, index_position in zip(scores[0], indices[0]):

        if index_position == -1:
            continue

        score = float(score)

        # Ignore chunks that are not sufficiently relevant.
        if score < SIMILARITY_THRESHOLD:
            continue

        result = {
            "score": score,
            "chunk_id": metadata[index_position]["chunk_id"],
            "text": metadata[index_position]["text"],
            "metadata": metadata[index_position]["metadata"]
        }

        results.append(result)

    return results


def main():
    query = input(
        "\nEnter your policy question: "
    ).strip()

    if not query:
        print("Please enter a question.")
        return

    results = search_policy(
        query,
        top_k=3
    )

    if not results:
        print(
            "\nNo sufficiently relevant policy information "
            "was found."
        )
        return

    print("\n===== TOP POLICY RESULTS =====")

    for i, result in enumerate(results, start=1):

        print(f"\nResult {i}")
        print(f"Similarity Score: {result['score']:.4f}")
        print(f"Source: {result['metadata']['source']}")
        print(f"Policy Type: {result['metadata']['policy_type']}")
        print(f"Country: {result['metadata']['country']}")
        print(f"Chunk ID: {result['chunk_id']}")
        print(f"Text:\n{result['text']}")


if __name__ == "__main__":
    main()