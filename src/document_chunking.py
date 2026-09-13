from pathlib import Path
import json


PROCESSED_DIR = Path("data/processed")
CHUNKS_DIR = Path("data/chunks")


def chunk_text(text):
    sections = text.split("\n\n")

    chunks = []

    i = 0

    while i < len(sections):
        section = sections[i].strip()

        if section:
            if section[0].isdigit() and "." in section:
                if i + 1 < len(sections):
                    section = section + "\n\n" + sections[i + 1].strip()
                    i += 1

            chunks.append(section)

        i += 1

    return chunks


def create_chunks():
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

    metadata = json.loads(
        (PROCESSED_DIR / "metadata.json").read_text(encoding="utf-8")
    )

    all_chunks = []

    for item in metadata:
        source = item["source"]

        file_path = PROCESSED_DIR / source
        text = file_path.read_text(encoding="utf-8")

        chunks = chunk_text(text)

        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "chunk_id": f"{source}_{i}",
                "text": chunk,
                "metadata": {
                    "source": source,
                    "policy_type": item["policy_type"],
                    "country": item["country"]
                }
            })

    output_path = CHUNKS_DIR / "policy_chunks.json"

    output_path.write_text(
        json.dumps(all_chunks, indent=4),
        encoding="utf-8"
    )

    print(f"Total chunks created: {len(all_chunks)}")
    print(f"Chunks saved to: {output_path}")


if __name__ == "__main__":
    create_chunks()